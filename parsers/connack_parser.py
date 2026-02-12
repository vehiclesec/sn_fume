# parsers/connack_parser.py
from protocol_parser import ProtocolParser as Parser

class ConnackParser(Parser):
    def __init__(self, payload, protocol_version):
        super().__init__(payload, protocol_version)
        # Format: [Length] [0x05] [ReturnCode]
        self.index = self.insertByteNoIdentifier("return code", payload, self.index, True)