# -*- coding: utf-8 -*-
"""
backend/serve_frontend_5173.py
High-performance HTTP Server & Reverse Proxy running on port 5173.
Serves the complete buisyvizzy frontend and proxies backend API calls to port 8000.
"""

import sys
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 5173
BACKEND_URL = "http://127.0.0.1:8000"

class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Keep console output clean
        pass

    def do_GET(self):
        # If requesting root or /app, forward to /web on backend
        target_path = self.path
        if target_path in ["/", "/index.html", "/app"]:
            target_path = "/web"

        url = f"{BACKEND_URL}{target_path}"
        try:
            req = urllib.request.Request(url, headers={k: v for k, v in self.headers.items() if k.lower() != 'host'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.send_response(resp.status)
                for header, val in resp.getheaders():
                    if header.lower() not in ['transfer-encoding', 'content-length']:
                        self.send_header(header, val)
                body = resp.read()
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as err:
            self.send_response(502)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            msg = f"<h3>buisyvizzy Gateway Error</h3><p>Could not connect to authoritative backend at :8000: {err}</p>"
            self.wfile.write(msg.encode('utf-8'))

    def do_POST(self):
        target_path = self.path
        url = f"{BACKEND_URL}{target_path}"
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None

        try:
            req = urllib.request.Request(
                url,
                data=post_data,
                headers={k: v for k, v in self.headers.items() if k.lower() != 'host'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.send_response(resp.status)
                for header, val in resp.getheaders():
                    if header.lower() not in ['transfer-encoding', 'content-length']:
                        self.send_header(header, val)
                body = resp.read()
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as err:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(err).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

def run():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f"buisyvizzy Frontend Server running live on http://localhost:{PORT}")
    sys.stdout.flush()
    httpd.serve_forever()

if __name__ == '__main__':
    run()
