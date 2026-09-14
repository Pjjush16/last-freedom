#!/usr/bin/env python3
"""统一游戏服务器 - 同时提供页面和瓦片代理"""
import http.server
import urllib.request
import os

PORT = 8877
TIANDITU_KEY = "YOUR_TIANDITU_KEY_HERE"
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')

class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)
    
    def do_GET(self):
        parts = self.path.strip('/').split('/')
        if len(parts) == 5 and parts[0] == 'tile':
            self._proxy_tile(parts[1], parts[2], parts[3], parts[4])
        else:
            super().do_GET()
    
    def _proxy_tile(self, layer, z, x, y):
        subdomain = f"t{hash(f'{x}{y}') % 8}"
        layer_prefix = layer.split('_')[0]
        tileset = layer.split('_')[1] if '_' in layer else 'w'
        
        url = (f"https://{subdomain}.tianditu.gov.cn/{layer}/wmts?"
               f"SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
               f"&LAYER={layer_prefix}&STYLE=default"
               f"&TILEMATRIXSET={tileset}&FORMAT=tiles"
               f"&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
               f"&tk={TIANDITU_KEY}")
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'TiandituClient/1.0',
                'Accept': 'image/*'
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                content_type = resp.headers.get('Content-Type', 'image/jpeg')
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Proxy error: {e}".encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), GameHandler)
    print(f"Game server on 0.0.0.0:{PORT}")
    server.serve_forever()
