from datetime import date

import pytest

from core import profile as P
from services import channel, llm, monitoring as M, notifications as N


class FakeResp:
    def __init__(self, status=200, body=None, content=b"page"):
        self.status_code, self._b, self.content = status, body or {}, content

    def json(self): return self._b
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


# ---- llm adapter
def test_provider_requires_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert llm.get_provider() is None                      # no key -> demo mode
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    assert llm.get_provider() == "anthropic"


def test_unknown_provider_ignored(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "skynet"); monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    assert llm.get_provider() is None


@pytest.mark.parametrize("prov,env,body,expected", [
    ("anthropic", "ANTHROPIC_API_KEY", {"content": [{"type": "text", "text": "hi"}]}, "hi"),
    ("gemini", "GEMINI_API_KEY", {"candidates": [{"content": {"parts": [{"text": "hi"}]}}]}, "hi"),
    ("sarvam", "SARVAM_API_KEY", {"choices": [{"message": {"content": "hi"}}]}, "hi"),
])
def test_each_provider_parses_response(monkeypatch, prov, env, body, expected):
    monkeypatch.setenv(env, "k")
    calls = {}
    def post(url, **kw): calls.update(url=url, **kw); return FakeResp(200, body)
    assert llm.complete("sys", "user", prov, post=post) == expected
    assert "k" not in calls["url"]                           # key never put in the URL


def test_http_error_becomes_llmerror(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    with pytest.raises(llm.LLMError):
        llm.complete("s", "u", "anthropic", post=lambda *a, **k: FakeResp(500))


def test_malformed_json_becomes_llmerror(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    with pytest.raises(llm.LLMError):
        llm.complete("s", "u", "gemini", post=lambda *a, **k: FakeResp(200, {"weird": 1}))


def test_complete_without_provider_raises():
    with pytest.raises(llm.LLMError):
        llm.complete("s", "u")


# ---- notifications
def test_reminder_preview_text_both_languages():
    task = {"title": "Collect Udyam certificate", "due_date": "2026-11-01"}
    assert "Preview only" in N.preview_reminder(task, "en")
    assert "முன்னோட்டம்" in N.preview_reminder(task, "ta")
    assert "no due date" in N.preview_reminder({"title": "x", "due_date": None}, "en")


def test_whatsapp_not_configured_never_claims_sent():
    r = N.send_whatsapp("+910000000000", "hi", post=lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not call")))
    assert r.status == "NOT_CONFIGURED"


@pytest.fixture
def twilio_env(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123"); monkeypatch.setenv("TWILIO_AUTH_TOKEN", "tok"); monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "+14155238886")


def test_whatsapp_sent_only_on_201_with_sid(twilio_env):
    assert N.send_whatsapp("+91x", "hi", post=lambda *a, **k: FakeResp(201, {"sid": "SM1"})).status == "SENT"
    assert N.send_whatsapp("+91x", "hi", post=lambda *a, **k: FakeResp(201, {})).status == "FAILED"
    assert N.send_whatsapp("+91x", "hi", post=lambda *a, **k: FakeResp(400, {"sid": "x"})).status == "FAILED"


def test_whatsapp_network_error_is_failed(twilio_env):
    def boom(*a, **k): raise ConnectionError()
    assert N.send_whatsapp("+91x", "hi", post=boom).status == "FAILED"


# ---- monitoring
def test_staleness_detection():
    rows = M.stale_schemes(today=date(2027, 6, 1))
    assert all(r["stale"] for r in rows)
    rows = M.stale_schemes(today=date(2026, 10, 19))
    assert not any(r["stale"] for r in rows)


def test_nothing_notifiable_until_admin_approves():
    assert M.notifiable_items() == []
    M.decide("upd-demo-001", "approved")
    assert [i["id"] for i in M.notifiable_items()] == ["upd-demo-001"]
    M.decide("upd-demo-001", "rejected")
    assert M.notifiable_items() == []


def test_invalid_decision_rejected():
    with pytest.raises(ValueError):
        M.decide("upd-demo-001", "maybe")


def test_demo_queue_item_is_labelled_synthetic():
    assert all(i["kind"] == "DEMO_SYNTHETIC" for i in M.load_queue())


def test_fetch_and_hash_ok_and_failures():
    ok = M.fetch_and_hash("https://x", get=lambda *a, **k: FakeResp(200, content=b"abc"))
    assert ok["ok"] and len(ok["hash"]) == 64
    assert M.fetch_and_hash("https://x", get=lambda *a, **k: FakeResp(404))["ok"] is False
    def boom(*a, **k): raise TimeoutError()
    assert M.fetch_and_hash("https://x", get=boom)["error"] == "TimeoutError"
    a = M.fetch_and_hash("https://x", get=lambda *a, **k: FakeResp(200, content=b"v1"))["hash"]
    b = M.fetch_and_hash("https://x", get=lambda *a, **k: FakeResp(200, content=b"v2"))["hash"]
    assert a != b                                              # change detection primitive


# ---- channel (WhatsApp-style text)
def test_language_detection():
    assert channel.detect_language("எனக்கு தகுதி உள்ளதா") == "ta"
    assert channel.detect_language("am I eligible") == "en"


def test_handle_incoming_returns_bounded_text_with_sources(demo):
    out = channel.handle_incoming("Am I eligible for MUDRA?", demo)
    assert len(out) <= channel.MAX_LEN and "http" in out
    ta = channel.handle_incoming("எனக்கு MUDRA தகுதி உள்ளதா?", demo)
    assert "நாங்கள் குறியிட்ட" in ta
