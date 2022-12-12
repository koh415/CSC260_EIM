import threading
from socket import *
import argparse
import sys
from cryptography.fernet import Fernet

with open("filekey.key", "rb") as file:
    key = file.read()
fernet = Fernet(key)
class ServerGC(threading.Thread):
    
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        
    def run(self):
        sock = socket(AF_INET,SOCK_STREAM)
        #allows for reuse of ports
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
        #binds the socket to ip address
        sock.bind((self.host, self.port))
        
        sock.listen(1)
        print("Listening at", sock.getsockname())
        
        while True:
            #this is where it accepts new connections
            sockConnect, sockname = sock.accept()
            print(f"getting new connection from {sockConnect.getpeername()} to {sockConnect.getsockname()}")
            
            #new thread
            serverSocket=  ServerSocket(sockConnect,sockname,self)
            
            #start thread
            serverSocket.start()
            
            #add thread to new conneciton
            self.connections.append(serverSocket)
            print("Ready to recieve messages from",sockConnect.getpeername())
            
    def broadcast(self, message, source):
        for connection in self.connections:
            
            if connection.sockname != source:
                #encrypt the message here
                connection.send(message)
                
    def removeConnection(self,connection):
        
        self.connections.remove(connection)
        
class ServerSocket(threading.Thread):
    

    def __init__(self, sockConnect, sockname, server):
        super(). __init__()
        self.sockConnect = sockConnect
        self.sockname = sockname
        self.server = server
        
    def run(self):
            
        while True:
            message = self.sockConnect.recv(1024).decode('ascii')
            message = fernet.decrypt(message)
            if message:
                print(f"{self.sockname} says {message}") 
                self.server.broadcast(message, self.sockname)
                    
            else:
                print(f"{self.sockname} has closed the connection")
                self.sockConnect.close()
                server.removeConnection(self)
                return
                
    def send(self, message):
        self.sockConnect.sendall(message.encode('ascii'))
        
    def exit(server):
        
        while True:
            inpt = input("")
            if inpt == "quit":
                print("Group Chat ending")
                for connection in server.connections:
                    connection.sockConnect.close()
                    
                print("Group Chat Closed")
                sys.exit(0)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Group Chat Server")
    parser.add_argument('host', help = 'The Server listens here')
    parser.add_argument('-p',metavar = 'PORT', type=int, default = 2222, help = 'TCP port default(2222)')
    
    args = parser.parse_args()
    
    server = ServerGC(args.host, args.p)
    server.start()
    
    exit = threading.Thread(target = exit, args = (server, ))
    exit.start()