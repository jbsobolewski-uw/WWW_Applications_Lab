# server.py
import os
import socket
from concurrent.futures import ThreadPoolExecutor

# Server host configuration
PORT = 8000
HOST = 'localhost'
THREAD_POOL = ThreadPoolExecutor(max_workers=os.process_cpu_count())

def read_file(file_path):
    # Validate file path
    good_path = os.path.normpath("." + file_path)
    if not good_path.startswith("public"):
        return "<h1>403 Resource forbidden</h1>", "403 Forbidden", "text/html"

    if good_path.endswith(".css"):
        content_type = "text/css"
    else:
        content_type = "text/html"

    try:
        # Open UTF-8 file
        with open(good_path, "r", encoding="utf-8") as f:
            return f.read(), "200 OK", content_type

    except UnicodeDecodeError:
        # Fallback for a different encoding
        try:
            with open(good_path, "r", encoding="utf-8-sig") as f:
                return f.read(), "200 OK", content_type
        except UnicodeDecodeError:
            return "<h1>500 Encoding Error</h1>", "500 Internal Server Error", content_type

    except FileNotFoundError:
        return "<h1>404 Not Found</h1>", "404 Not Found", content_type


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

    # Split body by '&', then each pair by '=',
    # return a dict like {"name": "Alice", "email": "..."}

    form_data = {}
    pairs = body.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            form_data[key] = value

    return form_data


def process_contact_form(request_data):
    form_data = parse_contact_form(request_data)
    print("Form data received:", form_data)

    # Simple response for form submission
    content = f"""
            <title>Message received</title>
            <h1>Thank you, {form_data["name"]}!</h1>
            <p>Your message has been received.</p>
            <ul>
            """
    content += "</ul><a href='/public/index.html'>Back</a>"
    return content, "200 OK", "text/html"


def generate_response(content, status_code="200 OK", content_type="text/html"):
    header = f"HTTP/1.1 {status_code}\r\n"
    header += f"Content-Type: {content_type}; charset=utf-8\r\n"

    # Calculate Content-Length (It is crucial!)
    body = content.encode("utf-8")
    header += f"Content-Length: {len(body)}\r\n"

    header += "\r\n"  # The blank line

    return header.encode("utf-8") + body  # Send bytes, not strings


def handle_client(client_connection, client_address):
    # Receive raw bytes (buffer size 1024)
    request_data = client_connection.recv(1024).decode('utf-8')
    path = parse_request(request_data)

    # Check if it's a POST request to /submit
    if request_data.startswith('POST /submit') and 'Content-Length' in request_data:
        content, status, content_type = process_contact_form(request_data)
    else:
        # Send a response to the client based on their request
        content, status, content_type = read_file(path if path != "/" else "/public/index.html")

    response_data = generate_response(content, status_code=status, content_type=content_type)
    client_connection.sendall(response_data)

    # Close connection immediately (for now)
    client_connection.close()


def start_server():
    global HOST, PORT, THREAD_POOL

    # Create a socket object (IPv4, TCP)
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

        # Concurrently process client requests
        future = THREAD_POOL.submit(handle_client, client_connection, client_address)
        try:
            future.result(timeout=10)  # Timeout in seconds
        except TimeoutError:
            print(f"Client {client_address} timeout - closing")
            client_connection.close()


if __name__ == '__main__':
    start_server()