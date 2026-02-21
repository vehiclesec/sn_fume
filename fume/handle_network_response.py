from parsers.parse_initializer import ParseInitializer
import helper_functions.determine_protocol_version as hpv
import helper_functions.print_verbosity as pv
import globals as g

def handle_network_response(recv):
    if len(recv) == 0:
        return

    if g.protocol_version == 0:
        #print("\n\nTRUE\n\n")

        g.protocol_version = hpv.determine_protocol_version(recv.hex())

    index = 0
    recv_hex = recv.hex()
    while index < len(recv_hex):
        try:
            parser = ParseInitializer(recv_hex[index:], g.protocol_version)

            if parser.parser is None:
                break

            G_fields = str(parser.parser.G_fields)
            if G_fields not in g.network_response_log.keys():
                g.network_response_log[G_fields] = g.payload
                pv.normal_print("Found new network response (%d found)" % len(g.network_response_log.keys()))

            packet_total_len = parser.parser.remainingLengthToInteger()
            if packet_total_len == 0:
                index += 2
            else:
                index += 2 * packet_total_len

        except (ValueError, KeyError, IndexError):
            index += 2