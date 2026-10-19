import re
from datetime import date

from core import profile as P
from services import alerts as A
from services import report as R

TA = re.compile("[\u0b80-\u0bff]")
TODAY = date(2026, 10, 18)


def mk(demo, tasks=(), docs=(), updates=(), lang="en", confirmed=frozenset()):
    return A.build_alerts(demo, set(confirmed), list(docs), list(tasks), list(updates), lang, today=TODAY)


def test_demo_gets_scheme_and_missing_doc_alerts(demo):
    kinds = [a.kind for a in mk(demo)]
    assert kinds.count("scheme_match") == 2 and "missing_docs" in kinds


def test_alerts_sorted_by_severity(demo):
    tasks = [{"title": "Old", "due_date": "2026-10-01", "status": "open"}]
    sev = [a.severity for a in mk(demo, tasks)]
    assert sev == sorted(sev, key={"action": 0, "warn": 1, "info": 2}.get)
    assert sev[0] == "action"


def test_task_windows(demo):
    tasks = [{"title": "soon", "due_date": "2026-10-25", "status": "open"},
             {"title": "far", "due_date": "2026-12-25", "status": "open"},
             {"title": "done", "due_date": "2026-10-01", "status": "done"},
             {"title": "nodate", "due_date": None, "status": "open"}]
    texts = " ".join(a.text for a in mk(demo, tasks))
    assert "soon" in texts and "far" not in texts and "done" not in texts and "nodate" not in texts


def test_pending_document_needs_review_alert(demo):
    docs = [{"filename": "u.pdf", "confirmation": "pending", "extraction_status": "text_extracted"},
            {"filename": "bad.pdf", "confirmation": "pending", "extraction_status": "corrupt"}]
    texts = " ".join(a.text for a in mk(demo, docs=docs))
    assert "u.pdf" in texts and "bad.pdf" not in texts


def test_class_mismatch_alert(demo):
    p = P.set_field(demo, "enterprise_class_declared", "small")
    assert any(a.kind == "class_mismatch" for a in A.build_alerts(p, set(), [], [], [], "en", today=TODAY))


def test_only_approved_updates_alert(demo):
    assert any(a.kind == "catalogue_update" for a in mk(demo, updates=[{"title": "Limit changed"}]))
    assert not any(a.kind == "catalogue_update" for a in mk(demo))


def test_tamil_alerts_and_preview(demo):
    a = mk(demo, lang="ta")[0]
    assert TA.search(a.text)
    pv = A.whatsapp_preview(a, "ta")
    assert "முன்னோட்டம் மட்டும்" in pv and a.text in pv
    assert "PREVIEW ONLY" in A.whatsapp_preview(mk(demo)[0], "en")


def test_empty_profile_has_no_scheme_alerts(empty):
    assert [a for a in A.build_alerts(empty, set(), [], [], [], "en", today=TODAY) if a.kind == "scheme_match"] == []


# ---- report
def test_report_has_sources_disclaimer_and_demo_label(demo):
    r = R.readiness_report(demo, set(), "en", today=TODAY)
    assert "READINESS REPORT" in r and "DEMO MODE" in r and "NOT an application" in r
    assert "https://dcmsme.gov.in" in r and "https://static.pib.gov.in" in r
    assert "₹8,00,000" in r and "Not provided / unknown" in r
    assert "2026-10-18" in r


def test_report_never_claims_approval(demo):
    low = R.readiness_report(demo, set(), "en").lower()
    assert "you are approved" not in low and "guaranteed" not in low.replace("not an application, an approval or a guarantee", "")


def test_report_tamil(demo):
    r = R.readiness_report(demo, set(), "ta")
    assert "விண்ணப்பத் தயார்நிலை அறிக்கை" in r and TA.search(r)


def test_report_for_empty_profile_does_not_crash(empty):
    r = R.readiness_report(empty, set(), "en")
    assert "More information required" in r


def test_report_reflects_confirmed_documents(demo):
    r1 = R.readiness_report(demo, set(), "en")
    r2 = R.readiness_report(demo, {"udyam_certificate"}, "en")
    assert r1 != r2 and "Confirmed" in r2


def test_report_lists_open_questions(demo):
    assert "Which exact KYC" in R.readiness_report(demo, set(), "en")


def test_report_drops_demo_banner_for_real_profile(demo):
    p = P.set_field(demo, "business_name", "My Unit")
    assert "DEMO MODE" not in R.readiness_report(p, set(), "en")
