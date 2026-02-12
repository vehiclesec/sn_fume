from parsers.parse_initializer import ParseInitializer

def determine_protocol_version(packet):
    if len(packet) == 0:
        return

    for version in range(3, 6):
        try:
            index = 0
            while index < len(packet):
                try:
                    parser = ParseInitializer(packet[index:], version)
                    index +=  2 * (parser.parser.remainingLengthToInteger()) + 2 + len(parser.parser.remaining_length)

                except ValueError:
                    index += 2
            return version
        except KeyError:
            continue