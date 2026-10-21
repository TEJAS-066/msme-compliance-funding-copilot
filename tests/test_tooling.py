"""Tests for the helper scripts and config - the tools you will use to verify AI-written changes."""
import importlib.util
import os
import sys

import pytest

from core import catalogue as C
from core import config

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "scripts", name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------- .env loader
def test_env_loader_parses_and_never_overrides(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text('# comment\nLLM_PROVIDER=gemini   # inline comment\nGEMINI_API_KEY="abc 123"\nEMPTY=   # blank placeholder\nKEEP=fromfile\nbad line\n')
    monkeypatch.delenv("LLM_PROVIDER", raising=False); monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("EMPTY", raising=False); monkeypatch.setenv("KEEP", "fromshell")
    loaded = config.load_env_file(str(f))
    assert sorted(loaded) == ["GEMINI_API_KEY", "LLM_PROVIDER"]
    assert os.environ["LLM_PROVIDER"] == "gemini" and os.environ["GEMINI_API_KEY"] == "abc 123"
    assert "EMPTY" not in os.environ and os.environ["KEEP"] == "fromshell"
    for k in ("LLM_PROVIDER", "GEMINI_API_KEY"):
        monkeypatch.delenv(k, raising=False)


def test_env_loader_missing_file_is_fine(tmp_path):
    assert config.load_env_file(str(tmp_path / "nope.env")) == []


def test_example_env_has_no_real_values(monkeypatch):
    for k in ("LLM_PROVIDER", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "SARVAM_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"):
        monkeypatch.delenv(k, raising=False)
    loaded = config.load_env_file(os.path.join(ROOT, ".env.example"))
    assert not {"ANTHROPIC_API_KEY", "GEMINI_API_KEY", "SARVAM_API_KEY", "TWILIO_AUTH_TOKEN", "TWILIO_ACCOUNT_SID", "LLM_PROVIDER"} & set(loaded)
    assert "PUBLIC_URL" not in loaded and os.environ.get("LLM_PROVIDER") is None   # blank-with-comment stays blank
    for k in loaded:
        monkeypatch.delenv(k, raising=False)


def test_get_prefers_environment(monkeypatch):
    monkeypatch.setenv("X_TEST_SETTING", "v")
    assert config.get("X_TEST_SETTING") == "v"
    assert config.get("X_NOT_SET_ANYWHERE", "dflt") == "dflt"


# ---------------- verify_phase
@pytest.fixture(scope="module")
def vp():
    return load_script("verify_phase")


def test_secret_scanner_finds_planted_keys_without_returning_values(tmp_path, vp):
    (tmp_path / "a.py").write_text('KEY = "AIza' + "x" * 35 + '"\n')
    (tmp_path / "b.txt").write_text("-----" + "BEGIN PRIVATE KEY-----\n")   # split so this file itself is not flagged
    (tmp_path / "c.md").write_text("nothing here")
    hits = vp.scan_secrets(str(tmp_path))
    assert {h[0] for h in hits} == {"a.py", "b.txt"}
    assert all("xxxx" not in str(h) for h in hits)


def test_secret_scanner_flags_untracked_env_without_gitignore(tmp_path, vp):
    (tmp_path / ".env").write_text("A=1\n")
    assert any(".env" in h[0] for h in vp.scan_secrets(str(tmp_path)))
    (tmp_path / ".gitignore").write_text(".env\n")
    assert not any("NOT in .gitignore" in h[1] for h in vp.scan_secrets(str(tmp_path)))


def test_repo_itself_has_no_secrets(vp):
    assert vp.scan_secrets() == []


def test_risky_claim_regex(vp):
    assert vp.RISKY.search("Your loan is guaranteed") and not vp.NEGATION.search("Your loan is guaranteed")
    assert vp.RISKY.search("The application was submitted") and vp.NEGATION.search("No application was submitted")
    assert vp.risky_strings() == []


# ---------------- catalogue coverage + scripts
def test_coverage_reports_secondary_only_criteria():
    rows = {r["scheme_id"]: r for r in C.coverage()}
    assert set(rows["pmmy_mudra"]["secondary_only"]) == {"nonfarm", "noncorporate"}
    assert rows["cgtmse"]["unsourced"] == [] and "udyam_cert" in rows["cgtmse"]["documents_unverified"]


def test_new_scheme_scaffold_creates_draft_that_app_ignores(tmp_path, monkeypatch, capsys):
    ns = load_script("new_scheme")
    monkeypatch.setattr(ns, "ROOT", str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["x", "--id", "pmegp", "--name", "PMEGP"])
    assert ns.main() == 0
    draft = tmp_path / "data" / "drafts" / "pmegp.json"
    assert draft.exists() and "unverified" in draft.read_text()
    assert ns.main() == 1                                   # refuses to overwrite
    monkeypatch.setattr(sys, "argv", ["x", "--id", "Bad Id", "--name", "x"])
    assert ns.main() == 1


def test_doctor_runs_and_reports_ready(capsys):
    d = load_script("doctor")
    assert d.main() == 0
    out = capsys.readouterr().out
    assert "RESULT: READY" in out and "Scheme catalogue valid" in out


def test_doctor_never_prints_secret_values(capsys, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini"); monkeypatch.setenv("GEMINI_API_KEY", "SUPER-SECRET-VALUE-123456")
    load_script("doctor").main()
    assert "SUPER-SECRET" not in capsys.readouterr().out


def test_check_llm_without_key_is_a_clean_noop(capsys, monkeypatch):
    for k in ("LLM_PROVIDER", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "SARVAM_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(sys, "argv", ["check_llm"])
    m = load_script("check_llm")
    monkeypatch.setattr(m.config, "load_env_file", lambda *a, **k: [])
    assert m.main() == 0 and "demo mode" in capsys.readouterr().out


def test_check_llm_reports_all_fallbacks_as_failure(capsys, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(sys, "argv", ["check_llm", "--provider", "gemini"])
    m = load_script("check_llm")
    monkeypatch.setattr(m.config, "load_env_file", lambda *a, **k: [])
    from services import llm
    def boom(*a, **k): raise llm.LLMError("network down")
    monkeypatch.setattr(llm, "complete", boom)
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "0/3" in out and "fell back" in out and "k" not in out.split("answer:")[0].replace("key", "")[:0]


# ---------------- webhook rate limiter
def test_rate_limiter_window():
    from services.whatsapp_server import RateLimiter
    t = [0.0]
    rl = RateLimiter(per_sender=3, total=5, clock=lambda: t[0])
    assert [rl.allow("a") for _ in range(4)] == [True, True, True, False]
    assert rl.allow("b") and rl.allow("c")             # other senders still fine (total 5 reached after)
    assert not rl.allow("d")                           # global cap
    t[0] = 61.0
    assert rl.allow("a") and rl.allow("d")             # window slid


def test_server_rate_limits_a_flooding_sender():
    import threading, urllib.parse, urllib.request
    from services.whatsapp_server import make_server
    srv = make_server("127.0.0.1", 0, env={"WA_ALLOW_UNSIGNED": "1"})
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{srv.server_address[1]}/whatsapp"
        bodies = []
        for _ in range(17):
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"Body": "hi", "From": "whatsapp:+911"}).encode(), method="POST")
            bodies.append(urllib.request.urlopen(req, timeout=10).read().decode())
        assert "Too many messages" in bodies[-1] and "Too many messages" not in bodies[0]
    finally:
        srv.shutdown()
