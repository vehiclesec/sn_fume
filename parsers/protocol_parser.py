# parsers/protocol_parser.py

class ProtocolParser:
    # Helper methods remain the same as they use self.index
    def insertByteNoIdentifier(self, fieldName, payload, index, use_G_field):
        return self.insertByte(fieldName, payload, index - 2, use_G_field)

    def insertByte(self, fieldName, payload, index, use_G_field):
        value = self.indexToByte(index + 2, 1, payload)
        if use_G_field:
            self.G_fields[fieldName] = value
        else:
            self.H_fields[fieldName] = value
        return index + 4

    def insertTwoBytesNoIdentifier(self, fieldName, payload, index, use_G_field):
        return self.insertTwoBytes(fieldName, payload, index - 2, use_G_field)

    def insertTwoBytes(self, fieldName, payload, index, use_G_field):
        value = self.indexToByte(index + 2, 2, payload)
        if use_G_field:
            self.G_fields[fieldName] = value
        else:
            self.H_fields[fieldName] = value
        return index + 6

    def indexToByte(self, index = None, numBytes = 1, payload = None):
        if index is None: index = self.index
        if payload is None: payload = self.payload
        return payload[index:index+(numBytes * 2)]

    def remainingLengthToInteger(self):
        # In MQTT-SN, the length field includes itself. 
        # We return the total length in bytes.
        return int(self.length_value, 16)

    def __init__(self, payload, protocol_version):
        self.payload = payload
        self.protocol_version = protocol_version
        self.G_fields = {}
        self.H_fields = {}
        
        # MQTT-SN Length Parsing
        first_byte = int(self.indexToByte(0, 1), 16)
        if first_byte == 1:
            # 3-byte length: 0x01 followed by 2-byte length
            self.length_value = self.indexToByte(2, 2)
            self.msg_type = self.indexToByte(6, 1)
            self.index = 8 
        else:
            # 1-byte length
            self.length_value = self.indexToByte(0, 1)
            self.msg_type = self.indexToByte(2, 1)
            self.index = 4

        self.G_fields["msg_type"] = self.msg_type