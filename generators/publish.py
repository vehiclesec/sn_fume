# generators/publish.py
import random
from packet import Packet

class PublishFlags(Packet):
    def __init__(self):
        self.dup = random.getrandbits(1)
        self.qos = min(2, random.getrandbits(2))
        self.retain = random.getrandbits(1)
        # TopicIdType: 00 (Normal), 01 (Pre-defined), 10 (Short Name)
        self.topic_id_type = min(2, random.getrandbits(2))
        
        # Format: [7:Dup][6-5:QoS][4:Retain][3:Reserved][2:TopicIdType]
        res = (self.dup << 7) | (self.qos << 5) | (self.retain << 4) | self.topic_id_type
        self.payload = ["%.2x" % res]

class Publish(Packet):
    def __init__(self, protocol_version=None):
        super().__init__()
        # MQTT-SN MsgType for PUBLISH is 0x0C
        self.msg_type = "0c"
        self.flags = PublishFlags()
        
        # TopicId (2 bytes)
        self.topic_id = self.toBinaryData(None, 2, True)
        
        # Message ID (2 bytes)
        self.msg_id = self.toBinaryData(None, 2, True)
        
        # Data (Payload)
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