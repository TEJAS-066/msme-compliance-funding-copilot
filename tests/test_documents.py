import os

import pytest

from core import documents as D
from core import profile as P

S = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")


def sample(name):
    with open(os.path.join(S, name), "rb") as f:
        return f.read()


def test_unsupported_type_rejected():
    r = D.extract_text(b"x", "virus.exe")
    assert r.upload_status == "rejected" and r.extraction_status == "skipped"


def test_empty_file_rejected():
    assert D.extract_text(b"", "a.pdf").upload_status == "rejected"


def test_oversize_rejected():
    assert D.extract_text(b"a" * (D.MAX_BYTES + 1), "a.txt").upload_status == "rejected"


def test_corrupt_pdf_handled_gracefully():
    r = D.extract_text(sample("sample_corrupt.pdf"), "sample_corrupt.pdf")
    assert r.upload_status == "accepted" and r.extraction_status == "corrupt"


def test_scan_without_text_layer_is_not_a_fake_success():
    r = D.extract_text(sample("sample_scan_no_text_layer.pdf"), "x.pdf")
    assert r.extraction_status in ("ocr_not_available", "empty") and r.text == ""     # empty = OCR ran, saw nothing


def test_scan_reports_ocr_unavailable_when_ocr_missing(monkeypatch):
    monkeypatch.setattr(D, "pdf_ocr_available", lambda: False)
    r = D.extract_text(sample("sample_udyam_scanned.pdf"), "x.pdf")
    assert r.extraction_status == "ocr_not_available" and r.text == "" and "not installed" in r.message


def test_upload_and_extraction_are_separate_states():
    r = D.extract_text(sample("sample_corrupt.pdf"), "x.pdf")
    assert r.upload_status == "accepted" and r.extraction_status != "text_extracted"


def test_image_without_ocr_reports_honestly(monkeypatch):
    monkeypatch.setattr(D, "ocr_available", lambda: False)
    r = D.extract_text(b"\x89PNG....", "scan.png")
    assert r.extraction_status == "ocr_not_available"


def test_txt_extraction_and_empty_txt():
    assert D.extract_text(b"hello", "a.txt").extraction_status == "text_extracted"
    assert D.extract_text(b"   \n ", "a.txt").extraction_status == "empty"


def test_udyam_sample_fields():
    r = D.extract_text(sample("sample_udyam_lakshmi.pdf"), "u.pdf")
    got = {c.field: c.value for c in D.extract_fields(r.text)}
    assert got["udyam_number"] == "UDYAM-TN-02-0000123"
    assert got["enterprise_class_declared"] == "micro" and got["entity_type"] == "proprietorship"
    assert D.detect_doc_type(r.text) == "udyam_certificate"


def test_only_supported_fields_are_extracted():
    assert D.extract_fields("Some random letter with no registration data.") == []


def test_gstin_checksum():
    assert D.gstin_valid("27AAPFU0939F1ZV")                     # widely-cited sample GSTIN
    assert not D.gstin_valid("27AAPFU0939F1ZX")                 # wrong check char
    assert not D.gstin_valid("12345")


def test_bad_checksum_gstin_is_flagged_not_trusted():
    cands = D.extract_fields("GST REGISTRATION CERTIFICATE\nGSTIN: 33ABCDE1234F1ZX")
    g = next(c for c in cands if c.field == "gstin")
    assert g.match_quality != "format_validated" and "INVALID" in g.note
    assert not any(c.field == "gst_status" for c in cands)       # no implied status from a bad GSTIN


def test_compare_new_match_mismatch(demo):
    cands = [D.Candidate("district", "Tiruppur", "label_match"), D.Candidate("state", "Kerala", "label_match"),
             D.Candidate("udyam_number", "UDYAM-TN-02-0000123", "format_validated")]
    kinds = {f.field: f.kind for f in D.compare_with_profile(cands, demo) if not f.advisory}
    assert kinds == {"district": "match", "state": "mismatch", "udyam_number": "new"}


