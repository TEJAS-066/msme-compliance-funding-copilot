"""Channel adapter: the same copilot behind WhatsApp/SMS-style plain text.

`handle_incoming` is a pure function (easy to test). To go live, a ~20 line webhook
(Twilio WhatsApp sandbox -> FastAPI/Flask) calls it; see docs/ROADMAP phase 5.
"""
from __future__ import annotations

from services.copilot import answer

TAMIL_RANGE = (0x0B80, 0x0BFF)
HINDI_RANGE = (0x0900, 0x097F)
TELUGU_RANGE = (0x0C00, 0x0C7F)
MAX_LEN = 1500  # WhatsApp messages are length-limited; keep headroom


def detect_language(text: str) -> str:
    if any(TAMIL_RANGE[0] <= ord(ch) <= TAMIL_RANGE[1] for ch in text):
        return "ta"
    if any(HINDI_RANGE[0] <= ord(ch) <= HINDI_RANGE[1] for ch in text):
        return "hi"
    if any(TELUGU_RANGE[0] <= ord(ch) <= TELUGU_RANGE[1] for ch in text):
        return "te"
    return "en"


def handle_incoming(text: str, profile: dict, confirmed_types: set[str] | None = None, lang: str | None = None) -> str:
    lang = lang or detect_language(text)
    a = answer(text, lang, profile, confirmed_types, use_llm=True)
    body = a.text
    if a.sources:
        body += "\n\n" + "\n".join(f"• {s['title']} ({s['tier']}) {s['url']}" for s in a.sources[:3])
    return body if len(body) <= MAX_LEN else body[: MAX_LEN - 1] + "…"
