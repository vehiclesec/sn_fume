import socket
import sys
import time
import subprocess
import random
import json
import threading
from difflib import SequenceMatcher

import globals as g
import helper_functions.print_verbosity as pv
import helper_functions.parse_config_file as pcf
import fume.run_target as rt

EXPECTED_ERROR = ""
target_process = None
target_logs = []

def parse_crash_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    parts = content.split("--- Request Queue ---")
    error_part = parts[0].replace("--- Crash Triggered By Console Message ---", "").strip()
    queue_part = parts[1].strip()
    
    return error_part, json.loads(queue_part)

def check_crash_log(crash_log):
    pv.normal_print("Testing %d payloads from the request queue..." % len(crash_log))
    for i, c in enumerate(reversed(crash_log)):
        c_bytes = bytearray.fromhex(c)
        pv.verbose_print(f"Testing payload {i+1}...")
        
        status = check_input(c_bytes, sleep_time=0.5)
        if status == False:
            pv.normal_print("The console error was replicated with the following input: %s" % c)
            return c_bytes
            
    pv.print_error("The crash log does not seem to contain a payload which triggers this console error.")
    exit(-1)

def log_reader(proc):
    """Reads stdout from the target process line-by-line and appends to a global list."""
    global target_logs
    for line in iter(proc.stdout.readline, b''):
        decoded_line = line.decode('utf-8', errors='ignore').strip()
        if decoded_line:
            target_logs.append(decoded_line)

