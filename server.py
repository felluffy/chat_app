import socket
from threading import Thread
import time
import sys
import select
import datetime

#@TODO dellocation properly
#add interface later
#encrypt and decrypt data 

class Server():
    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=500, number_of_connections_to_listen_to=30, audio_port = 501, video_port = 502) -> None:
        super().__init__()
        print(host)
        self.confirmation_text = "Connection established"
        self.MicStartText = "micstart-on-yes"
        self.MicStopText = "micstart-off-yes"
        self.VideoStartText = "videostart-on-yes"
        self.VideoStopText = "videostart-off-yes"
        self.chunksize = 1024
        self.number_of_connections_to_listen_to = number_of_connections_to_listen_to
        self.host = host
        self.port = port
        self.audio_port = audio_port
        self.video_port = video_port
        self.listofclients = []
        self.client_dict = {}
        self.p2pdict = {}
        self.ips = []
        self.thread_count = 0
        self.MaxDgram = 2 ** 16 

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_UDP_Aud = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock_UDP_Aud.bind((self.host, self.audio_port))
            self.sock_UDP_Vid = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #to send video stream
            self.sock_UDP_Vid.bind((self.host, self.video_port))
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.number_of_connections_to_listen_to)
            print(self.sock.getsockname()) #+ " waiting for new connections")
            print(self.sock_UDP_Aud.getsockname())
            print(self.sock_UDP_Vid.getsockname())
        except socket.error as e:
            print(e)
            sys.exit()
        Thread(target=self.listenForIncomingConnections, args=(), daemon=True).start()
        Thread(target=self.listenForVideoConnections, args=(), daemon=True).start()
        

    def listenForIncomingConnections(self): #should be a seperate thread and another for quitting the server
        try:
            i = 0
            while True:
                Client, address = self.sock.accept()
                self.listofclients.append(Client)
                i += 1
                Client.send(str.encode("Waiting on your partner to connect %d" %(i)))
                print("sent confirmation to", address)
                Client.settimeout(600)
                
                #should be threaded
                while True:
                    #get the ip address to connect to
                    toConnectTo = Client.recv(self.chunksize)
                    toConnectTo = toConnectTo.decode('utf-8')
                    print(toConnectTo)
                    #print(self.checkIpv4Adress(toConnectTo))
                    if(self.checkIpv4Adress(toConnectTo) == False and toConnectTo != 'random'):
                        print("not valid")
                        Client.send(str.encode("Enter a valid address"))
                        
                    else:
                        break
                #check if two connection people are mathced
                #then start thread betwween the two to setup comms
                #then set up cv as well
                #and ftp
                
                
                found = False
                clientToConnectTo = None
                #@TODO validate open connections only
                if len(self.client_dict) > 0:
                    for item in self.client_dict.keys():
                        if(toConnectTo == item[0]):
                            self.p2pdict[item[0]] = toConnectTo
                            self.p2pdict[toConnectTo] = item[0]
                            found = True
                            print("Found")
                            clientToConnectTo = self.client_dict[item]
                            break
                self.listofclients.append(Client)
                self.client_dict[address] = Client
                
                if found is True:
                    #for chat
                    #send - rec
                    Client.sendall(str.encode(self.confirmation_text))
                    clientToConnectTo.sendall(str.encode(self.confirmation_text))
                    Thread(target=self.ThreadedClientConnections, args=(clientToConnectTo, Client), daemon=True).start()
                    # #rec - send
                    Thread(target=self.ThreadedClientConnections, args=(Client, clientToConnectTo), daemon=True).start()
                    
                    # Thread(target=self.ThreadedUDPConnections, args=(clientToConnectTo, Client), daemon=True).start()
                    # # #rec - send
                    # Thread(target=self.ThreadedUDPConnections, args=(Client, clientToConnectTo), daemon=True).start()

                    #Thread(target=self.ThreadedClientConnections, args=(clientToConnectTo, Client), daemon=True).start()
                    # #rec - send
                    #Thread(target=self.ThreadedClientConnections, args=(Client, clientToConnectTo), daemon=True).start()




                self.thread_count += 1
                print('Thread Number: ' + str(self.thread_count))    
                # last = Client
                # last.send(str.encode("dingbat"))
                
        finally: 
            self.close_server()
        
        ServerSideSocket.close()

    def listenForVideoConnections(self):
        while True:
            buff, addr = self.sock_UDP_Vid.recvfrom(self.MaxDgram)
            if addr[1] == '6060':
                self.sock_UDP_Vid.sendto(buff, (addr[0], 6070))
            else:
                self.sock_UDP_Vid.sendto(buff, (addr[0], 6060))
            print(addr)#, ' ------- ', self.p2pdict[0])
            

        pass

    def close_server(self):
        if self.sock is not None:
            self.sock.close()

    def ThreadedClientConnections(self, Conn_A, Conn_B):
        #@TODO in chunks
        while True:
            data = "from %s %s" % (str(Conn_A.getsockname()), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            rec = Conn_A.recv(self.chunksize)
            #store or do whatever with data
            data = data + rec.decode('utf-8')
            #print(data)
            Conn_B.send(str.encode(data))

    def ThreadedUDPConnections(self, Conn_A, Conn_B):
        while True:
            rec = Conn_A.recv(self.chunksize)
            Conn_B.sendAll(rec)

    
    def isIPv4(self, s):
         try: return str(int(s)) == s and 0 <= int(s) <= 255
         except: return False
         
    def checkIpv4Adress(self, ip):
        if ip.count(".") == 3 and all(self.isIPv4(i) for i in ip.split(".")):
            return True
        else:
            return False


    def broadcasttoallactiveconnections(self, message = "announcement"):
        data = "Server: %s %s" % (str(message), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        for item in self.client_dict.keys():
            try:
                self.client_dict[item].send(data)
            except:
                print(self.client_dict[item], "has disconnected")

    def client_chat_thread(self, conn, addr):
        pass

    def recfrom(self, conn_a, conn_b):
        pass

    def closeConnection(self, conn_to_close):
        self.thread_count -= 1
        pass

    def decrypt(self, data):
        pass

    def encrpyt(self, data):
        pass

    def removeClients(clientToRemove = None):
        pass



# class ClientThread(threading.Thread):
#     pass
if len(sys.argv) > 1 and len(sys.argv) != 3:
    print("input format - server ip=ipval port=port_val")
else:
    pass

ser = Server(socket.gethostname())
time.sleep(3600) #keep open for 60 seconds
#seconds = time.time()
# while time.time() <= seconds + 10:
#     pass

    #print(seconds + 2 - time.time())
#sys.exit()
