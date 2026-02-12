# generators/register.py
import random
from packet import Packet

class Register(Packet):
    def __init__(self, protocol_version=None):
        super().__init__()
        # MQTT-SN MsgType for REGISTER is 0x0A
        self.msg_type = "0a"
        
        # TopicId (0x0000 in a request from client to gateway)
        self.topic_id = "0000"
        
        # Message ID (2 bytes)
        self.msg_id = self.toBinaryData(None, 2, True)
        
        # Topic Name (Variable length, no length prefix)
        topic_name_len = random.randint(1, 20)
        self.topic_name = self.getAlphanumHexString(topic_name_len)

        self.payload = [
            self.msg_type,
            self.topic_id,
            self.msg_id,
            self.topic_name
        ]
        
        # Always use the MQTT-SN specific length prepending
        self.prependPayloadLength()