import sys
import socket
import threading
import json

SERVER_NAME = ''
HOST = ''



def _handle_connection(socket):
    print('Handling connection with: ', socket.getpeername())
    data = socket.recv(1024)
    print(data)

def initiate_server(port, isMulti):
    
    if isMulti == True:
        
        print('this is multithreaded')
    else:
        print('this is singlethreaded')

#main
if __name__=="__main__":
    if len(sys.argv) < 2:
        print('Run python3 msg_server.py <port number>\nor python3 msg_server.py <port number> -m')
        sys.exit(1)
        
    port = int(sys.argv[1])
    
    if (len(sys.argv) > 2 and sys.argv[2] == '-m'):
        #multithreaded
        initiate_server(port, isMulti=True)
    else:
        #singlethreaded
        initiate_server(port, isMulti=False)