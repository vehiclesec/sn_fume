import globals as g
import os
import datetime

def create_crash_directory():
    dir_exists = os.path.exists(g.CRASH_DIRECTORY)

    if not dir_exists:
        os.makedirs(g.CRASH_DIRECTORY)

def dump_request_queue(console_message=None):
    if len(g.request_queue) == 0:
        return

    dt = str(datetime.datetime.now().timestamp())
    filename = g.CRASH_DIRECTORY + "/" + g.CRASH_FILENAME_PREFIX + "-" + dt + ".txt"
    f = open(filename, "w")
    if console_message:
        f.write("--- Crash Triggered By Console Message ---\n")
        f.write(console_message.strip() + "\n\n")
        f.write("--- Request Queue ---\n")
    for req in g.request_queue:
        f.write(req.hex() + "\n")
    f.close()

    print("Logged request queue to %s" % filename)