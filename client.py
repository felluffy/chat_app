import socket
from threading import Thread
from mic import *
import struct
import traceback
import logging
import math
import zlib as zl
import numpy as np
from cv2 import imdecode

class Client:
    def __init__(self, sever_addr=socket.gethostname(), server_port=500, server_video_port=502, server_audio_port=501, parent_ = None) -> None:
        super().__init__()
        self.confirmation_text = "Connection established"
        self.MicStartText = "micstart-on-yes"
        self.MicStopText = "micstart-off-yes"
        self.VideoStartText = "videostart-on-yes"
        self.VideoStopText = "videostart-off-yes"
        self.chunk_size = 1024 #to use in retreiveing bits
        self.server_addr = sever_addr
        self.server_port = server_port
        self.server_audio_port = server_audio_port
        self.server_video_port = server_video_port
        self.number_of_connections_to_listen_to = 10
        self.ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mic = MicInput()
        self.MaxDgram = 2 ** 16 
        self.MaxDgramImg = self.MaxDgram - 64
        self.ClientSocketUDPVid = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ClientSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.set_server_addr(sever_addr, server_port, True)
        
        self.threads = []
        self.videoTr = Thread(target=self.recFrame, args=(), daemon=False)
        #self.audioTr = Thread(target=self.recAudio, args=(), daemon=False)
        self.parent = parent_
        
            
    def set_server_addr(self, sever_addr=socket.gethostname(), server_port=500, init = False):
        print('tryna connect')  
        try: 

            self.tryConnect(600)
            self.server_port=server_port
            self.server_addr=sever_addr
            self.server_audio_port = server_port + 1 #change later
            self.server_video_port = server_port + 2 #change later
            try:
                self.ClientSocketUDPVid.bind((socket.gethostname(), 6060))
            except:
                self.ClientSocketUDPVid.bind((socket.gethostname(), 6070))
            
            self.threads.clear()
            print("connected to server")
        except socket.error as e:
            print(str(e), " :error")

    def tryConnect(self, timeout=30):
        self.ClientSocket.settimeout(timeout)
        self.ClientSocket.connect((self.server_addr, self.server_port))
        #self.ClientSocket.listen(self.number_of_connections_to_listen_to)
        #self.ClientSocketUDP.listen(self.number_of_connections_to_listen_to)
        #enable for udp conns
        #self.ClientSocketUDP.connect((self.server_addr, self.server_port))
        #self.ClientSocketUDP.settimeout(timeout)

    def tryOnRequested(self, message_ = "", timeout_ = 30):
        if self.VideoStartText in message_:
            self.stopRecievingVideo()
            self.startRecievingVideo()
            return True
            #open
        if self.VideoStopText in message_:
            self.stopRecievingVideo()
            return True
            #
        if self.MicStartText in message_:
            return True

        if self.MicStopText in message_:
            return True

    def stopRecievingVideo(self):
        if self.videoTr.isAlive():
            self.videoTr.signal = False
            self.videoTr.join()

    def startRecievingVideo(self):
        q = None
        self.videoTr = Thread(target=self.recFrame, args=(q,), daemon=False)
        self.videoTr.start()



    def rec_data(self, LabelToAddTo=None):
        while True:
            try:
                data = self.ClientSocket.recv(self.chunk_size)
                message = data.decode('utf-8')
                print(message)
                if self.tryOnRequested(message_=message) == True:
                    continue
                #@TODO investigate
                #QObject::connect: Cannot queue arguments of type 'QTextCursor'
                #(Make sure 'QTextCursor' is registered using qRegisterMetaType().)
                if LabelToAddTo is not None:
                    LabelToAddTo.append(message)
            except Exception as e:
                logging.error(traceback.format_exc())

    def send_data_tcp(self, data, LabelToAddTo=None):
        try:
            to_Send = str.encode(data)
            #if self.ClientSocket.
            self.ClientSocket.send(to_Send)
            data = "You :" + data
            if LabelToAddTo is not None:
                LabelToAddTo.append(data)
        except Exception as e:
            logging.error(traceback.format_exc())


    #def rec_aud(self, )
    
    def startThreads(self, labelToAdd=None):
        self.threads.append(Thread(target=self.rec_data, args=(labelToAdd,), daemon = True))
        print(len(self.threads), " : " , type(labelToAdd))
        print("Thread starting to read")
        self.threads[0].start()
        

        #this should be started only when send is given
        # self.threads.append(Thread(target=self.send_data, args=(), daemon = True))
        # self.threads[1].start()
        
    def __del__(self):
        self.threads.clear()
        self.ClientSocket.close()
        # self.ClientSocketUDP.close()


    def toogleSound(self, toggle = True):
        if (not self.mic.enabled and toggle):
            self.mic.startMic(socket_to_listen_to=self.ClientSocketUDP)
        else:
            self.mic.stop()
        pass

    def encryptData(self, data):
        pass
    def decryptData(self, data):
        pass


    def sendFrame(self, frame):
        try:
            size = len(frame)
            segments = math.ceil(size / (self.MaxDgramImg))
            start = 0
            while segments:
                end = min(size, start + self.MaxDgramImg)
                self.ClientSocketUDPVid.sendto(struct.pack('B', segments) + frame[start:end], (self.server_addr, self.server_video_port))
                print(segments)
                end = start
                segments -= 1
        except Exception as e:
            logging.error(traceback.format_exc())
        pass

    def recFrame(self, qlabelToAddTo):
        data = b''
        while True:
            try:
                buff, addr = self.ClientSocketUDPVid.recvfrom(self.MaxDgram)
                if struct.unpack('B', buff[0:1])[0] > 1 :
                    data += buff[1:]
                else:
                    data += buff[1:]
                    decomp = zl.decompress(data)
                    img = imdecode(np.frombuffer(decomp, dtype=np.uint8), 1)
                    self.updateFrame(img)
                    data = b''
            except socket.error as e:
                print(str(e), " :error")
                if self.parent is not None:
                    self.parent.updateImageLabel(None)
                    break
        pass

    def updateFrame(self, img):
        if self.parent is not None:
            self.parent.updateImageLabel(img)

# print()
# print('Waiting for connection response')
# try:
#     ClientMultiSocket.connect((host, port))
#     print("connected")
# except socket.error as e:
#     print(str(e))

# print("kkk")
# rec = ClientMultiSocket.recv(1024)
# print(rec.decode('utf-8'))
# print("kkk")
# ClientMultiSocket.send(str.encode("169.254.66.105"))
# print("kkk")
# rec = ClientMultiSocket.recv(1024)
# print(rec.decode('utf-8'))
# print("kkk")
# rec = ClientMultiSocket.recv(1024)
# print(rec.decode('utf-8'))

# res = ClientMultiSocket.recv(1024)
# while True:
#     Input = input('Hey there: ')
#     ClientMultiSocket.send(str.encode(Input))
#     res = ClientMultiSocket.recv(1024)
#     print(res.decode('utf-8'))

# ClientMultiSocket.close()