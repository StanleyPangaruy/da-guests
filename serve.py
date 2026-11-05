#!/usr/bin/env python3
"""
Local server for the District Assembly LED board.

    python serve.py            # port 8080
    python serve.py 9000       # custom port

Board (browser source):  http://localhost:8080/
Operator control page:   http://localhost:8080/control.html
Standard library only — no pip installs needed.
"""
import csv
import io
import json
import os
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

EVENT_FILE = os.path.join(ROOT, "event.json")
OLD_DISTRICTS_FILE = os.path.join(ROOT, "districts.json")
CSV_FILE = os.path.join(ROOT, "guests.csv")
PHOTOS_DIR = os.path.join(ROOT, "photos")
EVENT_FIELDS = ("event_title", "district", "date", "time", "venue", "address", "speaker", "speaker_title")
GUEST_COLUMNS = ["active", "honorific", "name", "position", "photo"]
PHOTO_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")

_lock = threading.Lock()


def _clean(d):
    return {k: str(d.get(k, "")).strip() for k in EVENT_FIELDS}


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return -1


def load_event():
    if _mtime(EVENT_FILE) >= _mtime(OLD_DISTRICTS_FILE):
        try:
            with open(EVENT_FILE, encoding="utf-8") as f:
                return _clean(json.load(f))
        except (OSError, ValueError):
            pass
    try:  # carry over details from the per-district version if that is newer
        with open(OLD_DISTRICTS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        ds = data.get("districts", [])
        active = next((d for d in ds if d.get("id") == data.get("active")), ds[0] if ds else {})
        return _clean(active)
    except (OSError, ValueError, IndexError):
        return _clean({"event_title": "District Assembly"})


def save_event(ev):
    tmp = EVENT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=2)
    os.replace(tmp, EVENT_FILE)


def save_guests(rows):
    """Write guests.csv from the control page. Keeps any extra columns already in the file."""
    extra = []
    for r in rows:
        for k in r:
            if k not in GUEST_COLUMNS and k not in extra and k:
                extra.append(k)
    cols = GUEST_COLUMNS + extra
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: str(r.get(k, "") or "").strip() for k in cols})
    # utf-8 with BOM so Excel shows Ñ and accents correctly
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        f.write(buf.getvalue())


def list_photos():
    try:
        names = sorted(n for n in os.listdir(PHOTOS_DIR) if n.lower().endswith(PHOTO_EXT))
    except OSError:
        names = []
    return ["photos/" + n for n in names]


STATE = {
    "mode": "manual",   # the operator picks the guest on control.html
    "index": 0,         # guest on the wall (0-based)
    "blank": False,     # black out the wall
    "main": False,      # show the main background instead of a guest
    "onAir": None,      # what the board reports it is currently showing
    "version": 0,
    "guestsVersion": 0,      # bumped when the control page saves guests.csv
    "event": load_event(),   # district / date / time / venue (saved in event.json)
}


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Never cache, so edits to guests.csv / photos appear immediately.
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        if "/api/" not in str(args[0] if args else ""):
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
        if self.path.startswith("/api/photos"):
            return self._json(list_photos())
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/state"):
            try:
                patch = json.loads(self._body() or "{}")
            except json.JSONDecodeError:
                return self._json({"error": "bad json"}, 400)
            with _lock:
                for k in ("index", "blank", "main"):
                    if k in patch:
                        STATE[k] = patch[k]
                STATE["version"] += 1
                return self._json(STATE)
        if self.path.startswith("/api/event"):
            try:
                patch = json.loads(self._body() or "{}")
            except json.JSONDecodeError:
                return self._json({"error": "bad json"}, 400)
            with _lock:
                ev = dict(STATE["event"])
                for k in EVENT_FIELDS:
                    if k in patch:
                        ev[k] = str(patch[k]).strip()
                STATE["event"] = ev
                save_event(ev)
                return self._json(STATE)
        if self.path.startswith("/api/guests"):
            # {"rows": [{active, honorific, name, position, photo, ...}], "index": n}
            try:
                req = json.loads(self._body() or "{}")
                rows = [r for r in req.get("rows", []) if isinstance(r, dict)]
            except (json.JSONDecodeError, AttributeError):
                return self._json({"error": "bad json"}, 400)
            with _lock:
                try:
                    save_guests(rows)
                except PermissionError:
                    return self._json({"error": "guests.csv is open in another program (close Excel)"}, 409)
                STATE["guestsVersion"] += 1
                if isinstance(req.get("index"), int):
                    STATE["index"] = req["index"]
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
