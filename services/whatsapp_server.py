"""Tiny stdlib HTTP server for the Twilio WhatsApp webhook (no extra dependencies).

Run:  python scripts/whatsapp_server.py     then expose it (e.g. ngrok) and set the Twilio sandbox
'When a message comes in' URL to  <PUBLIC_URL>/whatsapp .  Set PUBLIC_URL to that exact https URL
so signature verification uses the same URL Twilio signed.
Demo scope: ONE shared profile (the saved app profile, else the demo profile). Per-sender profiles +
consent are a roadmap item - do not use real customer data with this build.
"""
from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from core import db
from core import profile as P
from services.whatsapp import handle_webhook

MAX_BODY = 8 * 1024


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
        profile = db.load_profile() or P.load_demo_profile()
        code, ctype, body = handle_webhook(form, self.headers.get("X-Twilio-Signature"), url, profile,
                                           db.confirmed_doc_types(), env=self.server.env)
        self._send(code, ctype, body)

    def log_message(self, *a):  # never log message bodies (privacy)
        pass


def make_server(host: str = "127.0.0.1", port: int = 8765, env=None) -> HTTPServer:
    srv = HTTPServer((host, port), Handler)
    srv.env = os.environ if env is None else env
    return srv
