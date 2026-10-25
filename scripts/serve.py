#!/usr/bin/env python3
"""Dependency-free local static server with normal production-style gzip support.
Usage: python scripts/serve.py --port 4173. Do not expose sensitive directories.
"""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
from io import BytesIO
import argparse,gzip
R=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  p=Path(self.translate_path(self.path))
  if p.is_dir():p=p/'index.html'
  if p.is_file() and p.suffix in ['.html','.css','.js','.json','.svg'] and 'gzip' in self.headers.get('Accept-Encoding',''):
   data=gzip.compress(p.read_bytes(),compresslevel=6);self.send_response(200);self.send_header('Content-type',self.guess_type(str(p)));self.send_header('Content-Encoding','gzip');self.send_header('Vary','Accept-Encoding');self.send_header('Content-Length',str(len(data)));self.send_header('Last-Modified',self.date_time_string(p.stat().st_mtime));self.send_header('Cache-Control','no-cache' if p.suffix=='.html' else 'public, max-age=3600');self.end_headers();return BytesIO(data)
  return super().send_head()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=4173);args=parser.parse_args();print(f'Serving {R} on port {args.port}',flush=True);ThreadingHTTPServer(('0.0.0.0',args.port),partial(Handler,directory=str(R))).serve_forever()
