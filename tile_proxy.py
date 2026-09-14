#!/usr/bin/env python3
"""Local proxy - serves tiles + stickers"""
import http.server
import urllib.request
import urllib.parse
import os
import sys

STICKER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'stickers')
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
STICKERS_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stickers')

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == '/tile':
            url = params.get('url', [None])[0]
            if not url:
                self.send_error(400, "Missing url")
                return
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "ChaseGame/2.0"})
                resp = urllib.request.urlopen(req, timeout=10)
                data = resp.read()
                ct = resp.headers.get("Content-Type", "image/jpeg")
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "max-age=86400")
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(502, str(e))
        
        elif parsed.path.startswith('/sticker/'):
            # Serve sticker images (check assets/stickers first, then stickers/)
            filename = parsed.path.split('/')[-1]
            filepath = os.path.join(STICKER_DIR, filename)
            if not os.path.exists(filepath):
                filepath = os.path.join(STICKERS_SRC, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                ct = 'image/png' if filename.endswith('.png') else 'image/jpeg'
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "max-age=86400")
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(404, f"Sticker not found: {filename}")
        
        elif parsed.path.startswith('/audio/'):
            # Serve audio files (MP3/OGG)
            filename = parsed.path.split('/')[-1]
            filepath = os.path.join(AUDIO_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                ct = 'audio/mpeg' if filename.endswith('.mp3') else 'audio/ogg'
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "max-age=86400")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(404, f"Audio not found: {filename}")
        
        elif parsed.path in ('/', '/index.html'):
            filepath = os.path.join(SRC_DIR, 'index.html')
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)
    
    def log_message(self, *a): pass

if __name__ == "__main__":
    s = http.server.HTTPServer(("127.0.0.1", 18765), Handler)
    print("Proxy on http://127.0.0.1:18765", flush=True)
    s.serve_forever()
