import sys
import socket
import threading
import json

HOST = 'localhost'
PORT = 8000

def _handle_connection(socket):
    print('handle socket here')

def run_multithreaded():
    print('this is multithreaded')
    
def run_singlethreaded():
    print('this is singlethreaded')


#main
if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Run 'python3 msg_server.py <port>'\nor 'python3 msg_server.py <port> -m'")
        sys.exit(1)
        
    port = int(sys.argv[1])
    multithreaded = len(sys.argv) > 2 and sys.argv[2] == '-m'
    
    if multithreaded:
        #multithreaded
        run_multithreaded()
    else:
        #singlethreaded
        run_singlethreaded()