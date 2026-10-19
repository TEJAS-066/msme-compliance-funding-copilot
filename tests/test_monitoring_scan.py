import json
from datetime import date

import pytest

from core.catalogue import get_catalogue
from services import monitoring as M


class R:
    def __init__(self, content=b"x", status=200, headers=None):
        self.content, self.status_code, self.headers = content, status, headers or {}


def test_normalize_ignores_markup_scripts_and_whitespace():
    a = b"<html><script>var t=1</script><body>  Limit is   10 crore <!-- c --></body></html>"
    b = b"<html><script>var t=999</script><body>Limit is 10 crore</body></html>"
    assert M.normalize(a) == M.normalize(b)
    assert M.normalize(b"<p>10 crore</p>") != M.normalize(b"<p>20 crore</p>")


def test_pdf_hashed_raw():
    assert M.normalize(b"%PDF-1.7 abc") == b"%PDF-1.7 abc"


def test_first_scan_is_baseline_second_is_quiet_then_change_detected():
    cat = get_catalogue()
    r1 = M.scan_sources(cat, get=lambda *a, **k: R(b"<p>v1</p>"), today=date(2026, 10, 18))
    assert len(r1["baseline"]) == len(cat["sources"]) and r1["changes"] == []
    r2 = M.scan_sources(cat, get=lambda *a, **k: R(b"<p>v1</p>"), hashes=r1["hashes"], today=date(2026, 10, 19))
    assert r2["changes"] == [] and r2["baseline"] == []
    r3 = M.scan_sources(cat, get=lambda *a, **k: R(b"<p>v2</p>"), hashes=r2["hashes"], today=date(2026, 10, 20))
    assert len(r3["changes"]) == len(cat["sources"])
    ch = next(c for c in r3["changes"] if c["source_id"] == "dcmsme_cgs")
    assert ch["schemes"] == ["cgtmse"] and ch["previous_checked"] == "2026-10-19"


def test_errors_are_recorded_and_old_hash_kept():
    cat = get_catalogue()
    base = M.scan_sources(cat, get=lambda *a, **k: R(b"v1"), today=date(2026, 10, 18))["hashes"]
    def flaky(url, **k):
        if "dcmsme" in url:
            raise TimeoutError()
        if "pib" in url:
            return R(status=503)
        return R(b"v1")
    r = M.scan_sources(cat, get=flaky, hashes=base, today=date(2026, 10, 19))
    errs = {e["source_id"]: e["error"] for e in r["errors"]}
    assert errs["dcmsme_cgs"] == "TimeoutError" and errs["pib_pmmy_2024"] == "HTTP 503"
    assert r["hashes"]["dcmsme_cgs"] == base["dcmsme_cgs"] and r["changes"] == []


def test_queue_items_are_pending_and_clearly_flagged():
    items = M.changes_to_queue_items([{"source_id": "dcmsme_cgs", "title": "DC-MSME", "url": "https://x", "schemes": ["cgtmse"],
                                      "previous_checked": "2026-10-18", "today": "2026-10-19"}])
    i = items[0]
    assert i["status"] == "pending" and i["kind"] == "SOURCE_CHANGED" and i["id"] == "chg-dcmsme_cgs-2026-10-19"
    assert "BEFORE anyone is notified" in i["detail"] and "false alarm" in i["detail"]


def test_append_queue_dedupes(tmp_path):
    q = tmp_path / "q.json"
    q.write_text(json.dumps({"_label": "x", "items": [{"id": "a"}]}))
    assert M.append_queue([{"id": "a"}, {"id": "b"}], str(q)) == 1
    assert M.append_queue([{"id": "b"}], str(q)) == 0
    assert [i["id"] for i in json.loads(q.read_text())["items"]] == ["a", "b"]


def test_detected_change_needs_admin_approval_before_notification(tmp_path, monkeypatch):
    q = tmp_path / "q.json"
    q.write_text(json.dumps({"items": M.changes_to_queue_items([{"source_id": "s", "title": "T", "url": "u", "schemes": [], "previous_checked": "a", "today": "b"}])}))
    monkeypatch.setattr(M, "QUEUE_PATH", str(q))
    assert M.notifiable_items() == []
    M.decide("chg-s-b", "approved")
    assert [i["id"] for i in M.notifiable_items()] == ["chg-s-b"]
