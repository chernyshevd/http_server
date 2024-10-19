import logging
import socket
import threading
import os
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

HOST = 'localhost'
PORT = 8002
DOCUMENT_ROOT = './www'  # Root folder for static files
MAX_PACKET_SIZE = 1024

HTTP_STATUS_OK = "HTTP/1.1 200 OK\r\n"
HTTP_STATUS_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"
HTTP_STATUS_BAD_REQUEST = "HTTP/1.1 400 Bad Request\r\n"

CONTENT_TYPE_HTML = "text/html"
CONTENT_TYPE_BINARY = "application/octet-stream"

def handle_request(client_socket: socket.socket) -> None:

    """
    Handle incoming HTTP request from a client socket.

    Args:
        client_socket (socket.socket): The client socket to handle the request from.
    """

    try:
        request = client_socket.recv(MAX_PACKET_SIZE).decode()
        headers = request.split('\r\n')

        if len(headers) < 1:
            response = f"{HTTP_STATUS_BAD_REQUEST}\r\n"
            client_socket.send(response.encode())
            return

        method = headers[0].split()[0]

        if method in ['GET', 'HEAD']:
            if len(headers[0].split()) < 2:
                response = f"{HTTP_STATUS_BAD_REQUEST}\r\n"
                client_socket.send(response.encode())
                return

            filename = headers[0].split()[1]
            if filename == '/':
                filename = '/index.html'

            file_path = os.path.join(DOCUMENT_ROOT, filename.lstrip('/'))

            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    response_data = file.read()

                content_type = CONTENT_TYPE_HTML if file_path.endswith('.html') else CONTENT_TYPE_BINARY
                response_headers = f"{HTTP_STATUS_OK}Content-Type: {content_type}\r\nContent-Length: {len(response_data)}\r\n\r\n"
                client_socket.send(response_headers.encode())
                client_socket.send(response_data)
            else:
                response = f"{HTTP_STATUS_NOT_FOUND}\r\n"
                client_socket.send(response.encode())
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received, shutting down')
    except Exception as e:
        logger.critical(f'Fatal error: {e}')
    finally:
        client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    logger.info(f'Server is running on http://{HOST}:{PORT}')

    while True:
        client_socket, address = server_socket.accept()
        threading.Thread(target=handle_request, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()