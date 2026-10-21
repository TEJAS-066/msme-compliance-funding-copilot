"""SQLite persistence (profile, documents, tasks, applications, review decisions).

WHY SQLite: zero setup, a single file, survives Streamlit reruns. Path comes from
MSME_DB_PATH so tests can use a temp file.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "app.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (owner TEXT NOT NULL DEFAULT 'local', key TEXT NOT NULL, value TEXT NOT NULL, updated_at TEXT NOT NULL,
  PRIMARY KEY (owner, key));
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL DEFAULT 'local', filename TEXT NOT NULL, doc_type TEXT,
  upload_status TEXT NOT NULL, extraction_status TEXT NOT NULL, message TEXT,
  findings_json TEXT, confirmation TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL DEFAULT 'local', title TEXT NOT NULL, description TEXT DEFAULT '',
  scheme_id TEXT, due_date TEXT, status TEXT NOT NULL DEFAULT 'open',
  reminder_pref TEXT NOT NULL DEFAULT 'in_app', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS applications (
  owner TEXT NOT NULL DEFAULT 'local', scheme_id TEXT NOT NULL, status TEXT NOT NULL, next_action TEXT DEFAULT '',
  updated_at TEXT NOT NULL, PRIMARY KEY (owner, scheme_id));
CREATE TABLE IF NOT EXISTS review_decisions (
  item_id TEXT PRIMARY KEY, decision TEXT NOT NULL, decided_at TEXT NOT NULL);
"""

# WHO owns the rows? Single-user laptop mode: always 'local'. Shared deployment (MSME_MULTIUSER=1): one random id per
# browser session, so visitors never see or overwrite each other's data. Thread-local because Streamlit runs each
# session in its own thread.
_ctx = threading.local()


def set_owner(owner: str) -> None:
    _ctx.owner = owner or "local"


def get_owner() -> str:
    return getattr(_ctx, "owner", "local")


def _migrate(c) -> None:
    """Upgrade a v0.1/v0.2 database (no owner column) in place; existing rows become owner 'local'."""
    cols = {r["name"] for r in c.execute("PRAGMA table_info(kv)").fetchall()}
    if cols and "owner" not in cols:
        c.executescript("""
            ALTER TABLE kv RENAME TO kv_old;
            CREATE TABLE kv (owner TEXT NOT NULL DEFAULT 'local', key TEXT NOT NULL, value TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY (owner, key));
            INSERT INTO kv (owner, key, value, updated_at) SELECT 'local', key, value, updated_at FROM kv_old;
            DROP TABLE kv_old;
            ALTER TABLE applications RENAME TO applications_old;
            CREATE TABLE applications (owner TEXT NOT NULL DEFAULT 'local', scheme_id TEXT NOT NULL, status TEXT NOT NULL, next_action TEXT DEFAULT '',
              updated_at TEXT NOT NULL, PRIMARY KEY (owner, scheme_id));
            INSERT INTO applications (owner, scheme_id, status, next_action, updated_at) SELECT 'local', scheme_id, status, next_action, updated_at FROM applications_old;
            DROP TABLE applications_old;
        """)
        for t in ("documents", "tasks"):
            c.execute(f"ALTER TABLE {t} ADD COLUMN owner TEXT NOT NULL DEFAULT 'local'")


def db_path() -> str:
    return os.environ.get("MSME_DB_PATH", DEFAULT_DB)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def conn():
    path = db_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kv'").fetchone():
        _migrate(c)
    c.executescript(SCHEMA)
    try:
        yield c
        c.commit()
    finally:
        c.close()


def save_profile(profile: dict) -> None:
    with conn() as c:
        c.execute("INSERT INTO kv(owner,key,value,updated_at) VALUES(?, 'profile', ?, ?) "
                  "ON CONFLICT(owner,key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                  (get_owner(), json.dumps(profile, ensure_ascii=False), now()))


def load_profile() -> dict | None:
    with conn() as c:
        r = c.execute("SELECT value FROM kv WHERE owner=? AND key='profile'", (get_owner(),)).fetchone()
    return json.loads(r["value"]) if r else None


def add_document(filename: str, doc_type: str, upload_status: str, extraction_status: str,
                 message: str, findings: list[dict]) -> int:
    with conn() as c:
        cur = c.execute("INSERT INTO documents(owner,filename,doc_type,upload_status,extraction_status,message,findings_json,created_at) "
                        "VALUES(?,?,?,?,?,?,?,?)",
                        (get_owner(), filename, doc_type, upload_status, extraction_status, message,
                         json.dumps(findings, ensure_ascii=False), now()))
        return cur.lastrowid


def list_documents() -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT * FROM documents WHERE owner=? ORDER BY id DESC", (get_owner(),)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["findings"] = json.loads(d.pop("findings_json") or "[]")
        out.append(d)
    return out


def set_document_confirmation(doc_id: int, confirmation: str) -> None:
    with conn() as c:
        c.execute("UPDATE documents SET confirmation=? WHERE id=? AND owner=?", (confirmation, doc_id, get_owner()))


def confirmed_doc_types() -> set[str]:
    """Doc types the OWNER has confirmed. Upload alone does not count."""
    with conn() as c:
        rows = c.execute("SELECT DISTINCT doc_type FROM documents WHERE owner=? AND confirmation='confirmed'", (get_owner(),)).fetchall()
    return {r["doc_type"] for r in rows if r["doc_type"]}


def pending_doc_types() -> set[str]:
    with conn() as c:
        rows = c.execute("SELECT DISTINCT doc_type FROM documents WHERE owner=? AND confirmation='pending' "
                         "AND extraction_status='text_extracted'", (get_owner(),)).fetchall()
    return {r["doc_type"] for r in rows if r["doc_type"]}


def reset_all() -> None:
    """Delete ONLY the current owner's data (never other visitors')."""
    with conn() as c:
        for t in ("kv", "documents", "tasks", "applications"):
            c.execute(f"DELETE FROM {t} WHERE owner=?", (get_owner(),))


def purge_inactive_owners(days: int = 7) -> int:
    """Shared deployments: delete every non-'local' owner whose profile was last saved more than `days` ago
    (and owners with no profile that have rows older than that). Returns the number of owners purged."""
    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    with conn() as c:
        owners = {r["owner"] for t in ("kv", "documents", "tasks", "applications")
                  for r in c.execute(f"SELECT DISTINCT owner FROM {t} WHERE owner != 'local'").fetchall()}
        stale = []
        for o in owners:
            last = max([r[0] or "" for r in (
                c.execute("SELECT MAX(updated_at) FROM kv WHERE owner=?", (o,)).fetchone(),
                c.execute("SELECT MAX(created_at) FROM documents WHERE owner=?", (o,)).fetchone(),
                c.execute("SELECT MAX(updated_at) FROM tasks WHERE owner=?", (o,)).fetchone(),
                c.execute("SELECT MAX(updated_at) FROM applications WHERE owner=?", (o,)).fetchone())])
            if last < cutoff:
                stale.append(o)
        for o in stale:
            for t in ("kv", "documents", "tasks", "applications"):
                c.execute(f"DELETE FROM {t} WHERE owner=?", (o,))
    return len(stale)
