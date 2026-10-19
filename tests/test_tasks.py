from datetime import date

import pytest

from core import db
from core import tasks as T


def test_add_list_complete():
    tid = T.add_task("Collect certificate", due_date="2026-12-01", scheme_id="cgtmse")
    t = T.list_tasks()[0]
    assert t["title"] == "Collect certificate" and t["status"] == "open" and t["created_at"] and t["updated_at"]
    T.complete_task(tid)
    assert T.list_tasks()[0]["status"] == "done"
    assert T.list_tasks(include_done=False) == []


def test_empty_title_rejected():
    with pytest.raises(ValueError):
        T.add_task("   ")


def test_bad_date_rejected():
    with pytest.raises(ValueError):
        T.add_task("x", due_date="31-12-2026")


def test_bad_reminder_pref_rejected():
    with pytest.raises(ValueError):
        T.add_task("x", reminder_pref="telepathy")


def test_update_task_fields_and_validation():
    tid = T.add_task("a")
    T.update_task(tid, title="b", status="in_progress")
    t = T.list_tasks()[0]
    assert t["title"] == "b" and t["status"] == "in_progress"
    with pytest.raises(ValueError):
        T.update_task(tid, status="weird")
    with pytest.raises(ValueError):
        T.update_task(tid, id=5)


def test_overdue_logic():
    T.add_task("old", due_date="2020-01-01")
    T.add_task("future", due_date="2999-01-01")
    T.add_task("nodate")
    by = {t["title"]: t for t in T.list_tasks()}
    assert T.is_overdue(by["old"]) and not T.is_overdue(by["future"]) and not T.is_overdue(by["nodate"])
    T.complete_task(by["old"]["id"])
    assert not T.is_overdue(next(t for t in T.list_tasks() if t["title"] == "old"))


def test_tasks_sorted_by_due_date_nulls_last():
    T.add_task("none")
    T.add_task("late", due_date="2027-01-01")
    T.add_task("soon", due_date="2026-11-01")
    assert [t["title"] for t in T.list_tasks()] == ["soon", "late", "none"]


def test_application_tracking_upsert_and_validation():
    T.set_application("cgtmse", "preparing", "collect docs")
    T.set_application("cgtmse", "submitted_by_owner", "wait for bank")
    a = T.list_applications()["cgtmse"]
    assert a["status"] == "submitted_by_owner" and a["next_action"] == "wait for bank"
    with pytest.raises(ValueError):
        T.set_application("cgtmse", "auto_submitted")


def test_profile_persistence_roundtrip(demo):
    assert db.load_profile() is None
    db.save_profile(demo)
    assert db.load_profile()["fields"]["state"]["value"] == "Tamil Nadu"


def test_document_state_persistence():
    i = db.add_document("a.pdf", "udyam_certificate", "accepted", "text_extracted", "", [])
    assert db.confirmed_doc_types() == set() and db.pending_doc_types() == {"udyam_certificate"}
    db.set_document_confirmation(i, "confirmed")
    assert db.confirmed_doc_types() == {"udyam_certificate"}


def test_reset_all_clears_everything(demo):
    db.save_profile(demo)
    T.add_task("x")
    db.reset_all()
    assert db.load_profile() is None and T.list_tasks() == []