def test_gstin_state_crosscheck_flags_advisory(demo):
    r = D.extract_text(sample("sample_gst_state_mismatch.pdf"), "g.pdf")
    adv = [f for f in D.compare_with_profile(D.extract_fields(r.text), demo) if f.advisory]
    assert adv and "Karnataka" in adv[0].note


def test_class_mismatch_crosscheck(demo):
    r = D.extract_text(sample("sample_udyam_class_mismatch.pdf"), "u.pdf")
    adv = [f for f in D.compare_with_profile(D.extract_fields(r.text), demo) if f.advisory]
    assert any("compute to micro" in f.note for f in adv)


def test_accept_fills_unknown_field(demo):
    p = D.apply_decisions(demo, [{"field": "udyam_number", "value": "UDYAM-TN-02-0000123", "action": "accept"}], "u.pdf")
    assert P.get(p, "udyam_number") == "UDYAM-TN-02-0000123"
    assert p["fields"]["udyam_number"]["source"] == "document:u.pdf"


def test_accept_never_silently_overwrites(demo):
    p = D.apply_decisions(demo, [{"field": "state", "value": "Kerala", "action": "accept"}], "u.pdf")
    assert P.get(p, "state") == "Tamil Nadu"


def test_overwrite_requires_explicit_action(demo):
    p = D.apply_decisions(demo, [{"field": "state", "value": "Kerala", "action": "overwrite"}], "u.pdf")
    assert P.get(p, "state") == "Kerala"


def test_reject_changes_nothing(demo):
    p = D.apply_decisions(demo, [{"field": "udyam_number", "value": "UDYAM-TN-02-0000123", "action": "reject"}], "u.pdf")
    assert P.get(p, "udyam_number") is None


# ---------------- real OCR (skipped automatically on machines without tesseract) ----------------
needs_ocr = pytest.mark.skipif(not D.pdf_ocr_available(), reason="tesseract/pytesseract/pypdfium2 not installed")


@needs_ocr
def test_ocr_reads_png():
    r = D.extract_text(sample("sample_udyam_scan.png"), "s.png")
    assert r.extraction_status == "text_extracted" and r.method == "ocr" and "OCR" in r.message
    got = {c.field: c.value for c in D.extract_fields(r.text, r.method)}
    assert got["udyam_number"] == "UDYAM-TN-02-0000123" and got["state"] == "Tamil Nadu"


@needs_ocr
def test_ocr_reads_scanned_pdf():
    r = D.extract_text(sample("sample_udyam_scanned.pdf"), "s.pdf")
    assert r.extraction_status == "text_extracted" and r.method == "ocr"
    assert D.detect_doc_type(r.text) == "udyam_certificate"


@needs_ocr
def test_ocr_blank_image_is_empty_not_success():
    from PIL import Image
    import io
    buf = io.BytesIO(); Image.new("RGB", (300, 200), "white").save(buf, "PNG")
    assert D.extract_text(buf.getvalue(), "blank.png").extraction_status == "empty"


@needs_ocr
def test_ocr_corrupt_image_handled():
    assert D.extract_text(b"\x89PNG not an image", "bad.png").extraction_status == "corrupt"


def test_ocr_fields_are_downgraded_but_checksum_ids_keep_strength():
    text = "UDYAM REGISTRATION CERTIFICATE\nUDYAM REGISTRATION NUMBER: UDYAM-TN-02-0000123\nSTATE: Tamil Nadu"
    by = {c.field: c for c in D.extract_fields(text, "ocr")}
    assert by["state"].match_quality == "ocr_read" and by["state"].note.startswith("Read by OCR")
    assert by["udyam_number"].match_quality == "format_validated"
    plain = {c.field: c for c in D.extract_fields(text)}
    assert plain["state"].match_quality == "label_match"
