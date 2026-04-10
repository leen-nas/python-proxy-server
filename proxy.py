# CSC 430 - Computer Networks
# Proxy Server - main file
# Author: Lynn

import socket
import threading
from cache.cache_manager import CacheManager
from logs.logger import get_logger
from blacklist import is_blocked
from config import HOST, PORT, BUFFER_SIZE

logger = get_logger()
cache = CacheManager()

# this function reads the raw HTTP request and pulls out
# the important stuff like the host, port, and method
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


# handles one client connection ,  receives request, checks cache,
# forwards to server if needed, sends response back
def handle_client(client_socket, client_address):
    server_socket = None
    try:
        raw_request = client_socket.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
        if not raw_request:
            return

        method, host, port, clean_request = parse_request(raw_request)
        if not host:
            client_socket.close()
            return

        logger.info(f"Request from {client_address[0]} | {method} {host}:{port}")

        # check if this site is blocked
        if is_blocked(host):
            logger.warning(f"BLOCKED: {host}")
            blocked_response = b"HTTP/1.0 403 Forbidden\r\n\r\nThis site is blocked by the proxy."
            client_socket.sendall(blocked_response)
            return

        # check if we already have this response saved in cache
        cached = cache.get(host + str(port))
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
        cache.set(host + str(port), response)