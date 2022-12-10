import threading
from socket import *
import argparse
import os
import sys
import tkinter as tk
import Server

class Send(threading.Thread):
    
    
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        
    def run(self):
        #listen for input and sends to the server
        
        while True:
            print('{}:  '.format(self.name), end = '')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]
            
            
            if(message.upper() == "QUIT"):
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
                break
            else:
                self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))
                
        print('\n Quitting')
        self.sock.close()
        sys.exit(0)


class Recieve(threading.Thread):
    
    #listens for messagses
    
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None
    
    def run(self):
        
        while True:
            message = self.sock.recv(1024).decode('ascii')
            
            if message:
                
                if self.messages:
                    self.messages.insert(tk.END, message)
                    
                    print('\r{}\n{}: '.format(message, self.name), end='')
                else:
                    print('\r{}\n{}: '.format(message, self.name), end='')
            else:
                print('\n No. We have lost connection to the Server.')
                print('\n Quitting')
                self.sock.close()
                os.exit(0)
                
class Client:
    
    def __init__(self,host,port):
        
        self.host = host
        self.port = port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.name = None
        self.messages = None
        
        
    def start(self):
        
        print('Attempting to connect to  {}:{}'.format(self.host, self.port))
        
        self.sock.connect((self.host, self.port))
        
        print('Connected to {}:{}'.format(self.host, self.port))
        
        print()
        
        self.name = input('Enter Username: ')
        
        print()
        
        print('Welcome {}'.format(self.name))
        
        send = Send(self.sock, self.name)
        
        recieve = Recieve(self.sock, self.name)
        
        send.start()
        recieve.start()
        
        self.sock.sendall('Server: {} has joined the chat.'.format(self.name).encode('ascii'))
        print("\r Messaging is now Ready, you may leave by typing the word 'quit' \n")
        print('{}: '.format(self.name), end = '')
        return recieve
    
    def send(self, textInput):
        
        
        message =  textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name, message))
        
        
        if message.upper() == "QUIT":
            self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
            
            print('\n Quitting')
            self.sock.close()
            sys.exit(0)
            
            
        #send messages for broadcasting
        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))
            
def main(host, port):
    #run the gui here
    
    client = Client(host, port)
    recieve = client.start()
    
    window = tk.Tk()
    window.title("Group Chat App")
    
    fromMessage = tk.Frame(master = window)
    scrollBar = tk.Scrollbar(master = fromMessage)
    messages = tk.Listbox(master = fromMessage, yscrollcommand=scrollBar.set)
    onlineList = tk.Listbox(master = fromMessage)
    onlineList.pack(side=tk.LEFT, fill = tk.Y)
    names = []
   #for name in client.name:
    names.append(client.name)
    print(names)
    i = 0
    while i < len(names):
        onlineList.insert(i, names[i])
        i += 1
    scrollBar.pack(side= tk.RIGHT, fill = tk.Y, expand = False)
    messages.pack(side= tk.LEFT, fill = tk.BOTH, expand = True)
    
    client.messages = messages
    recieve.messages = messages
    
    fromMessage.grid(row = 0, column = 0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master = fromEntry)
    
    textInput.pack(fill = tk.BOTH, expand = True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Message here.")
    btnSend = tk.Button(
        master = window, 
        text = 'Send', 
        command = lambda: client.send(textInput))
    
    fromEntry.grid(row =1, column = 0, padx = 10, sticky="ew")
    btnSend.grid(row =1, column = 1, pady = 10, sticky="ew")
    
    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)
    
    window.mainloop()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Group Chat Server")
    parser.add_argument('host', help = 'The Server listens here')
    parser.add_argument('-p',metavar = 'PORT', type=int, default = 2222, help = 'TCP port default(2222)')
    
    args = parser.parse_args()
    
    main(args.host, args.p)