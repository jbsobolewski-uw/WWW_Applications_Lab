# server.py
import socket
import threading

# Server host configuration
PORT = 8000
HOST = 'localhost'

# Example server response HTML
EXAMPLE_CONTENT = "<h1>Hello from Python!</h1>"

# Visitor counting
VISITORS_COUNT = 0

# Lock for thread-safe visitor counting
VISITORS_LOCK = threading.Lock()


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


def generate_response(content, status_code="200 OK"):

    header = f"HTTP/1.1 {status_code}\r\n"
    header += "Content-Type: text/html\r\n"

    # Calculate Content-Length (It is crucial!)
    header += f"Content-Length: {len(content)}\r\n"

    header += "\r\n"  # The blank line
    response_str = header + content

    return response_str.encode('utf-8')  # Send bytes, not strings


def handle_client(client_connection, client_address):
    global VISITORS_COUNT

    print(f"Connection received!")

    # Receive raw bytes (buffer size 1024)
    request_data = client_connection.recv(1024).decode('utf-8')
    request_data = parse_request(request_data)
    print(f"--- Received Request ---\n{request_data}\n------------------------")

    # Send a response to the client based on their request
    # response = generate_response(EXAMPLE_CONTENT)

    if '/' == request_data:
        # Thread-safe increment - Lock is crucial here!
        with VISITORS_LOCK:
            VISITORS_COUNT += 1
            current_count = VISITORS_COUNT

        response = generate_response(
            f"<h1>Visitors</h1><p>This page has been visited {current_count} times</p>"
        )

    elif '/favicon.ico' == request_data:
        response = generate_response(
            "<h1>Visitors</h1><p>favicon.ico not found</p>",
            "404 Not Found"
        )

    else:
        response = generate_response(
            "<h1>Visitors</h1><p>404</p>",
            "404 Not Found"
        )

    client_connection.sendall(response)

    # Close connection immediately (for now)
    client_connection.close()


def start_server():
    global HOST, PORT

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

        # Create a new thread for each client
        client_thread = threading.Thread(
            target=handle_client,
            args=(client_connection, client_address)
        )

        # Daemon thread (optional: closes with main program)
        client_thread.daemon = True
        client_thread.start()


if __name__ == '__main__':
    start_server()