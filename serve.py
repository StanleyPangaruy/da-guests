#!/usr/bin/env python3
"""
Local server for the District Assembly LED board.

    python serve.py            # port 8080
    python serve.py 9000       # custom port

Board (browser source):  http://localhost:8080/
Operator control page:   http://localhost:8080/control.html
Standard library only — no pip installs needed.
"""
import json
import os
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

_lock = threading.Lock()
STATE = {
    "mode": "auto",     # auto = board rotates by itself, manual = operator picks the guest
    "index": 0,         # guest chosen by the operator (0-based)
    "interval": 12,     # seconds per guest in auto mode
    "blank": False,     # black out the wall
    "onAir": None,      # what the board reports it is currently showing
    "version": 0,
}


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Never cache, so edits to guests.csv / photos appear immediately.
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        if "/api/" not in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n).decode("utf-8") if n else ""

    def do_GET(self):
        if self.path.startswith("/api/state"):
            with _lock:
                return self._json(STATE)
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/state"):
            try:
                patch = json.loads(self._body() or "{}")
            except json.JSONDecodeError:
                return self._json({"error": "bad json"}, 400)
            with _lock:
                for k in ("mode", "index", "interval", "blank"):
                    if k in patch:
                        STATE[k] = patch[k]
                STATE["version"] += 1
                return self._json(STATE)
        if self.path.startswith("/api/onair"):
            try:
                with _lock:
                    STATE["onAir"] = int(self._body())
            except ValueError:
                pass
            return self._json({"ok": True})
        self.send_error(404)


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), partial(Handler, directory=ROOT))
    ip = lan_ip()
    print(f"\n  Board   : http://localhost:{PORT}/      (LAN: http://{ip}:{PORT}/)")
    print(f"  Control : http://localhost:{PORT}/control.html  (LAN: http://{ip}:{PORT}/control.html)")
    print("  Ctrl+C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
