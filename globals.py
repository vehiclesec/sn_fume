
X1 = 0.5
X2 = 0.5
X3 = 1
b = 0.5
c = [1/4] * 4
d = [1/3, 1/3, 1/3, 1/8]

TARGET_ADDR = "0.0.0.0"
TARGET_PORT = 1884

SOURCE_PORT = 0

CHOOSE_MUTATION = 0
PACKET_SELECTION_UNIFORM_DISTRIBUTION = 1
FUZZING_STATE_UNIFORM_DISTRIBUTION = 1

FUZZING_INTENSITY = 0.1
CONSTRUCTION_INTENSITY = 3

START_COMMAND = "docker-compose up"
TARGET_START_TIME = 0.5

user_supplied_X = [0, 0, 0]

VERBOSITY = 3

payload = []

protocol_version = 1

network_response_log = {}
console_response_log = {}

SIMILARITY_THRESHOLD = 0.3

request_queue = []
REQUEST_QUEUE_SIZE = 5

TRIAGE_FAST = 1
TRIAGE_MAX_DEPTH = 3

import os
CRASH_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
CRASH_FILENAME_PREFIX = "emqx"

MAXIMUM_PAYLOAD_LENGTH = 10000