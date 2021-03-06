#!/usr/bin/env python
"""
Very simple HTTP server in python (Updated for Python 3.7)

Usage:

    ./dummy-web-server.py -h
    ./dummy-web-server.py -l localhost -p 8000

Send a GET request:

    curl http://localhost:8000

Send a HEAD request:

    curl -I http://localhost:8000

Send a POST request:

    curl -d "foo=bar&bin=baz" http://localhost:8000

"""
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import cgi
import ml

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.

        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!\

    def _json(self, message):
      content = json.dumps(message)
      return content.encode('utf8')

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("hi!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        print("HEADERS: ", self.headers)
        try: 
          ctype = self.headers['Content-Type']
          if ctype != 'application/json':
            self.wfile.write(self.html('fail!'))
            return
          
          length = int(self.headers['Content-Length'])
          j = json.loads(self.rfile.read(length))

          if 'question' not in j:
            self.wfile.write(self._html('fail! question'))
            return

          if 'context' not in j:
            self.wfile.write(self._html('fail! context'))
            return

          bert = ml.load_bert()
          res = ml.run_bert(bert, j)
          print(res['score'])
          self._set_headers()
          self.wfile.write(self._json(res))
        except Exception as e:
          print(e)
          self._set_headers()

          self.wfile.write(self._html('nothing'))


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
