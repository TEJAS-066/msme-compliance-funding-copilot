"""SQLite persistence (profile, documents, tasks, applications, review decisions).

WHY SQLite: zero setup, a single file, survives Streamlit reruns. Path comes from
MSME_DB_PATH so tests can use a temp file.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "app.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, doc_type TEXT,
  upload_status TEXT NOT NULL, extraction_status TEXT NOT NULL, message TEXT,
  findings_json TEXT, confirmation TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT DEFAULT '',
  scheme_id TEXT, due_date TEXT, status TEXT NOT NULL DEFAULT 'open',
  reminder_pref TEXT NOT NULL DEFAULT 'in_app', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS applications (
  scheme_id TEXT PRIMARY KEY, status TEXT NOT NULL, next_action TEXT DEFAULT '', updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS review_decisions (
  item_id TEXT PRIMARY KEY, decision TEXT NOT NULL, decided_at TEXT NOT NULL);
"""


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
    c.executescript(SCHEMA)
    try:
        yield c
        c.commit()
    finally:
        c.close()


def save_profile(profile: dict) -> None:
    with conn() as c:
        c.execute("INSERT INTO kv(key,value,updated_at) VALUES('profile',?,?) "
                  "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                  (json.dumps(profile, ensure_ascii=False), now()))


def load_profile() -> dict | None:
    with conn() as c:
        r = c.execute("SELECT value FROM kv WHERE key='profile'").fetchone()
    return json.loads(r["value"]) if r else None


def add_document(filename: str, doc_type: str, upload_status: str, extraction_status: str,
                 message: str, findings: list[dict]) -> int:
    with conn() as c:
        cur = c.execute("INSERT INTO documents(filename,doc_type,upload_status,extraction_status,message,findings_json,created_at) "
                        "VALUES(?,?,?,?,?,?,?)",
                        (filename, doc_type, upload_status, extraction_status, message,
                         json.dumps(findings, ensure_ascii=False), now()))
        return cur.lastrowid


def list_documents() -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["findings"] = json.loads(d.pop("findings_json") or "[]")
        out.append(d)
    return out


def set_document_confirmation(doc_id: int, confirmation: str) -> None:
    with conn() as c:
        c.execute("UPDATE documents SET confirmation=? WHERE id=?", (confirmation, doc_id))


def confirmed_doc_types() -> set[str]:
    """Doc types the OWNER has confirmed. Upload alone does not count."""
    with conn() as c:
        rows = c.execute("SELECT DISTINCT doc_type FROM documents WHERE confirmation='confirmed'").fetchall()
    return {r["doc_type"] for r in rows if r["doc_type"]}


def pending_doc_types() -> set[str]:
    with conn() as c:
        rows = c.execute("SELECT DISTINCT doc_type FROM documents WHERE confirmation='pending' "
                         "AND extraction_status='text_extracted'").fetchall()
    return {r["doc_type"] for r in rows if r["doc_type"]}


def reset_all() -> None:
    with conn() as c:
        for t in ("kv", "documents", "tasks", "applications", "review_decisions"):
            c.execute(f"DELETE FROM {t}")
