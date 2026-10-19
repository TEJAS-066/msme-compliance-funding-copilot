"""WhatsApp (Twilio) webhook logic as PURE functions - same code path the simulator page uses.

Security: if TWILIO_AUTH_TOKEN is set every request must carry a valid X-Twilio-Signature
(HMAC-SHA1 over URL + sorted POST params, base64). With no token the webhook REFUSES requests
unless WA_ALLOW_UNSIGNED=1 (local development only).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from xml.sax.saxutils import escape

from core.i18n import t
from services.channel import detect_language, handle_incoming

GREETINGS = {"hi", "hello", "hey", "help", "menu", "start", "வணக்கம்", "உதவி", "नमस्ते", "प्रणाम", "నమస్కారం"}


def twilio_signature(auth_token: str, url: str, params: dict) -> str:
    data = url + "".join(f"{k}{params[k]}" for k in sorted(params))
    return base64.b64encode(hmac.new(auth_token.encode(), data.encode(), hashlib.sha1).digest()).decode()


def verify_signature(auth_token: str, url: str, params: dict, header_sig: str | None) -> bool:
    if not header_sig:
        return False
    return hmac.compare_digest(twilio_signature(auth_token, url, params), header_sig)


def twiml(text: str) -> str:
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escape(text)}</Message></Response>'


def handle_message(text: str, profile: dict, confirmed: set[str] | None = None, lang: str | None = None) -> str:
    text = (text or "").strip()
    lang = lang or detect_language(text)
    if not text or text.lower() in GREETINGS:
        return t("wa_menu", lang)
    return handle_incoming(text, profile, confirmed, lang)


def handle_webhook(form: dict, header_sig: str | None, url: str, profile: dict, confirmed: set[str] | None = None,
                   env=None) -> tuple[int, str, str]:
    """Returns (http_status, content_type, body)."""
    env = os.environ if env is None else env
    token = env.get("TWILIO_AUTH_TOKEN")
    if token:
        if not verify_signature(token, url, form, header_sig):
            return 403, "text/plain", "invalid signature"
    elif env.get("WA_ALLOW_UNSIGNED") != "1":
        return 403, "text/plain", "refusing unsigned requests: set TWILIO_AUTH_TOKEN (or WA_ALLOW_UNSIGNED=1 for local dev only)"
    reply = handle_message(form.get("Body", ""), profile, confirmed)
    return 200, "text/xml", twiml(reply)
