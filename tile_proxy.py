#!/usr/bin/env python3
"""Tile proxy + static file server for chase-game web version."""
import http.server
import urllib.request
import urllib.parse
import os

PORT = 18765
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
TILE_UA = 'ChaseGame/2.0'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith('/proxy_tile?'):
            self.proxy_tile_generic()
        elif self.path.startswith('/tile/'):
            self.proxy_tile()
        elif 'tianditu.gov.cn' in self.path:
            self.proxy_direct()
        else:
            super().do_GET()

    def proxy_tile_generic(self):
        """Proxy /proxy_tile?url=<encoded_url> with custom UA."""
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        url = params.get('url', [None])[0]
        if not url:
            self.send_error(400, "Missing url parameter")
            return
        self._fetch(url)

    def proxy_tile(self):
        parts = self.path.strip('/').split('/')
        if len(parts) < 4:
            self.send_error(400)
            return
        _, z, x, y = parts[0], parts[1], parts[2], parts[3]
        key = '526d518941b3e52f37d0015698800f74'
        server = int(x) % 8
        url = f"https://t{server}.tianditu.gov.cn/DataServer?T=img_c&X={x}&Y={y}&L={z}&tk={key}"
        self._fetch(url)

    def proxy_direct(self):
        url = urllib.parse.unquote(self.path.lstrip('/'))
        self._fetch(url)

    def _fetch(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': TILE_UA})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                ctype = resp.headers.get('Content-Type', 'image/jpeg')
                self.send_response(200)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    with http.server.HTTPServer(('127.0.0.1', PORT), Handler) as httpd:
        print(f"Tile proxy on http://127.0.0.1:{PORT}")
        httpd.serve_forever()
