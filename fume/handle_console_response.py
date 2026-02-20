import globals as g
from difflib import SequenceMatcher
import helper_functions.print_verbosity as pv
import helper_functions.crash_logging as cl

def check_similarity(line):
    for response in g.console_response_log:
        similarity = SequenceMatcher(None, line, response).ratio()

        if similarity >= g.SIMILARITY_THRESHOLD:
            return True
    return False

def handle_console_response(proc):
    for line in iter(proc.stdout.readline, b''):

        decoded_line = line.decode('utf-8', errors='ignore').lower()
        
        if "error" in decoded_line:
            pv.normal_print(f"Keyword 'error' detected in console message: {decoded_line.strip()}")
            cl.create_crash_directory()
            cl.dump_request_queue(console_message=decoded_line)

        if line not in g.console_response_log:

            similarity = check_similarity(line)

            if similarity is False and type(g.payload) is bytearray:
                g.console_response_log[line] = g.payload
                pv.normal_print("Found new console response (%d found)" % len(g.console_response_log.keys()))