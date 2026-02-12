import random
import binascii
import string

from packet import Packet
from packet import packetTest
from properties import Properties

class ConnectFlags(Packet):
    def __init__(self):        
        self.will = random.getrandbits(1)
        self.clean_session = random.getrandbits(1)

        res = (self.will << 3) | (self.clean_session << 2)
        self.payload = ["%.2x" % res]

class Connect(Packet):
    def __init__(self, protocol_version = None):
        super().__init__()

        self.msg_type = "04"
        self.flags = ConnectFlags()

        self.protocol_id = "01"

        self.duration = self.toBinaryData(None, 2, True)

        client_id_len = random.randint(1, 23)
        self.client_id = self.getAlphanumHexString(client_id_len)

        self.payload = [
            self.msg_type,
            self.flags.toList(),
            self.protocol_id,
            self.duration,
            self.client_id
        ]

        self.prependPayloadLength()

if __name__ == "__main__":
    packetTest([Connect], 10)