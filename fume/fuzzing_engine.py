import time

from generators.connect import Connect
from generators.publish import Publish
from generators.disconnect import Disconnect
from generators.register import Register

import fume.handle_network_response as hnr
import fume.requests_queue as rq

import helper_functions.print_verbosity as pv
import helper_functions.determine_protocol_version as dpv
import helper_functions.crash_logging as cl
import helper_functions.get_payload_length as gpl

import globals as g

import random
import binascii
import socket

def corpus_to_array(file):
    lines = file.readlines()
    for index, line in enumerate(lines):
        lines[index] = line.replace("\n", "")
    return lines

def handle_send_state():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", g.SOURCE_PORT))
    s.settimeout(0.05)

    g.payload = g.payload[:g.MAXIMUM_PAYLOAD_LENGTH]

    try:
        pv.verbose_print("Sending payload to the target: %s" % binascii.hexlify(g.payload))
        s.sendto(g.payload, (g.TARGET_ADDR, g.TARGET_PORT))

        rq.push(g.payload)

    except ConnectionRefusedError:
        pv.print_error("No connection was found at %s:%d" % (g.TARGET_ADDR, g.TARGET_PORT))

        rq.print_queue()
        cl.dump_request_queue()

        exit(-1)

    recv = b''
    try:
        recv = s.recv(1024)
        pv.verbose_print("Response: %s" % binascii.hexlify(recv))
    except socket.timeout:
        pv.debug_print("Timeout while waiting for response")
    except ConnectionResetError:
        pv.debug_print("Connection closed after sending the payload")
    s.close()

    hnr.handle_network_response(recv)

def handle_s2_state(mm):
    if type(g.payload) is bytearray:
        return

    if mm.model_type == 'mutation':
        g.payload = "".join(g.payload)
    else:
        g.payload = "".join([p.toString() for p in g.payload])
    g.payload = bytearray.fromhex(g.payload)

def handle_bof_state():
    if gpl.get_payload_length() >= g.MAXIMUM_PAYLOAD_LENGTH:
        return

    minlen = (1 + g.FUZZING_INTENSITY) * len(g.payload)
    maxlen = 5 * (1 + g.FUZZING_INTENSITY) * len(g.payload)
    inject_len = random.randint(round(minlen), round(maxlen))
    inject_payload = random.getrandbits(8 * inject_len).to_bytes(inject_len, 'little')

    for p in inject_payload:
        index = random.randint(0, len(g.payload))
        g.payload = g.payload[:index] + p.to_bytes(1, 'little') + g.payload[index:] 

    pv.debug_print("Fuzzed payload now (injected %d bytes): %s" % (inject_len, binascii.hexlify(g.payload)))

def handle_nonbof_state():
    if gpl.get_payload_length() >= g.MAXIMUM_PAYLOAD_LENGTH:
        return

    maxlen = len(g.payload) * g.FUZZING_INTENSITY
    inject_len = random.randint(1, max(1, round(maxlen)))
    inject_payload = random.getrandbits(8 * inject_len).to_bytes(inject_len, 'little')

    for p in inject_payload:
        index = random.randint(0, len(g.payload))
        g.payload = g.payload[:index] + p.to_bytes(1, 'little') + g.payload[index:] 

    pv.debug_print("Fuzzed payload now (injected %d bytes): %s" % (inject_len, binascii.hexlify(g.payload)))

def handle_delete_state():
    if len(g.payload) <= 2:
        return

    maxlen = len(g.payload) * g.FUZZING_INTENSITY
    delete_len = random.randint(1, max(1, round(maxlen)))

    for d in range(delete_len):
        index = random.randint(0, len(g.payload) - 1)
        g.payload = g.payload[:index] + g.payload[index + 1:]

    pv.debug_print("Fuzzed payload now (deleted %d bytes): %s" % (delete_len, binascii.hexlify(g.payload)))

def handle_mutate_state():
    maxlen = len(g.payload) * g.FUZZING_INTENSITY
    mutate_len = random.randint(1, max(1, round(maxlen)))
    mutate_payload = random.getrandbits(8 * mutate_len).to_bytes(mutate_len, 'little')

    for p in mutate_payload:
        index = random.randint(0, len(g.payload))
        g.payload = g.payload[:index] + p.to_bytes(1, 'little') + g.payload[index + 1:] 

    pv.debug_print("Fuzzed payload now (mutated %d bytes): %s" % (mutate_len, binascii.hexlify(g.payload)))

