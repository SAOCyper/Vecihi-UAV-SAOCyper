import cv2
import zmq
import base64
import numpy as np
from threading import Thread
import time
import joystick



def kamera():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://192.168.137.19:5555')
    socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
    while True:
        try:
            frame = socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.frombuffer(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            cv2.imshow("image", source)
            cv2.waitKey(1)
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            break

def kamera_2():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://192.168.137.19:5554')
    socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
    while True:
        try:
            frame = socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.frombuffer(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            cv2.imshow("image2", source)
            cv2.waitKey(1)
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            break

        

def mesaj_al():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://192.168.137.19:5557')
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        mesaj = socket.recv_pyobj()
        print(f"Raspiden gelen mesaj: {mesaj}")
        



def mesaj_gonder():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://192.168.137.1:5556")
    while True:
        socket.send_pyobj(joystick.kumanda_data)
        print(joystick.kumanda_data)
            


def threadolustur():
    #threadlist = [kamera_2]
    threadlist = [kamera, mesaj_gonder,joystick.kumanda]
    for i in threadlist:
        yield Thread(target=i)

if __name__ == '__main__':
    for i in threadolustur():
        i.deamon = True
        i.start()