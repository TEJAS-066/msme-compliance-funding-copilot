"""Tiny stdlib HTTP server for the Twilio WhatsApp webhook (no extra dependencies).

Run:  python scripts/whatsapp_server.py     then expose it (e.g. ngrok) and set the Twilio sandbox
'When a message comes in' URL to  <PUBLIC_URL>/whatsapp .  Set PUBLIC_URL to that exact https URL
so signature verification uses the same URL Twilio signed.
Demo scope: ONE shared profile (the saved app profile, else the demo profile). Per-sender profiles +
consent are a roadmap item - do not use real customer data with this build.
"""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from core import db
from core import profile as P
from services.whatsapp import handle_webhook

MAX_BODY = 8 * 1024
PER_SENDER_PER_MIN = 15
TOTAL_PER_MIN = 120


class RateLimiter:
    """Sliding 60-second window per sender and overall (in memory; resets on restart)."""

    def __init__(self, per_sender: int = PER_SENDER_PER_MIN, total: int = TOTAL_PER_MIN, clock=time.monotonic):
        self.per_sender, self.total, self.clock = per_sender, total, clock
        self.by_sender: dict[str, deque] = defaultdict(deque)
        self.all: deque = deque()

    def allow(self, sender: str) -> bool:
        now = self.clock()
        for q in (self.by_sender[sender], self.all):
            while q and now - q[0] > 60:
                q.popleft()
        if len(self.by_sender[sender]) >= self.per_sender or len(self.all) >= self.total:
            return False
        self.by_sender[sender].append(now)
        self.all.append(now)
        return True


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, ctype: str, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # health check
        self._send(200, "text/plain", "ok") if self.path in ("/", "/health") else self._send(404, "text/plain", "not found")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if self.path != "/whatsapp":
            if n > 0:
                self.rfile.read(min(n, MAX_BODY))
            return self._send(404, "text/plain", "not found")
        if n > MAX_BODY:
            if n > 0:
                self.rfile.read(min(n, MAX_BODY))
            return self._send(413, "text/plain", "too large")
        form = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode("utf-8", "replace")).items()}
        url = os.environ.get("PUBLIC_URL") or f"http://{self.headers.get('Host', '')}{self.path}"
        if not self.server.limiter.allow(form.get("From", "?")):
            from services.whatsapp import twiml
            return self._send(200, "text/xml", twiml("Too many messages — please wait a minute and try again. / சற்று காத்திருந்து மீண்டும் முயற்சிக்கவும்."))
        profile = db.load_profile() or P.load_demo_profile()
        code, ctype, body = handle_webhook(form, self.headers.get("X-Twilio-Signature"), url, profile,
                                           db.confirmed_doc_types(), env=self.server.env)
        self._send(code, ctype, body)

    def log_message(self, *a):  # never log message bodies (privacy)
        pass


def make_server(host: str = "127.0.0.1", port: int = 8765, env=None) -> HTTPServer:
    srv = HTTPServer((host, port), Handler)
    srv.env = os.environ if env is None else env
    srv.limiter = RateLimiter()
    return srv
