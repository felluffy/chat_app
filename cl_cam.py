import cv2
import numpy as np
import socket
import sys
import pickle
import struct

cap=cv2.VideoCapture(1)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('localhost',8089))

while True:
    ret,frame=cap.read()
    # Serialize frame
    data = pickle.dumps(frame)
    print(len(data))

    # Send message length first
    message_size = struct.pack("L", len(data)) ### CHANGED

    # Then data
    clientsocket.sendall(message_size + data)