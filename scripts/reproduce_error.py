import socket

payload =  ["1b040401ca947838337a707642644b3574427a6e54546948497433", "17040c014f647031574d59704b64697a4773474d763530"]

def reproducer(payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for message in payload:
        message = bytes.fromhex(message)
        sock.sendto(message, ("127.0.0.1", 1884))
    
    sock.close()

reproducer(payload)