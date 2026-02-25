# server.py
import os.path
import socket
import threading

# Server host configuration
PORT = 8000
HOST = 'localhost'


def read_file(file_path):
    # Validate file path
    good_path = os.path.normpath("." + file_path)
    if not good_path.startswith("public"):
        return "<h1>403 Resource forbidden</h1>", "403 Forbidden"

    try:
        # Otwórz plik z jawnie określonym kodowaniem UTF-8
        with open(good_path, "r", encoding="utf-8") as f:
            return f.read(), "200 OK"

    except UnicodeDecodeError:
        # Fallback dla plików z innymi kodowaniami
        try:
            with open(good_path, "r", encoding="utf-8-sig") as f:
                return f.read(), "200 OK"
        except UnicodeDecodeError:
            return "<h1>500 Encoding Error</h1>", "500 Internal Server Error"

    except FileNotFoundError:
        return "<h1>404 Not Found</h1>", "404 Not Found"


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


def parse_contact_form(request_data):
    # The body is separated from headers by a blank line
    parts = request_data.split("\r\n\r\n", 1)
    if len(parts) < 2:
        return {}
    body = parts[1]
    # TODO: Split body by '&', then each pair by '=',
    # return a dict like {"name": "Alice", "email": "..."}
    return {}


def generate_response(content, status_code="200 OK"):
    header = f"HTTP/1.1 {status_code}\r\n"
    header += "Content-Type: text/html; charset=utf-8\r\n"

    # Calculate Content-Length (It is crucial!)
    body = content.encode("utf-8")
    header += f"Content-Length: {len(body)}\r\n"

    header += "\r\n"  # The blank line

    return header.encode("utf-8") + body  # Send bytes, not strings


def handle_client(client_connection, client_address):
    # Receive raw bytes (buffer size 1024)
    request_data = client_connection.recv(1024).decode('utf-8')
    path = parse_request(request_data)

    # Send a response to the client based on their request
    content, status = read_file(path if path != "/" else "/public/index.html")
    response_data = generate_response(content, status)
    client_connection.sendall(response_data)

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