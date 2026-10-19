from core import checklist as C
from core import profile as P


def by_id(items, i):
    return next(x for x in items if x["id"] == i)


def test_all_missing_initially(demo):
    items = C.build_checklist("pmmy_mudra", demo, set())
    assert all(i["status"] in ("missing", "not_applicable") for i in items)


def test_upload_alone_is_needs_review_not_confirmed(demo):
    items = C.build_checklist("pmmy_mudra", demo, set(), {"udyam_certificate"})
    assert by_id(items, "udyam_cert")["status"] == "needs_review"


def test_confirmed_document_marks_item(demo):
    items = C.build_checklist("cgtmse", demo, {"udyam_certificate"})
    assert by_id(items, "udyam_cert")["status"] == "confirmed"


def test_gst_item_not_applicable_when_not_registered(demo):
    p = P.set_field(demo, "gst_status", "not_registered")
    assert by_id(C.build_checklist("pmmy_mudra", p, set()), "gst_cert")["status"] == "not_applicable"


def test_gst_item_applicable_when_registered(demo):
    p = P.set_field(demo, "gst_status", "registered")
    assert by_id(C.build_checklist("pmmy_mudra", p, set()), "gst_cert")["status"] == "missing"


def test_gst_applicability_unknown_is_flagged(demo):
    it = by_id(C.build_checklist("pmmy_mudra", demo, set()), "gst_cert")
    assert it["applicability_unknown"] is True


def test_different_schemes_have_different_lists(demo):
    a = {i["id"] for i in C.build_checklist("pmmy_mudra", demo, set())}
    b = {i["id"] for i in C.build_checklist("cgtmse", demo, set())}
    assert a != b


def test_unverified_items_are_labelled_unverified(demo):
    for i in C.build_checklist("cgtmse", demo, set()):
        assert i["verified"] is False


def test_summary_excludes_not_applicable(demo):
    p = P.set_field(demo, "gst_status", "not_registered")
    s = C.summarize(C.build_checklist("pmmy_mudra", p, {"lender_application_form"}))
    assert s["total"] == 2 and s["confirmed"] == 1


def test_unknown_scheme_raises(demo):
    import pytest
    with pytest.raises(KeyError):
        C.build_checklist("nope", demo, set())
