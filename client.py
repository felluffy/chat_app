import socket
from threading import Thread
from mic import *
import traceback
import logging

class Client:
    def __init__(self, sever_addr=socket.gethostname(), server_port=500) -> None:
        super().__init__()
        self.confirmation_text = "Connection established"
        self.chunk_size = 1024 #to use in retreiveing bits
        self.server_addr = sever_addr
        self.server_port = server_port
        self.number_of_connections_to_listen_to = 10
        self.threads = []
        self.ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mic = MicInput()
        
        self.ClientSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.set_server_addr(sever_addr, server_port, True)
        
        
        
            
    def set_server_addr(self, sever_addr=socket.gethostname(), server_port=500, init = False):
        try: 

            self.tryConnect(600)
            self.server_port=server_port
            self.server_addr=sever_addr
            
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
        self.ClientSocketUDP.connect((self.server_addr, self.server_port))
        self.ClientSocketUDP.settimeout(timeout)


    def rec_data(self, LabelToAddTo=None):
        while True:
            try:
                data = self.ClientSocket.recv(self.chunk_size)
                print(data.decode('utf-8'))

                #@TODO investigate
                #QObject::connect: Cannot queue arguments of type 'QTextCursor'
                #(Make sure 'QTextCursor' is registered using qRegisterMetaType().)
                if LabelToAddTo is not None:
                    LabelToAddTo.append(data.decode('utf-8'))
            except Exception as e:
                logging.error(traceback.format_exc())

    def send_data_tcp(self, data, LabelToAddTo=None):
        try:
            to_Send = str.encode(data)
            self.ClientSocket.send(to_Send)
            data = "You :" + data
            if LabelToAddTo is not None:
                LabelToAddTo.append(data)
        except Exception as e:
            logging.error(traceback.format_exc())
    
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