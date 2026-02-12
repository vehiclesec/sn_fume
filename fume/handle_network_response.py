from parsers.parse_initializer import ParseInitializer
import helper_functions.determine_protocol_version as hpv
import helper_functions.print_verbosity as pv
import globals as g

# Handle the network response -- log the request if 
# the response was unique.
# A response is unique if its G field has never been seen before.
def handle_network_response(recv):
    if len(recv) == 0:
        return

    # For MQTT-SN, protocol version is typically 1 (v1.2)
    if g.protocol_version == 0:
        # Note: You may need to update determine_protocol_version to handle SN
        g.protocol_version = hpv.determine_protocol_version(recv.hex())
        
    index = 0
    recv_hex = recv.hex()
    while index < len(recv_hex):
        try:
            parser = ParseInitializer(recv_hex[index:], g.protocol_version)

            if parser.parser is None:
                break

            # Log G fields (Global fields used to determine unique state discovery)
            G_fields = str(parser.parser.G_fields)
            if G_fields not in g.network_response_log.keys():
                g.network_response_log[G_fields] = g.payload
                pv.normal_print("Found new network response (%d found)" % len(g.network_response_log.keys()))

            # MQTT-SN Change: The remainingLengthToInteger() in our new ProtocolParser 
            # returns the TOTAL length of the packet. Since we are working with a 
            # hex string, we multiply by 2 to jump to the next packet.
            packet_total_len = parser.parser.remainingLengthToInteger()
            if packet_total_len == 0:
                index += 2
            else:
                index += 2 * packet_total_len

        # If the parser throws an error, skip the current byte and continue
        except (ValueError, KeyError, IndexError):
            index += 2