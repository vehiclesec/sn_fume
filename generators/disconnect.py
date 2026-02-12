# generators/disconnect.py
import random
from packet import Packet

class Disconnect(Packet):
    def __init__(self, protocol_version=None):
        super().__init__()
        # MQTT-SN MsgType for DISCONNECT is 0x18
        self.msg_type = "18"
        
        # Optional Duration (2 bytes) used by sleeping clients
        self.duration = self.toBinaryData(None, 2, True)

        # 50% chance to include duration (simulating normal vs sleeping disconnect)
        if random.getrandbits(1) == 1:
            self.payload = [self.msg_type, self.duration]
        else:
            self.payload = [self.msg_type]
        
        self.prependPayloadLength()