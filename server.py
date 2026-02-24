# server.py
import socket

# Server host configuration
PORT = 8000
HOST = 'localhost'


def parse_request(request_data):
    if not request_data:
        return ""

    # Split the string into lines
    request_data = request_data.split('\n')

    # Take the first line ("GET / HTTP/1.1")
    request_data = request_data[0]

    # Split by spaces and return the middle part ("/")
    request_data = request_data.split(' ')
    path = request_data[1]

    return path


def start_server():
    # 1. Create a socket object (IPv4, TCP)
    # AF_INET = IPv4, SOCK_STREAM = TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow the port to be reused immediately (prevents "Address already in use" errors)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to 'localhost' and port 8000
    # Hint: bind() takes a tuple: ('host', port)
    server_socket.bind((HOST, PORT))

    # Start listening for connections (backlog of 5)
    server_socket.listen(5)

    print(f"Server running on http://{HOST}:{PORT} ...")

    while True:
        # Accept a new connection
        client_connection, client_address = server_socket.accept()

        print(f"Connection received!")

        # Receive raw bytes (buffer size 1024)
        request_data = client_connection.recv(1024).decode('utf-8')
        request_data = parse_request(request_data)
        print(f"--- Received Request ---\n{request_data}\n------------------------")

        # Close connection immediately (for now)
        client_connection.close()


if __name__ == '__main__':
    start_server()
