#!/usr/bin/env python3
"""Wings of Fire: LAN game host and lightweight player-position relay.

No third-party Python packages are required.
"""
import argparse
import gzip
import json
import math
import mimetypes
import re
import socket
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
PLAYERS = {}
PLAYERS_LOCK = threading.Lock()
PLAYER_TTL = 7.0
MAX_PLAYERS = 32
PLAYER_ID = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")
# Cached compressed static assets are shared between simultaneous LAN clients.
FILE_CACHE = {}
CACHE_LOCK = threading.Lock()


def local_ip():
    # Determines the outgoing interface's address without sending data over the Internet.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 80))
            return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"


class GameHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("[wings] %s - %s" % (self.address_string(), fmt % args), flush=True)

    def send_data(self, status, payload, content_type, extra=None, head=False):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if not head and payload:
            self.wfile.write(payload)

    def send_json(self, status, data):
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_data(status, payload, "application/json; charset=utf-8",
                       {"Cache-Control": "no-store"})

    def serve_static(self, head=False):
        requested = urlsplit(self.path).path
        if requested == "/":
            requested = "/index.html"
        # Never expose .git, scripts, saves or other filesystem files.
        if requested not in ("/index.html", "/Qwen_html_20261010_w6p7ub4fi.html") and not (
                requested.startswith("/src/js/") and requested.endswith(".js")
                and "/" not in requested[len("/src/js/"):]):
            self.send_error(404, "Not found")
            return
        path = ROOT / requested.lstrip("/")
        if not path.is_file():
            self.send_error(404, "Not found")
            return
        stat = path.stat()
        version = (stat.st_mtime_ns, stat.st_size)
        etag = '"%x-%x"' % version
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", "no-cache" if path.suffix == ".html" else "public, max-age=3600")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        with CACHE_LOCK:
            cached = FILE_CACHE.get(str(path))
            if cached is None or cached[0] != version:
                raw = path.read_bytes()
                compressed = gzip.compress(raw, compresslevel=6, mtime=0)
                cached = (version, raw, compressed)
                FILE_CACHE[str(path)] = cached
        use_gzip = "gzip" in self.headers.get("Accept-Encoding", "").lower()
        payload = cached[2] if use_gzip else cached[1]
        headers = {
            "Cache-Control": "no-cache" if path.suffix == ".html" else "public, max-age=3600",
            "ETag": etag,
            "Vary": "Accept-Encoding",
        }
        if use_gzip:
            headers["Content-Encoding"] = "gzip"
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix in (".js", ".html"):
            media_type += "; charset=utf-8"
        self.send_data(200, payload, media_type, headers, head=head)

    def do_GET(self):
        if urlsplit(self.path).path == "/health":
            self.send_json(200, {"status": "ok"})
        else:
            self.serve_static()

    def do_HEAD(self):
        self.serve_static(head=True)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/state":
            self.send_json(404, {"error": "unknown endpoint"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 2048:
                self.send_json(413, {"error": "invalid request size"})
                return
            data = json.loads(self.rfile.read(size).decode("utf-8"))
            player_id = data.get("id")
            if not isinstance(player_id, str) or not PLAYER_ID.fullmatch(player_id):
                raise ValueError("invalid player id")
            coords = {}
            for name in ("x", "y", "z", "angle", "flap", "bank", "spd"):
                number = data.get(name, 0)
                if isinstance(number, bool) or not isinstance(number, (int, float)):
                    raise ValueError("invalid position")
                number = float(number)
                if not math.isfinite(number) or abs(number) > 100000:
                    raise ValueError("invalid position")
                coords[name] = number
            name = str(data.get("name", "Дракон"))[:20]
        except (ValueError, UnicodeError, TypeError, AttributeError, json.JSONDecodeError):
            self.send_json(400, {"error": "invalid player state"})
            return

        now = time.monotonic()
        with PLAYERS_LOCK:
            expired = [pid for pid, entry in PLAYERS.items() if now - entry["updated"] > PLAYER_TTL]
            for pid in expired:
                del PLAYERS[pid]
            if player_id not in PLAYERS and len(PLAYERS) >= MAX_PLAYERS:
                self.send_json(503, {"error": "player limit reached"})
                return
            PLAYERS[player_id] = {"id": player_id, "name": name, **coords, "updated": now}
            others = [{k: v for k, v in p.items() if k != "updated"}
                      for pid, p in PLAYERS.items() if pid != player_id]
            online = len(PLAYERS)
        self.send_json(200, {"online": online, "players": others})


def main():
    parser = argparse.ArgumentParser(description="Wings of Fire LAN server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: all LAN interfaces)")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    try:
        with ThreadingHTTPServer((args.host, args.port), GameHandler) as httpd:
            print("Wings of Fire started", flush=True)
            print("  This PC: http://localhost:%d/" % args.port, flush=True)
            print("  Wi-Fi:   http://%s:%d/" % (local_ip(), args.port), flush=True)
            print("  Ctrl+C to stop. Allow Python through the OS firewall if needed.", flush=True)
            if not args.no_browser:
                webbrowser.open("http://localhost:%d/" % args.port)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as exc:
        parser.exit(1, "Cannot start server: %s\n" % exc)


if __name__ == "__main__":
    main()
