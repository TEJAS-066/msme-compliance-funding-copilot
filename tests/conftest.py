import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Every test gets its own SQLite file and NO accidental LLM/Twilio credentials."""
    monkeypatch.setenv("MSME_DB_PATH", str(tmp_path / "test.db"))
    for k in ("LLM_PROVIDER", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "SARVAM_API_KEY",
              "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM"):
        monkeypatch.delenv(k, raising=False)
    yield


@pytest.fixture
def demo():
    from core import profile as P
    return P.load_demo_profile()


@pytest.fixture
def empty():
    from core import profile as P
    return P.empty_profile()
