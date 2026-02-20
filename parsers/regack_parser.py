
from parsers.protocol_parser import ProtocolParser as Parser

class RegackParser(Parser):
    def __init__(self, payload, protocol_version):
        super().__init__(payload, protocol_version)

        self.index = self.insertTwoBytesNoIdentifier("topic id", payload, self.index, False)
        self.index = self.insertTwoBytesNoIdentifier("message id", payload, self.index, False)
        self.index = self.insertByteNoIdentifier("return code", payload, self.index, True)