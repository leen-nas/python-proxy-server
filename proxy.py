# CSC 430 - Computer Networks
# Proxy Server - main file
# Author: Lynn

import socket
import threading
import select
from cache.cache_manager import CacheManager
from logs.logger import get_logger
from blacklist import is_blocked
from whitelist import is_allowed
from config import HOST, PORT, BUFFER_SIZE

logger = get_logger()
cache = CacheManager()

def parse_request(raw_request):
    lines = raw_request.split('\r\n')
    first_line = lines[0]

    parts = first_line.split(' ')
    if len(parts) < 3:
        return None, None, None, None

    method = parts[0]
    url = parts[1]

    host = ''
    port = 80

    # CONNECT requests have a different format: CONNECT host:443 HTTP/1.1
    if method == 'CONNECT':
        if ':' in url:
            host, port = url.split(':')
            port = int(port)
        else:
            host = url
            port = 443
        return method, host, port, None

    if url.startswith('http://'):
        url_stripped = url[7:]
        host_part = url_stripped.split('/')[0]
        if ':' in host_part:
            host, port = host_part.split(':')
            port = int(port)
        else:
            host = host_part

    # remove proxy-specific headers that the target server doesn't need
    headers = ''
    for line in lines[1:]:
        if line.lower().startswith('proxy-connection'):
            continue
        headers += line + '\r\n'

    path = '/' + '/'.join(url.split('/')[3:]) if '/' in url[7:] else '/'
    clean_request = f"{method} {path} HTTP/1.0\r\nHost: {host}\r\n{headers}\r\n"

    return method, host, port, clean_request.encode()


# opens a raw tunnel between client and server for HTTPS
# we don't read or decrypt anything, just pass bytes both ways
def tunnel_data(client_socket, server_socket):
    while True:
        readable, _, _ = select.select([client_socket, server_socket], [], [], 60)
        if not readable:
            break
        for sock in readable:
            try:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    return
                if sock is client_socket:
                    server_socket.sendall(data)
                else:
                    client_socket.sendall(data)
            except:
                return


def handle_client(client_socket, client_address):
    server_socket = None
    try:
        raw_request = client_socket.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
        if not raw_request:
            return

        method, host, port, clean_request = parse_request(raw_request)

        # safely extract url from the first line of the request
        try:
            url = raw_request.split('\r\n')[0].split(' ')[1]
        except:
            url = '/'

        if not host:
            client_socket.close()
            return

        # if parsing failed and it's not HTTPS, nothing to forward
        if method != 'CONNECT' and not clean_request:
            client_socket.close()
            return

        # HTTPS tunnel - just relay bytes, no decryption
        if method == 'CONNECT':
            logger.info(f"HTTPS tunnel: {host}:{port}")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(10)
            try:
                server_socket.connect((host, port))
            except Exception as e:
                logger.error(f"Could not connect to {host}:{port} - {e}")
                client_socket.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                return
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            tunnel_data(client_socket, server_socket)
            return

        logger.info(f"Request from {client_address[0]} | {method} {host}:{port}")

        # check whitelist first
        if not is_allowed(host):
            logger.warning(f"NOT ALLOWED (whitelist): {host}")
            client_socket.sendall(
                b"HTTP/1.0 403 Forbidden\r\n\r\nBlocked by whitelist policy."
            )
            return

        # check if this site is blocked
        if is_blocked(host):
            logger.warning(f"BLOCKED: {host}")
            blocked_response = b"HTTP/1.0 403 Forbidden\r\n\r\nThis site is blocked by the proxy."
            client_socket.sendall(blocked_response)
            return

        # check if we already have this response saved in cache
        # using host+port+url as key so /index and /about are cached separately
        cached = cache.get(host + str(port) + url)
        if cached:
            logger.info(f"Cache hit: {host}")
            client_socket.sendall(cached)
            return

        # nothing in cache so forward the request to the real server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(10)
        server_socket.connect((host, port))
        server_socket.sendall(clean_request)

        # collect the full response
        response = b""
        while True:
            chunk = server_socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            response += chunk

        # save to cache for next time and send back to client
        cache.set(host + str(port) + url, response)
        client_socket.sendall(response)
        logger.info(f"Response sent to {client_address[0]} | {len(response)} bytes")

    except Exception as e:
        logger.error(f"Error: {client_address} - {e}")
    finally:
        client_socket.close()
        if server_socket:
            server_socket.close()


# starts the server and keeps listening for new clients
def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(50)

    logger.info(f"Proxy listening on {HOST}:{PORT}")
    print(f"Proxy running on port {PORT}, waiting for connections...")

    while True:
        client_socket, client_address = server.accept()
        # each client gets its own thread so multiple can connect at once
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_proxy()