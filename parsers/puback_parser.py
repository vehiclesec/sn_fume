# parsers/puback_parser.py
from protocol_parser import ProtocolParser as Parser

class PubackParser(Parser):
    def __init__(self, payload, protocol_version):
        super().__init__(payload, protocol_version)
        # Format: [Length] [0x0D] [TopicId(2)] [MsgId(2)] [ReturnCode(1)]
        self.index = self.insertTwoBytesNoIdentifier("topic id", payload, self.index, False)
        self.index = self.insertTwoBytesNoIdentifier("message id", payload, self.index, False)
        self.index = self.insertByteNoIdentifier("return code", payload, self.index, True)