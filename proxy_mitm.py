# CSC 430 - Computer Networks
# Bonus H - HTTPS MITM Proxy
# Author: Lynn
# this intercepts HTTPS traffic using a fake certificate per domain
# the browser trusts our CA so it accepts our fake certs

import socket
import threading
import ssl
import select
from logs.logger import get_logger
from blacklist import is_blocked
from config import HOST, BUFFER_SIZE
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime
import tempfile
import os

MITM_PORT = 8889
logger = get_logger()

# load our root CA that we generated
CA_CERT = "ca.crt"
CA_KEY  = "ca.key"

def load_ca():
    with open(CA_CERT, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())
    with open(CA_KEY, "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)
    return ca_cert, ca_key

# generate a fake certificate for a specific domain signed by our CA
def generate_cert(hostname, ca_cert, ca_key):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])
    cert = (x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(hostname)]), critical=False)
        .sign(ca_key, hashes.SHA256()))

    # save to temp files so ssl can load them
    tmp_cert = tempfile.NamedTemporaryFile(delete=False, suffix=".crt")
    tmp_key  = tempfile.NamedTemporaryFile(delete=False, suffix=".key")
    tmp_cert.write(cert.public_bytes(serialization.Encoding.PEM))
    tmp_key.write(key.private_bytes(serialization.Encoding.PEM,
                  serialization.PrivateFormat.TraditionalOpenSSL,
                  serialization.NoEncryption()))
    tmp_cert.close()
    tmp_key.close()
    return tmp_cert.name, tmp_key.name


def tunnel_data(client_ssl, server_ssl):
    # relay decrypted data both ways
    while True:
        readable, _, _ = select.select([client_ssl, server_ssl], [], [], 60)
        if not readable:
            break
        for sock in readable:
            try:
                data = sock.recv(BUFFER_SIZE)
                if sock is server_ssl:
                    logger.info(f"Intercepted data from server: {data[:100]}")
                if not data:
                    return
                if sock is client_ssl:
                    server_ssl.sendall(data)
                else:
                    client_ssl.sendall(data)
            except:
                return


def handle_client(client_socket, client_address, ca_cert, ca_key):
    try:
        raw = client_socket.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
        if not raw or not raw.startswith('CONNECT'):
            client_socket.close()
            return

        # extract host and port from CONNECT request
        first_line = raw.split('\r\n')[0]
        host_port  = first_line.split(' ')[1]
        host = host_port.split(':')[0]
        port = int(host_port.split(':')[1]) if ':' in host_port else 443

        if is_blocked(host):
            logger.warning(f"MITM BLOCKED: {host}")
            client_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            client_socket.close()
            return

        # tell browser tunnel is ready
        client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        # generate a fake cert for this domain
        cert_file, key_file = generate_cert(host, ca_cert, ca_key)

        try:
            # wrap client socket with our fake cert - browser thinks it's talking to the real site
            ctx_client = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx_client.load_cert_chain(certfile=cert_file, keyfile=key_file)
            client_ssl = ctx_client.wrap_socket(client_socket, server_side=True)

            # connect to real server with real SSL
            raw_server = socket.create_connection((host, port))
            ctx_server = ssl.create_default_context()
            server_ssl = ctx_server.wrap_socket(raw_server, server_hostname=host)

            logger.info(f"MITM intercepting: {host}:{port}")

            # relay data between browser and real server
            tunnel_data(client_ssl, server_ssl)

        finally:
            os.unlink(cert_file)
            os.unlink(key_file)

    except Exception as e:
        logger.error(f"MITM error {client_address}: {e}")
    finally:
        client_socket.close()


def start_mitm():
    ca_cert, ca_key = load_ca()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, MITM_PORT))
    server.listen(50)
    logger.info(f"MITM proxy listening on port {MITM_PORT}")
    print(f"MITM proxy running on port {MITM_PORT}")

    while True:
        client_socket, client_address = server.accept()
        thread = threading.Thread(target=handle_client,
                                  args=(client_socket, client_address, ca_cert, ca_key))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_mitm()