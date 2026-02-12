# parsers/parse_initializer.py
from protocol_parser import ProtocolParser
from connack_parser import ConnackParser
from puback_parser import PubackParser
from regack_parser import RegackParser

class ParseInitializer:
    def __init__(self, payload, protocol_version):
        assert type(payload) == str
        # MQTT-SN Message Type mapping (Hex)
        packetDict = {
            '05': ConnackParser, 
            '0b': RegackParser,
            '0d': PubackParser
        }
        
        if len(payload) > 0:
            # Correctly extract the MsgType byte based on length format
            first_byte = int(payload[0:2], 16)
            msg_type = payload[6:8] if first_byte == 1 else payload[2:4]
            
            try:
                self.parser = packetDict[msg_type](payload, protocol_version)
            except KeyError:
                self.parser = ProtocolParser(payload, protocol_version)
        else:
            self.parser = None

# Update the main loop for MQTT-SN total length incrementing
if __name__ == "__main__":
    # Example MQTT-SN payload
    payload = "030500" # Length 3, Type 05 (CONNACK), ReturnCode 00
    index = 0
    while index < len(payload):
        try:
            parser = ParseInitializer(payload[index:], 1)        
            print(f"MsgType: {parser.parser.msg_type}, Fields: {parser.parser.G_fields}")
            # MQTT-SN index increment is simply 2 * total_length
            index += 2 * parser.parser.remainingLengthToInteger()
        except Exception:
            index += 2