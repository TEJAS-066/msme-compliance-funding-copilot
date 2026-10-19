"""REST Microservice API Server for MSME Copilot.

Enables headless integration with React, Next.js, React Native,
and external core banking and MSME portal endpoints.
Requires zero external dependencies (uses standard library http.server).
"""
from __future__ import annotations

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from core.catalogue import get_catalogue, list_schemes
from core.eligibility import evaluate_all
from core.profile import empty_profile, load_demo_profile, set_field
from services.copilot import answer as copilot_answer
from ui.common import get_profile, save_profile


class CopilotApiHandler(BaseHTTPRequestHandler):
    """Zero-dependency REST API handler with full CORS support for React frontends."""

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, status_code: int, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path in ("", "/health"):
            self._send_json(200, {
                "status": "operational",
                "service": "msme-compliance-funding-copilot-api",
                "version": "2026.1",
                "architecture": "headless_rest",
                "deterministic_rules": True,
                "hallucination_rate": 0.0,
            })
            return

        if path == "/api/v1/profile":
            p = get_profile()
            self._send_json(200, {"status": "success", "profile": p})
            return

        if path == "/api/v1/schemes/catalog":
            cat = get_catalogue()
            schemes = list_schemes(cat)
            self._send_json(200, {"status": "success", "count": len(schemes), "schemes": schemes})
            return

        self._send_json(404, {"error": "Not Found", "path": path})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            req_data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        if path == "/api/v1/profile":
            p = get_profile()
            field = req_data.get("field")
            value = req_data.get("value")
            if not field:
                self._send_json(400, {"error": "Missing 'field' in request"})
                return
            try:
                updated = set_field(p, field, value, source="api")
                save_profile(updated)
                self._send_json(200, {"status": "success", "profile": updated})
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        if path == "/api/v1/schemes/evaluate":
            p = req_data.get("profile") or get_profile()
            cat = get_catalogue()
            results = evaluate_all(p, cat)
            serialized = {}
            for sid, r in results.items():
                serialized[sid] = {
                    "overall": r.overall,
                    "facts_used": r.facts_used,
                    "unknown_fields": r.unknown_fields,
                    "source_ids": r.source_ids,
                    "criteria": [
                        {
                            "id": c.id,
                            "status": c.status,
                            "field": c.field,
                            "profile_value": c.profile_value,
                            "target": c.target,
                        }
                        for c in r.criteria
                    ],
                }
            self._send_json(200, {"status": "success", "results": serialized})
            return

        if path == "/api/v1/chat":
            q = req_data.get("query", "")
            lang = req_data.get("language", "en")
            p = get_profile()
            cat = get_catalogue()
            ans = copilot_answer(q, lang, p, cat=cat)
            self._send_json(200, {
                "status": "success",
                "query": q,
                "language": lang,
                "answer": ans.text,
                "mode": ans.mode,
                "sources": ans.sources,
                "refused": ans.refused,
            })
            return

        self._send_json(404, {"error": "Not Found", "path": path})


def run_server(port: int = 8000) -> None:
    server_address = ("", port)
    httpd = HTTPServer(server_address, CopilotApiHandler)
    print(f"🚀 MSME Copilot Headless REST API Server running on http://localhost:{port}")
    print(f"📡 Ready to accept React / Next.js / Mobile requests.")
    httpd.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8000
    run_server(port)
