"""Shared-deployment safety: visitors must never see, edit or delete each other's data."""
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from streamlit.testing.v1 import AppTest

from core import db
from core import profile as P
from core import tasks as T
import os

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


@pytest.fixture(autouse=True)
def back_to_local():
    yield
    db.set_owner("local")


def as_owner(o):
    db.set_owner(o)


def test_profiles_documents_tasks_applications_are_private(demo):
    as_owner("alice"); db.save_profile(demo); T.add_task("alice task"); T.set_application("cgtmse", "preparing")
    db.add_document("a.pdf", "udyam_certificate", "accepted", "text_extracted", "", [])
    as_owner("bob")
    assert db.load_profile() is None and T.list_tasks() == [] and T.list_applications() == {}
    assert db.list_documents() == [] and db.confirmed_doc_types() == set()
    as_owner("alice")
    assert db.load_profile() is not None and len(T.list_tasks()) == 1 and "cgtmse" in T.list_applications()


def test_cannot_edit_or_complete_another_owners_task():
    as_owner("alice"); tid = T.add_task("secret")
    as_owner("bob"); T.complete_task(tid); T.update_task(tid, title="hacked")
    as_owner("alice")
    t = T.list_tasks()[0]
    assert t["title"] == "secret" and t["status"] == "open"


def test_cannot_confirm_another_owners_document():
    as_owner("alice"); i = db.add_document("a.pdf", "udyam_certificate", "accepted", "text_extracted", "", [])
    as_owner("bob"); db.set_document_confirmation(i, "confirmed")
    as_owner("alice"); assert db.confirmed_doc_types() == set()


def test_reset_only_clears_own_data(demo):
    as_owner("alice"); db.save_profile(demo); T.add_task("a")
    as_owner("bob"); db.save_profile(demo); T.add_task("b")
    db.reset_all()
    assert db.load_profile() is None and T.list_tasks() == []
    as_owner("alice"); assert db.load_profile() is not None and [t["title"] for t in T.list_tasks()] == ["a"]


def test_purge_removes_only_stale_non_local_owners(demo):
    as_owner("local"); db.save_profile(demo)
    as_owner("old"); db.save_profile(demo); T.add_task("x")
    as_owner("fresh"); db.save_profile(demo)
    old = (datetime.now(timezone.utc) - timedelta(days=9)).isoformat(timespec="seconds")
    with db.conn() as c:
        for t, col in (("kv", "updated_at"), ("tasks", "updated_at")):
            c.execute(f"UPDATE {t} SET {col}=? WHERE owner='old'", (old,))
    assert db.purge_inactive_owners(7) == 1
    as_owner("old"); assert db.load_profile() is None and T.list_tasks() == []
    as_owner("fresh"); assert db.load_profile() is not None
    as_owner("local"); assert db.load_profile() is not None


def test_old_schema_database_is_migrated_in_place(tmp_path, monkeypatch):
    path = tmp_path / "old.db"
    c = sqlite3.connect(path)
    c.executescript("""
        CREATE TABLE kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE documents (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, doc_type TEXT, upload_status TEXT NOT NULL,
          extraction_status TEXT NOT NULL, message TEXT, findings_json TEXT, confirmation TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
        CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT DEFAULT '', scheme_id TEXT, due_date TEXT,
          status TEXT NOT NULL DEFAULT 'open', reminder_pref TEXT NOT NULL DEFAULT 'in_app', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE applications (scheme_id TEXT PRIMARY KEY, status TEXT NOT NULL, next_action TEXT DEFAULT '', updated_at TEXT NOT NULL);
        CREATE TABLE review_decisions (item_id TEXT PRIMARY KEY, decision TEXT NOT NULL, decided_at TEXT NOT NULL);
        INSERT INTO kv VALUES ('profile', '{"fields": {"state": {"value": "Kerala", "status": "known", "source": "user"}}}', '2026-10-01T00:00:00');
        INSERT INTO tasks (title, created_at, updated_at) VALUES ('legacy task', 'x', 'x');
        INSERT INTO applications VALUES ('cgtmse', 'preparing', 'call bank', 'x');
        INSERT INTO documents (filename, doc_type, upload_status, extraction_status, created_at, confirmation)
          VALUES ('u.pdf', 'udyam_certificate', 'accepted', 'text_extracted', 'x', 'confirmed');
    """)
    c.commit(); c.close()
    monkeypatch.setenv("MSME_DB_PATH", str(path))
    as_owner("local")
    assert db.load_profile()["fields"]["state"]["value"] == "Kerala"
    assert [t["title"] for t in T.list_tasks()] == ["legacy task"]
    assert T.list_applications()["cgtmse"]["next_action"] == "call bank"
    assert db.confirmed_doc_types() == {"udyam_certificate"}
    as_owner("someone-else"); assert db.load_profile() is None
    as_owner("local"); T.add_task("new after migration")       # still writable
    assert len(T.list_tasks()) == 2


# ---------------- through the real UI ----------------
def boot(monkeypatch, multiuser):
    monkeypatch.setenv("MSME_MULTIUSER", "1" if multiuser else "0")
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception
    return at


def metric(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_two_browser_sessions_do_not_share_data_in_shared_mode(monkeypatch):
    a = boot(monkeypatch, True)
    a.button(key="btn_load_demo").click().run()
    assert metric(a, "Profile fields known") != f"0/{len(P.FIELDS)}"
    b = boot(monkeypatch, True)
    assert metric(b, "Profile fields known") == f"0/{len(P.FIELDS)}"
    b.button(key="btn_reset").click().run()                      # B resetting must not touch A
    a2 = a.run()
    assert metric(a2, "Profile fields known") != f"0/{len(P.FIELDS)}"
    assert any("Shared demo" in c.value for c in a2.caption)


def test_local_mode_keeps_one_shared_user(monkeypatch):
    a = boot(monkeypatch, False)
    a.button(key="btn_load_demo").click().run()
    b = boot(monkeypatch, False)                                 # same laptop, same 'local' owner (webhook relies on this)
    assert metric(b, "Profile fields known") != f"0/{len(P.FIELDS)}"


def test_admin_page_locked_without_pin_in_shared_mode(monkeypatch):
    monkeypatch.delenv("ADMIN_PIN", raising=False)
    at = boot(monkeypatch, True)
    at.sidebar.radio(key="nav").set_value("nav_admin").run()
    assert not at.exception and any("disabled" in w.value for w in at.warning)
    assert not [b for b in at.button if b.key and b.key.startswith("ap_")]


def test_admin_pin_flow(monkeypatch):
    monkeypatch.setenv("ADMIN_PIN", "4821")
    at = boot(monkeypatch, True)
    at.sidebar.radio(key="nav").set_value("nav_admin").run()
    at.text_input(key="adm_pin_input").set_value("0000").run()
    assert any("Wrong PIN" in e.value for e in at.error)
    assert not [b for b in at.button if b.key and b.key.startswith("ap_")]
    at.text_input(key="adm_pin_input").set_value("4821").run()
    assert not at.exception
    assert [b for b in at.button if b.key and b.key.startswith("ap_")]          # approve buttons now visible


def test_admin_always_open_in_local_mode(monkeypatch):
    at = boot(monkeypatch, False)
    at.sidebar.radio(key="nav").set_value("nav_admin").run()
    assert [b for b in at.button if b.key and b.key.startswith("ap_")]
