import globals as g

def get_payload_length():
    if len(g.payload) == 0:
        return 0

    if type(g.payload) == bytearray:
        return len(g.payload)

    length = 0

    for p in g.payload:
        if type(g.payload[0]) == str:
            length += len(p)
        else:
            length += len(p.toString())

    return length / 2