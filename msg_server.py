import sys
import socket
import threading
import json
import datetime
import os
import time
import pytz
from http import HTTPStatus

# Constants
HOST = ''
BUFFER_SIZE = 1024*1024
DATA_DIR = 'db'
SERVER_NAME = 'Message Board Server'

MIMETYPES = {
    "text/plain": ".txt",
    "image/jpeg": ".jpg",
    "application/json": ".json"
}

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Helper function to get the current time in the correct format
def current_time():
    lastUpdatedPattern = "%a, %d %b %Y %H:%M:%S %Z"
    modifiedTimestamp = os.path.getmtime("msg_server.py")
    # hardcoding Winnipeg for simplicity
    modifiedTime = datetime.datetime.fromtimestamp(modifiedTimestamp, tz=pytz.timezone("America/Winnipeg"))
    forHeader = modifiedTime.strftime(lastUpdatedPattern)
    return forHeader

# Function to handle client connections
def handle_client(client_socket):
    try:
        request = client_socket.recv(BUFFER_SIZE).decode('ISO-8859-1')
        method, path, protocol = parse_request(request)
        
        if method == 'GET':
            handle_get(client_socket, path)
        elif method == 'POST':
            handle_post(client_socket, path, request)
        else:
            # Respond with Method Not Allowed for unsupported methods
            send_response(client_socket, HTTPStatus.METHOD_NOT_ALLOWED, 'text/plain', 'Method Not Allowed')

    except Exception as e:
        # Respond with Internal Server Error for any other exceptions
        send_response(client_socket, HTTPStatus.INTERNAL_SERVER_ERROR, 'text/plain', 'Internal Server Error')
    finally:
        client_socket.close()

# Function to parse the HTTP request
def parse_request(request):
    lines = request.split('\r\n')
    method, path, protocol = lines[0].split()
    return method, path, protocol

# Function to send HTTP response
def send_response(client_socket, status, content_type, content, last_modified=None):
    response = f'HTTP/1.1 {status.value} {status.phrase}\r\n'
    response += f'Server: {SERVER_NAME}\r\n'
    response += f'Content-Type: {content_type}\r\n'
    response += f'Content-Length: {len(content)}\r\n'
    response += f'Last-Modified: {last_modified or current_time()}\r\n'
    response += '\r\n'
    if content_type.startswith('image/'):
        response = response.encode() + content
    else:
        response += content
        response = response.encode()
    client_socket.sendall(response)

# Function to handle GET requests
def handle_get(client_socket, path):
    if path == '/':
        list_boards(client_socket)
    elif path.endswith('.html') or path.endswith('.json'):
        board, ext = path.split('.')[-2], path.split('.')[-1]
        list_messages(client_socket, board, ext)
    else:
        parts = path.strip('/').split('/')
        if len(parts) == 1:
            list_messages(client_socket, parts[0])
        elif len(parts) == 2 and parts[1].isdigit():
            get_message(client_socket, parts[0], int(parts[1]))
        else:
            send_response(client_socket, HTTPStatus.NOT_FOUND, 'text/plain', 'Not Found')

# Function to handle POST requests
def handle_post(client_socket, path, request):
    parts = path.strip('/').split('/')
    if len(parts) == 1:
        board = parts[0]
        if not os.path.exists(os.path.join(DATA_DIR, board)):
            os.makedirs(os.path.join(DATA_DIR, board))
        index = len(os.listdir(os.path.join(DATA_DIR, board)))
        
        # Parse headers from the request
        headers, body = request.split('\r\n\r\n', 1)
        headers = headers.split('\r\n')
        content_type = None
        for header in headers:
            if header.startswith('Content-Type:'):
                content_type = header.split(': ')[1]
                break
        
        if content_type.startswith('image/'):
            # Handle image data
            image_data = body.encode('ISO-8859-1')
            print(image_data)

            # Write image data to file
            with open(os.path.join(DATA_DIR, board, f'{index}.jpg'), 'wb') as f:
                f.write(image_data)
            send_response(client_socket, HTTPStatus.OK, 'text/plain', str(index), last_modified=current_time())
        else:
            # Write content to file (for other types of content)
            with open(os.path.join(DATA_DIR, board, f'{index}{MIMETYPES[content_type]}'), 'w') as f:
                f.write(body)
            send_response(client_socket, HTTPStatus.OK, content_type, str(index), last_modified=current_time())
    else:
        send_response(client_socket, HTTPStatus.NOT_FOUND, 'text/plain', 'Not Found')

# Show message boards in HTML
def list_boards(client_socket):
    boards = os.listdir(DATA_DIR)
    content = '<!DOCTYPE html><html><head><title>Message Boards</title></head><body><h1>Message Boards:</h1><ul>'
    for board in boards:
        content += f'<li><a href="/{board}/">{board}</a></li>'
    content += '</ul></body></html>'
    send_response(client_socket, HTTPStatus.OK, 'text/html', content)

# Show list of messages in HTML
def list_messages(client_socket, board):
    board_path = os.path.join(DATA_DIR, board)
    if not os.path.exists(board_path):
        send_response(client_socket, HTTPStatus.NOT_FOUND, 'text/plain', 'Not Found')
        return
    messages = []
    for filename in sorted(os.listdir(board_path), key=lambda x: int(x.split('.')[0])):
        with open(os.path.join(board_path, filename), 'rb') as f:
            messages.append(f.read())
    content = '<!DOCTYPE html><html><head><title>Messages</title></head><body><h1>Messages:</h1><ul>'
    for filename in os.listdir(board_path):
        message_index = filename.split('.')[0]
        content += f'<li><a href="/{board}/{message_index}/">{filename}</a></li>'
    content += '</ul></body></html>'
    send_response(client_socket, HTTPStatus.OK, 'text/html', content)


# Function to get a single message
def get_message(client_socket, board, index):
    message_file = None
    for content_type, ext in MIMETYPES.items():
        message_file = os.path.join(DATA_DIR, board, f'{index}{ext}')
        if os.path.exists(message_file):
            break
    else:
        send_response(client_socket, HTTPStatus.NOT_FOUND, 'text/plain', 'Message file not found')
        return

    content_type = 'text/plain'
    if message_file.endswith('.txt'):
        with open(message_file, 'r') as f:
            content = f.read()
    elif message_file.endswith('.json'):
        with open(message_file, 'r') as f:
            content = json.load(f)
            content = json.dumps(content)
        content_type = 'application/json'
    elif message_file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        with open(message_file, 'rb') as f:
            content = f.read()
        content_type = 'image/jpeg'
    else:
        send_response(client_socket, HTTPStatus.UNSUPPORTED_MEDIA_TYPE, 'text/plain', 'Unsupported Media Type')
        return

    send_response(client_socket, HTTPStatus.OK, content_type, content)

# Main server function
def run_server(port, multi_threaded=False):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, port))
    server_socket.listen(5)
    print(f'Server listening on port {port}')

    while True:
        client_socket, addr = server_socket.accept()
        if multi_threaded:
            threading.Thread(target=handle_client, args=(client_socket,)).start()
        else:
            threading.Thread(target=handle_client, args=(client_socket,)).run()

if __name__ == '__main__':
    port = int(sys.argv[1])
    multi_threaded = len(sys.argv) > 2 and sys.argv[2] == '-m'
    run_server(port, multi_threaded)