def start_target():
    global target_process, target_logs
    if target_process:
        target_process.kill()
        
    target_logs.clear()
    
    target_process = subprocess.Popen(g.START_COMMAND.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    t = threading.Thread(target=log_reader, args=(target_process,), daemon=True)
    t.start()

    pv.verbose_print("Starting target...")
    
    pv.normal_print("Waiting up to 15 seconds for EMQX to fully boot...")
    for i in range(15):
        time.sleep(1)
        if any("is running now" in line or "Start listener" in line for line in target_logs):
            pv.normal_print("Detected EMQX boot completion in logs!")
            break

    time.sleep(1)
    target_logs.clear()
    pv.verbose_print("Target started successfully and is ready for datagrams!")

def check_input(input, sleep_time=0.5):
    global target_logs, EXPECTED_ERROR
    
    time.sleep(1.0) 
    
    target_logs.clear()
    start_index = 0
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(input, (g.TARGET_ADDR, g.TARGET_PORT))
    s.close()

    max_retries = 5
    for _ in range(max_retries):
        time.sleep(sleep_time)
        new_logs = target_logs[start_index:]
        
        if EXPECTED_ERROR:
            for line in new_logs:
                similarity = SequenceMatcher(None, EXPECTED_ERROR, line).ratio()
                
                if similarity >= g.SIMILARITY_THRESHOLD or ("parse_frame_failed" in line and "unkown_message_type" in line):
                    return False

    return True

def get_header_size(payload):
    """Returns the size of the MQTT-SN header (Length + MsgType)."""
    if len(payload) == 0:
        return 0
    return 4 if payload[0] == 0x01 else 2

def update_mqttsn_length(payload):
    """Recalculates and updates the MQTT-SN length field."""
    p = bytearray(payload)
    if len(p) == 0:
        return p
        
    if p[0] == 0x01:
        if len(p) >= 3:
            p[1] = (len(p) >> 8) & 0xFF
            p[2] = len(p) & 0xFF
    else:
        p[0] = len(p)
    return p

def delete_random(input, delete_size):
    header_size = get_header_size(input)
    if len(input) <= header_size:
        return input
        
    p = bytearray(input)
    for _ in range(delete_size):
        if len(p) <= header_size:
            break
        index = random.randint(header_size, len(p) - 1)
        del p[index]
        
    return update_mqttsn_length(p)

def delete_block(input, index, delete_size):
    p = bytearray(input)
    del p[index : index + delete_size]
    return update_mqttsn_length(p)

def check_for_crash(input, candidates, local_candidates):
    crash_status = check_input(input)

    if crash_status is False:
        if not rt.check_connection():
            start_target()

        if input not in candidates:
            if g.TRIAGE_FAST:
                if len(candidates) == 0:
                    candidates.append(input)
                    pv.normal_print("Found new minimized input: %s" % input.hex())
                elif len(input) < len(candidates[0]):
                    candidates[0] = input
                    pv.normal_print("Found new minimized input: %s" % input.hex())
            else:
                candidates.append(input)
                local_candidates.append(input)
                pv.normal_print("Found new minimized input: %s" % input.hex())

    return candidates, local_candidates

def triage(input, candidates = None, triage_level = 1):
    if candidates is None:
        candidates = []

    if triage_level > g.TRIAGE_MAX_DEPTH:
        return input, []

    pv.normal_print("Triaging input %s" % input.hex())
    start_size = len(input)
    delete_size = 1
    local_candidates = []

    while delete_size < len(input):
        pv.verbose_print("Delete size is now %d" % delete_size)
        
        header_size = get_header_size(input)
        
        i = header_size

        while i + delete_size <= len(input):
            new_input = delete_block(input, i, delete_size)
            check_for_crash(new_input, candidates, local_candidates)
            i += 1

        if len(input) > header_size:
            random_iterations = round((len(input) - header_size) / delete_size)
            for j in range(random_iterations):
                new_input = delete_random(input, delete_size)
                check_for_crash(new_input, candidates, local_candidates)

        delete_size *= 2

    if g.TRIAGE_FAST:
        if len(candidates) > 0:
            new_candidate, _ = triage(candidates[0], [], triage_level + 1)
            if len(new_candidate) < len(input):
                input = new_candidate
    else:
        for candidate in local_candidates:
            new_candidate, new_locals = triage(candidate, candidates, triage_level + 1)
            if len(new_candidate) < len(input):
                input = new_candidate
            for local in new_locals:
                if local not in candidates:
                    candidates.append(local)

    end_size = len(input)
    if end_size < start_size:
        reduction = 100 * (1 - (float(end_size) / float(start_size)))
        pv.normal_print("Input size reduced by %f%% (we are %d triage levels deep)" % (reduction, triage_level))
    else:
        pv.normal_print("Input size did not change (we are %d triage levels deep)" % triage_level)

    return input, local_candidates
    
if __name__ == "__main__":
    try:
        config_f = open(sys.argv[2], 'r')
        config = config_f.readlines()
        pcf.parse_config_file(config)
        config_f.close()
    except FileNotFoundError:
        pv.print_error("Could not find the supplied config file file: %s" % sys.argv[2])
        exit(-1)
    except IndexError:
        pv.print_error("Usage: triage.py <crash log file> <config file>")
        exit(-1)

    try:
        EXPECTED_ERROR, request_queue = parse_crash_file(sys.argv[1])
    except Exception as e:
        pv.print_error("Failed to parse the supplied crash file: %s" % sys.argv[1])
        exit(-1)

    start_target()

    input = check_crash_log(request_queue)

    if g.TRIAGE_FAST:
        pv.normal_print("Using the FAST version")
    else:
        pv.normal_print("Using the SLOW version")

    run = 1
    first_start_size = len(input)
    while True:
        pv.normal_print("RUN #%d" % run)
        start_size = len(input)
        input, _ = triage(input)
        end_size = len(input)
        
        if end_size == start_size:
            print("Input size did not change.")
            break
        else:
            reduction = 100 * (1 - (float(end_size) / float(start_size)))
            print("New input: %s\nReduced by %f%%" % (input.hex(), reduction))
            run += 1

    reduction = 100 * (1 - (float(end_size) / float(first_start_size)))
    print("FINAL INPUT: %s\nReduced by %f%%" % (input.hex(), reduction))