def handle_select_or_generation_state(mm, packet):
    if gpl.get_payload_length() >= g.MAXIMUM_PAYLOAD_LENGTH:
        return

    state_name = mm.current_state.name

    if mm.model_type == 'mutation':
        file = open("mqtt_corpus/" + state_name, "r")
        lines = corpus_to_array(file)
        payload = random.choice(lines)
        g.payload.append(payload)
        pv.debug_print("Added payload %s" % payload)
        pv.debug_print("Payload so far: %s" % "".join(g.payload))
    else:

        payload = packet(g.protocol_version)
        g.payload.append(payload)
        pv.debug_print("Added payload %s" % payload.toString())
        pv.debug_print("Payload so far: %s" % "".join([p.toString() for p in g.payload]))

def handle_response_log_state(mm):
    response_type_pick = random.randint(0, 1)

    if response_type_pick == 0:
        if len(g.network_response_log) > 0:
            response = random.choice(list(g.network_response_log.keys()))
            g.payload = g.network_response_log[response]

        else:
            mm.current_state = mm.state_connect
            handle_state(mm)
    else:
        if len(g.console_response_log) > 0:
            response = random.choice(list(g.console_response_log.keys()))
            g.payload = g.console_response_log[response]
        else:
            mm.current_state = mm.state_connect
            handle_state(mm)

def handle_state(mm):
    state = mm.current_state.name

    if state == 'S0':
        g.SOURCE_PORT = random.randint(49152, 65535)
        g.request_queue = []

    if state == 'S1':
        g.payload = []

#    elif state == 'RESPONSE_LOG':
#        handle_response_log_state(mm)
#
    elif state == 'CONNECT':
        handle_select_or_generation_state(mm, Connect)
#
#    elif state == 'CONNACK':
#        handle_select_or_generation_state(mm, Connack)
#
    elif state == 'PUBLISH':
        handle_select_or_generation_state(mm, Publish)
#
#    elif state == 'PUBACK':
#        handle_select_or_generation_state(mm, Puback)
#
#    elif state == 'PUBREC':
#        handle_select_or_generation_state(mm, Pubrec)
#
#    elif state == 'PUBREL':
#        handle_select_or_generation_state(mm, Pubrel)
#
#    elif state == 'PUBCOMP':
#        handle_select_or_generation_state(mm, Pubcomp)
#
#    elif state == 'SUBSCRIBE':
#        handle_select_or_generation_state(mm, Subscribe)
#
#    elif state == 'SUBACK':
#        handle_select_or_generation_state(mm, Suback)
#
#    elif state == 'UNSUBSCRIBE':
#        handle_select_or_generation_state(mm, Unsubscribe)
#
#    elif state == 'UNSUBACK':
#        handle_select_or_generation_state(mm, Unsuback)
#
#    elif state == 'PINGREQ':
#        handle_select_or_generation_state(mm, Pingreq)
#
#    elif state == 'PINGRESP':
#        handle_select_or_generation_state(mm, Pingresp)
#
    elif state == 'DISCONNECT':
        handle_select_or_generation_state(mm, Disconnect)
#
#    elif state == 'AUTH':
#        handle_select_or_generation_state(mm, Auth)

    elif state == 'S2':
        handle_s2_state(mm)

    elif state in ['S1', 'INJECT', 'Sf']:
        return

    elif state == 'BOF':
        handle_bof_state()

    elif state == 'NONBOF':
        handle_nonbof_state()

    elif state == 'DELETE':
        handle_delete_state()

    elif state == 'MUTATE':
        handle_mutate_state()

    elif state == 'SEND':
        handle_send_state()

def run_fuzzing_engine(mm):
    control = True

    while True:
        model_types = ['mutation', 'generation']
        mm.model_type = random.choices(model_types, weights=[g.CHOOSE_MUTATION, 1 - g.CHOOSE_MUTATION])[0]
        pv.verbose_print("Selected model type %s" % mm.model_type)

        if mm.model_type == 'mutation':
            mm.state_s0.next = [mm.state_response_log, mm.state_connect]
            mm.state_s0.next_prob = [g.b, 1 - g.b]
        else:
            mm.state_s0.next = [mm.state_connect]
            mm.state_s0.next_prob = [1]

        mm.current_state = mm.state_s0

        while mm.current_state.name != 'Sf':
            pv.verbose_print("In state %s" % mm.current_state.name)
            handle_state(mm)
            mm.next_state()
        
        time.sleep(5)
        control = False