# CSC 430 - Caching Proxy Server

A multithreaded HTTP/HTTPS caching proxy server with blacklist filtering, MITM interception, and a live admin dashboard.

## Team
- Leen Nassar
- Antonio Karam

## Requirements
- Python 3.x
- pip install flask pyopenssl cryptography

## How to Run

### Main Proxy
1. Run the proxy server:
   python proxy.py
2. Set your browser proxy to IP 127.0.0.1 and Port 8888
3. Access the admin interface at http://127.0.0.1:5000

### MITM Proxy (Bonus H)
1. Import ca.crt into Firefox: Settings, Privacy, Certificates, Authorities, Import
2. Run the MITM proxy:
   py -3.12 proxy_mitm.py
3. Set your browser proxy to IP 127.0.0.1 and Port 8889

## Features
- HTTP proxy with request parsing
- HTTPS support using CONNECT tunneling
- MITM interception (bonus)
- In-memory caching with expiration
- Blacklist filtering (including subdomains)
- Multi-threaded client handling
- Logging to file and console
- Flask-based admin dashboard

## Project Structure
- proxy.py , main proxy server (Leen)
- proxy_mitm.py , HTTPS MITM proxy (Leen)
- config.py , settings (Leen)
- admin.py ,  admin dashboard (Antonio)
- blacklist.py ,  URL filtering (Antonio)
- ca.crt ,  root CA certificate
- cache/cache_manager.py , caching logic (Antonio)
- logs/logger.py , logging (Antonio)
