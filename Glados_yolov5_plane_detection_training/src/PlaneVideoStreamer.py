import socket,struct,imutils,cv2,pickle
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 10050
socket_address = (host_ip,port)
server_socket.bind(socket_address)
server_socket.listen(5)
camera = True

def start_video_stream():
    client_socket,addr = server_socket.accept()
    if camera == True:
        vid = cv2.VideoCapture(0)
    else:
        vid = cv2.VideoCapture('videos/boat.mp4')
    
    try:
        print("CLIENT {} CONNECTED!".format(addr))
        if client_socket:
            while(vid.isOpened()):
                img,frame = vid.read()
                frame = imutils.resize(frame,width=640,height=480)
                a = pickle.dumps(frame)
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)
                cv2.imshow('Transmitting to the Cache Server...',frame)
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    client_socket.close()
    except Exception as e:
        print(f"CACHE SERVER {addr} DISCONNECTED")

while True:
    start_video_stream()