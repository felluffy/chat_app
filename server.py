import socket
from threading import Thread
import time
import sys
import select
import datetime

#@TODO dellocation properly
#add interface later

class Server():
    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=500, number_of_connections_to_listen_to=10000) -> None:
        super().__init__()
        print(host)
        self.number_of_connections_to_listen_to =number_of_connections_to_listen_to
        self.host = host
        self.port = port
        self.listofclients = []
        self.client_dict = {}
        self.p2pdict = []
        self.ips = []
        self.thread_count = 0

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.sock_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #to send video stream
            # self.sock_UDP.bind((self.host, self.port))
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.number_of_connections_to_listen_to)
            # self.sock_UDP.listen(self.number_of_connections_to_listen_to)
            print(self.sock.getsockname()) #+ " waiting for new connections")
        except socket.error as e:
            print(e)
            sys.exit()
        Thread(target=self.listenForIncomingConnections, args=(), daemon=True).start()
        

    def listenForIncomingConnections(self): #should be a seperate thread and another for quitting the server
        try:
            while True:
                Client, address = self.sock.accept()
                self.listofclients.append(Client)
                Client.send(str.encode("Waiting on your partner to connect"))
                print("sent confirmation")
                
                #should be threaded
                while True:
                    #get the ip address to connect to
                    toConnectTo = Client.recv(1024)
                    toConnectTo = toConnectTo.decode('utf-8')
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
                self.listofclients.append(Client)
                self.client_dict[address] = Client
                
                found = False
                clientToConnectTo = None
                #@TODO validate open connections only
                if len(self.client_dict) > 1:
                    for item in self.client_dict.keys():
                        print(item)
                        if(toConnectTo == item[0]):
                            found = True
                            clientToConnectTo = self.client_dict[item]
                            break

                if found is True:
                    #for chat
                    #send - rec
                    Thread(target=self.ThreadedClientConnections, args=(clientToConnectTo, Client), daemon=True).start()
                    # #rec - send
                    Thread(target=self.ThreadedClientConnections, args=(Client, clientToConnectTo), daemon=True).start()

                self.thread_count += 1
                print('Thread Number: ' + str(self.thread_count))    
                
        finally: 
            self.close_server()
        
        ServerSideSocket.close()
    def close_server(self):
        if self.sock is not None:
            self.sock.close()

    def ThreadedClientConnections(self, Conn_A, Conn_B):
        #@TODO in chunks
        data = "from %s %s" % (str(Conn_A.getsockname()), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        rec = Conn_A.recv(1024)
        #store or do whatever with data
        data = data + rec.decode('utf-8')
        Conn_B.send(str.encode(data))
    
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
        pass



# class ClientThread(threading.Thread):
#     pass
if len(sys.argv) > 1 and len(sys.argv) != 3:
    print("input format - server ip=ipval port=port_val")
else:
    pass

ser = Server(socket.gethostname())
time.sleep(60) #keep open for 60 seconds
#seconds = time.time()
# while time.time() <= seconds + 10:
#     pass

    #print(seconds + 2 - time.time())
#sys.exit()
