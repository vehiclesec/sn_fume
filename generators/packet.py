import socket
import string
import random
import math
import time

class Packet:
    def __init__(self):
        self.payload = []

    def toList(self):
        l = []

        for p in self.payload:
            for n in p:
                if type(n) == list:
                    for x in n:
                        l.append(x)
                else:
                    l.append(n)

        return l

    def toString(self):
        return "".join(self.toList())

    def getByteLength(self):
        lenFloat = len(self.toString()) / 2
        assert math.ceil(lenFloat) == math.floor(lenFloat)
        return int(lenFloat)

    def toVariableByte(self, byteString):
        varByte = ""
        byteInt = int(byteString, 16)
        while True:
            encoded = int(byteInt % 128)
            byteInt = int(byteInt / 128)
            if byteInt > 0:
                encoded = encoded | 128

            varByte += "%.2x" % encoded
            if byteInt <= 0:
                break

        return varByte

    def prependPayloadLength(self):
        total_len = self.getByteLength()
        if total_len < 255:

            payload_length = "%.2x" % (total_len + 1)
        else:

            payload_length = "01%.4x" % (total_len + 3)

        self.payload.insert(0, payload_length)

    def getAlphanumHexString(self, stringLength, userstring = None):
        if userstring is not None:
            return ["%.2x" % ord(s) for s in userstring]

        alphanum = string.ascii_letters + string.digits
        return ["%.2x" % ord(random.choice(alphanum)) for i in range(stringLength)]

    def toEncodedString(self, identifier, stringLength, userstring = None):
        if userstring is None:
            userstring = self.getAlphanumHexString(stringLength)
        else:
            userstring = self.getAlphanumHexString(stringLength, userstring)
        if identifier is None:
            return ["%.4x" % len(userstring), userstring]
        return ["%.2x" % identifier, "%.4x" % len(userstring), userstring]

    def toEncodedStringPair(self, identifier, string1Length, string2Length):
        return ["%.2x" % identifier, "%.4x" % string1Length, self.getAlphanumHexString(string1Length), "%.4x" % string2Length, self.getAlphanumHexString(string2Length)]

    def toBinaryData(self, identifier, byteLength, omitLength = False, maxBits = 8, minValue = 0):

        if identifier is None:
            fullData = ["%.4x" % byteLength, ["%.2x" % max(minValue, random.getrandbits(maxBits)) for i in range(byteLength)]]
            if omitLength:
                return fullData[1]
            else:
                return fullData
        else:
            fullData = ["%.2x" % identifier, "%.4x" % byteLength, ["%.2x" % max(minValue, random.getrandbits(maxBits)) for i in range(byteLength)]]
            if omitLength:
                return [fullData[0], fullData[2]]
            else:
                return fullData

    def appendPayloadRandomly(self, newPacket):
        if random.getrandbits(1) == 0:
            self.payload.append(newPacket)

def sendToBroker(host, port, payload, silenceError = False, killOnError = True):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        if type(payload) == str:
            s.sendto(bytearray.fromhex(payload), (host, port))
        else:
            s.sendto(payload, (host, port))
    except ValueError:
        if not silenceError:
            print("ValueError caused by following payload:")
            print(payload)
        if killOnError:
            exit(0)
    except ConnectionRefusedError:
        if not silenceError:
            print("ConnectRefusedError caused by following payload:")
            print(payload)
        if killOnError:
            exit(0)
    except ConnectionResetError:
        pass
    s.close()

def packetTest(packetTypes, runs = 10, verbose = False):
    host = "127.0.0.1"
    port = 1883

    for i in range(runs):
        payload = ""
        protocol_version = random.randint(3, 5)
        for p in packetTypes:
            payload += p(protocol_version).toString()
        if verbose:
            print("Sending payload: ", payload)
        sendToBroker(host, port, payload)
        time.sleep(0.01)