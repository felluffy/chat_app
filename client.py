import socket

ClientMultiSocket = socket.socket()
host = socket.gethostname()
port = 500
print()
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
    print("connected")
except socket.error as e:
    print(str(e))

print("kkk")
rec = ClientMultiSocket.recv(1024)
print(rec.decode('utf-8'))
print("kkk")
ClientMultiSocket.send(str.encode("169.254.66.105"))
print("kkk")
rec = ClientMultiSocket.recv(1024)
print(rec.decode('utf-8'))
print("kkk")
rec = ClientMultiSocket.recv(1024)
print(rec.decode('utf-8'))

# res = ClientMultiSocket.recv(1024)
# while True:
#     Input = input('Hey there: ')
#     ClientMultiSocket.send(str.encode(Input))
#     res = ClientMultiSocket.recv(1024)
#     print(res.decode('utf-8'))

ClientMultiSocket.close()