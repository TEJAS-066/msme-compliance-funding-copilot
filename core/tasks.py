"""Tasks, application tracking and reminder PREVIEWS.

Three different things, never conflated:
  saved reminder   -> a row with a due date + preference (this module)
  scheduled        -> NOT implemented in this starter (needs a scheduler)
  delivered        -> only true if services/notifications returns SENT
"""
from __future__ import annotations

from datetime import date

from core.db import conn, get_owner, now

TASK_STATUSES = ("open", "in_progress", "done")
APP_STATUSES = ("not_started", "preparing", "submitted_by_owner", "under_review", "approved", "rejected")
REMINDER_PREFS = ("none", "in_app", "whatsapp_preview", "sms_preview")


def add_task(title: str, description: str = "", scheme_id: str | None = None,
             due_date: str | None = None, reminder_pref: str = "in_app") -> int:
    title = (title or "").strip()
    if not title:
        raise ValueError("title is required")
    if due_date:
        date.fromisoformat(due_date)
    if reminder_pref not in REMINDER_PREFS:
        raise ValueError("bad reminder_pref")
    with conn() as c:
        cur = c.execute("INSERT INTO tasks(owner,title,description,scheme_id,due_date,status,reminder_pref,created_at,updated_at) "
                        "VALUES(?,?,?,?,?,?,?,?,?)",
                        (get_owner(), title, description, scheme_id, due_date, "open", reminder_pref, now(), now()))
        return cur.lastrowid


def update_task(task_id: int, **fields) -> None:
    allowed = {"title", "description", "scheme_id", "due_date", "status", "reminder_pref"}
    bad = set(fields) - allowed
    if bad:
        raise ValueError(f"cannot update {bad}")
    if "status" in fields and fields["status"] not in TASK_STATUSES:
        raise ValueError("bad status")
    if fields.get("due_date"):
        date.fromisoformat(fields["due_date"])
    if not fields:
        return
    sets = ", ".join(f"{k}=?" for k in fields)
    with conn() as c:
        c.execute(f"UPDATE tasks SET {sets}, updated_at=? WHERE id=? AND owner=?", (*fields.values(), now(), task_id, get_owner()))


def complete_task(task_id: int) -> None:
    update_task(task_id, status="done")


def list_tasks(include_done: bool = True) -> list[dict]:
    q = "SELECT * FROM tasks WHERE owner=?" + ("" if include_done else " AND status!='done'") + \
        " ORDER BY (due_date IS NULL), due_date, id"
    with conn() as c:
        return [dict(r) for r in c.execute(q, (get_owner(),)).fetchall()]


def is_overdue(task: dict, today: date | None = None) -> bool:
    today = today or date.today()
    return bool(task.get("due_date")) and task["status"] != "done" and date.fromisoformat(task["due_date"]) < today


def set_application(scheme_id: str, status: str, next_action: str = "") -> None:
    if status not in APP_STATUSES:
        raise ValueError("bad status")
    with conn() as c:
        c.execute("INSERT INTO applications(owner,scheme_id,status,next_action,updated_at) VALUES(?,?,?,?,?) "
                  "ON CONFLICT(owner,scheme_id) DO UPDATE SET status=excluded.status, next_action=excluded.next_action, updated_at=excluded.updated_at",
                  (get_owner(), scheme_id, status, next_action, now()))


def list_applications() -> dict[str, dict]:
    with conn() as c:
        return {r["scheme_id"]: dict(r) for r in c.execute("SELECT * FROM applications WHERE owner=?", (get_owner(),)).fetchall()}
