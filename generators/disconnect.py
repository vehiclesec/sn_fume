
import random
from .packet import Packet

class Disconnect(Packet):
    def __init__(self, protocol_version=None):
        super().__init__()

        self.msg_type = "18"

        self.duration = self.toBinaryData(None, 2, True)

        if random.getrandbits(1) == 1:
            self.payload = [self.msg_type, self.duration]
        else:
            self.payload = [self.msg_type]

        self.prependPayloadLength()