import socket,struct,imutils,cv2,pickle

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = "192.168.1.102"
port = 10049
socket_address = (host_ip,port)
client_socket.connect(socket_address)

data = b''
payload_size = struct.calcsize("Q")
while True:
    while len(data) < payload_size:
        packet = client_socket.recv(4*1024)
        if not packet : break
        data += packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q",packed_msg_size)[0]
    while len(data) < msg_size:
        data += client_socket.recv(4*1024)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    cv2.imshow('Receiving from cache server',frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
client_socket.close()