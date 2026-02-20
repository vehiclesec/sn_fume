
import random
from .packet import Packet

class Register(Packet):
    def __init__(self, protocol_version=None):
        super().__init__()

        self.msg_type = "0a"

        self.topic_id = "0000"

        self.msg_id = self.toBinaryData(None, 2, True)

        topic_name_len = random.randint(1, 20)
        self.topic_name = self.getAlphanumHexString(topic_name_len)

        self.payload = [
            self.msg_type,
            self.topic_id,
            self.msg_id,
            self.topic_name
        ]

        self.prependPayloadLength()