
import random
from packet import Packet

class PublishFlags(Packet):
    def __init__(self):
        self.dup = random.getrandbits(1)
        self.qos = min(2, random.getrandbits(2))
        self.retain = random.getrandbits(1)

        self.topic_id_type = min(2, random.getrandbits(2))

        res = (self.dup << 7) | (self.qos << 5) | (self.retain << 4) | self.topic_id_type
        self.payload = ["%.2x" % res]

class Publish(Packet):
    def __init__(self, protocol_version=None):
        super().__init__()

        self.msg_type = "0c"
        self.flags = PublishFlags()

        self.topic_id = self.toBinaryData(None, 2, True)

        self.msg_id = self.toBinaryData(None, 2, True)

        data_len = random.randint(1, 20)
        self.data = self.toBinaryData(None, data_len, True)

        self.payload = [
            self.msg_type,
            self.flags.toList(),
            self.topic_id,
            self.msg_id,
            self.data
        ]

        self.prependPayloadLength()