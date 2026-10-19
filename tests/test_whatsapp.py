import json
import threading
import urllib.error
import urllib.request
import urllib.parse

import pytest

from services import whatsapp as W
from services.whatsapp_server import make_server

URL = "https://mycompany.com/myapp.php?foo=1&bar=2"
PARAMS = {"Digits": "1234", "To": "+18005551212", "From": "+14158675310", "Caller": "+14158675310", "CallSid": "CA1234567890ABCDE"}


def test_signature_matches_twilio_official_library():
    # value produced by twilio.request_validator.RequestValidator("12345").compute_signature(URL, PARAMS)
    assert W.twilio_signature("12345", URL, PARAMS) == "GvWf1cFY/Q7PnoempGyD5oXAezc="


def test_signature_is_order_independent_and_tamper_evident():
    sig = W.twilio_signature("tok", URL, PARAMS)
    assert W.verify_signature("tok", URL, dict(reversed(list(PARAMS.items()))), sig)
    assert not W.verify_signature("tok", URL, {**PARAMS, "Digits": "9999"}, sig)
    assert not W.verify_signature("tok", URL + "x", PARAMS, sig)
    assert not W.verify_signature("other", URL, PARAMS, sig)
    assert not W.verify_signature("tok", URL, PARAMS, None)
    assert not W.verify_signature("tok", URL, PARAMS, "")


def test_twiml_escapes_xml():
    x = W.twiml("A & B <script>")
    assert "&amp;" in x and "&lt;script&gt;" in x and "<script>" not in x


def test_greeting_returns_menu_in_detected_language(demo):
    assert "I never submit" in W.handle_message("hi", demo)
    assert "சமர்ப்பிக்க மாட்டேன்" in W.handle_message("வணக்கம்", demo)
    assert "I never submit" in W.handle_message("", demo)


def test_message_gets_grounded_answer(demo):
    out = W.handle_message("Am I eligible for MUDRA?", demo)
    assert "Meets the criteria we have encoded" in out and "http" in out


def test_webhook_refuses_unsigned_by_default(demo):
    code, _, body = W.handle_webhook({"Body": "hi"}, None, URL, demo, env={})
    assert code == 403 and "refusing unsigned" in body


def test_webhook_dev_mode_allows_unsigned(demo):
    code, ctype, body = W.handle_webhook({"Body": "hi"}, None, URL, demo, env={"WA_ALLOW_UNSIGNED": "1"})
    assert code == 200 and ctype == "text/xml" and "<Message>" in body


def test_webhook_with_token_requires_valid_signature(demo):
    form = {"Body": "hi", "From": "whatsapp:+911"}
    env = {"TWILIO_AUTH_TOKEN": "tok", "WA_ALLOW_UNSIGNED": "1"}        # token wins over the dev flag
    assert W.handle_webhook(form, None, URL, demo, env=env)[0] == 403
    assert W.handle_webhook(form, "bad", URL, demo, env=env)[0] == 403
    good = W.twilio_signature("tok", URL, form)
    assert W.handle_webhook(form, good, URL, demo, env=env)[0] == 200


# ---- real HTTP round trip against the stdlib server
@pytest.fixture
def server():
    srv = make_server("127.0.0.1", 0, env={"WA_ALLOW_UNSIGNED": "1"})
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def post(url, data: bytes):
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def test_http_roundtrip_english_and_tamil(server):
    code, body = post(server + "/whatsapp", urllib.parse.urlencode({"Body": "What documents do I need for CGTMSE?"}).encode())
    assert code == 200 and "<Response>" in body and "Udyam" in body
    code, body = post(server + "/whatsapp", urllib.parse.urlencode({"Body": "எனக்கு MUDRA தகுதி உள்ளதா?"}).encode())
    assert code == 200 and "நாங்கள் குறியிட்ட" in body


def test_http_health_404_and_size_limit(server):
    with urllib.request.urlopen(server + "/health", timeout=10) as r:
        assert r.read() == b"ok"
    assert post(server + "/nope", b"x=1")[0] == 404
    assert post(server + "/whatsapp", b"Body=" + b"a" * 9000)[0] == 413


def test_http_refuses_unsigned_when_not_dev_mode():
    srv = make_server("127.0.0.1", 0, env={})
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        code, _ = post(f"http://127.0.0.1:{srv.server_address[1]}/whatsapp", b"Body=hi")
        assert code == 403
    finally:
        srv.shutdown()
