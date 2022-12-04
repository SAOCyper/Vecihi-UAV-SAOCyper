import pickle
import socket
import json
data  = 0
def start_client():
    global data
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    addr = (HOST, PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.connect_ex(addr)
        while True:
            s.sendall(b"200")
            data = s.recv(4096)
            if not data:
                break
            #data = json.loads(data)
            data = pickle.loads(data)
            #datarcvd = str(datarcvd)
            print(f"Received {data!r}")