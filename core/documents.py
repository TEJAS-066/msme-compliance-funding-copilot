"""Document upload -> extraction -> candidate fields -> user confirmation.

THREE SEPARATE STATES (never conflate them):
  1. upload_status      accepted | rejected          (file type/size ok?)
  2. extraction_status  text_extracted | empty | corrupt | ocr_not_available | unsupported
  3. confirmation       pending | confirmed | rejected   (per field, by the human)

Pattern/format matches are NOT verification against any government portal.
"""
from __future__ import annotations

import io
import re
import shutil
from dataclasses import dataclass, field, asdict

from core import profile as P

MAX_BYTES = 5 * 1024 * 1024
TEXT_EXT = {".txt"}
PDF_EXT = {".pdf"}
IMG_EXT = {".png", ".jpg", ".jpeg"}
ALLOWED_EXT = TEXT_EXT | PDF_EXT | IMG_EXT

# GST state codes (subset we are sure about; extend from the official GST code list)
GST_STATE_CODES = {
    "07": "Delhi", "24": "Gujarat", "27": "Maharashtra", "29": "Karnataka",
    "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry", "36": "Telangana", "37": "Andhra Pradesh",
}
UDYAM_STATE_CODES = {"TN": "Tamil Nadu", "KA": "Karnataka", "KL": "Kerala", "AP": "Andhra Pradesh",
                     "TS": "Telangana", "MH": "Maharashtra", "GJ": "Gujarat", "DL": "Delhi", "PY": "Puducherry"}

_CH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GSTIN_RE = re.compile(r"\b(\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z])\b")
UDYAM_RE = re.compile(r"\b(UDYAM-[A-Z]{2}-\d{2}-\d{7})\b")


def gstin_check_char(first14: str) -> str:
    s = 0
    for i, c in enumerate(first14):
        p = _CH.index(c) * (1 if i % 2 == 0 else 2)
        s += p // 36 + p % 36
    return _CH[(36 - s % 36) % 36]


def gstin_valid(g: str) -> bool:
    return bool(GSTIN_RE.fullmatch(g)) and gstin_check_char(g[:14]) == g[14]


@dataclass
class ExtractionResult:
    upload_status: str            # accepted | rejected
    extraction_status: str        # text_extracted | empty | corrupt | ocr_not_available | unsupported | skipped
    text: str = ""
    message: str = ""
    method: str = ""              # text_layer | ocr


@dataclass
class Candidate:
    field: str
    value: str
    match_quality: str            # format_validated | label_match
    snippet: str = ""
    note: str = ""


@dataclass
class Finding:
    field: str
    proposed: str
    current: str | None
    kind: str                     # new | match | mismatch
    match_quality: str
    note: str = ""
    advisory: bool = False        # True = cross-check WARNING for human review; not an apply-able field


OCR_MAX_PAGES = 3
OCR_NOTE = "Read with OCR - characters can be misread. Check every value before you confirm."


def ocr_available() -> bool:
    """Images need: tesseract binary + pytesseract + Pillow."""
    if not shutil.which("tesseract"):
        return False
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
        return True
    except ImportError:
        return False


def pdf_ocr_available() -> bool:
    """Scanned PDFs additionally need pypdfium2 to turn pages into images."""
    if not ocr_available():
        return False
    try:
        import pypdfium2  # noqa: F401
        return True
    except ImportError:
        return False


def _ocr_lang() -> str:
    import pytesseract
    try:
        langs = set(pytesseract.get_languages(config=""))
    except Exception:
        return "eng"
    return "eng+tam" if "tam" in langs else "eng"


def _ocr_image(img) -> str:
    import pytesseract
    return pytesseract.image_to_string(img, lang=_ocr_lang(), timeout=40).strip()


def _ocr_pdf(data: bytes) -> str:
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(data)
    parts = []
    for i in range(min(len(pdf), OCR_MAX_PAGES)):
        img = pdf[i].render(scale=2.5).to_pil().convert("L")
        parts.append(_ocr_image(img))
    return "\n".join(p for p in parts if p).strip()


def extract_text(data: bytes, filename: str) -> ExtractionResult:
    name = (filename or "").lower()
    ext = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    if ext not in ALLOWED_EXT:
        return ExtractionResult("rejected", "skipped", message=f"File type '{ext or 'none'}' is not supported (allowed: pdf, txt, png, jpg).")
    if len(data) == 0:
        return ExtractionResult("rejected", "skipped", message="The file is empty (0 bytes).")
    if len(data) > MAX_BYTES:
        return ExtractionResult("rejected", "skipped", message=f"File is larger than {MAX_BYTES // (1024*1024)} MB.")

    if ext in TEXT_EXT:
        text = data.decode("utf-8", errors="replace").strip()
        if not text:
            return ExtractionResult("accepted", "empty", message="No text found in the file.")
        return ExtractionResult("accepted", "text_extracted", text=text)

    if ext in PDF_EXT:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                return ExtractionResult("accepted", "corrupt", message="The PDF is password-protected; it cannot be read.")
            text = "\n".join((pg.extract_text() or "") for pg in reader.pages).strip()
        except Exception as e:  # pypdf raises several error types for broken files
            return ExtractionResult("accepted", "corrupt", message=f"The PDF could not be read ({type(e).__name__}).")
        if text:
            return ExtractionResult("accepted", "text_extracted", text=text, method="text_layer")
        if not pdf_ocr_available():
            return ExtractionResult("accepted", "ocr_not_available",
                                    message="No embedded text found - this looks like a scan, and OCR is not installed in this build.")
        try:
            text = _ocr_pdf(data)
        except Exception as e:
            return ExtractionResult("accepted", "corrupt", message=f"OCR failed on this PDF ({type(e).__name__}).")
        if not text:
            return ExtractionResult("accepted", "empty", message="OCR ran but found no readable text.", method="ocr")
        return ExtractionResult("accepted", "text_extracted", text=text, message=OCR_NOTE, method="ocr")

    # images
    if not ocr_available():
        return ExtractionResult("accepted", "ocr_not_available",
                                message="Image saved, but OCR is not installed/enabled, so nothing was extracted. Use a text-based PDF for the demo.")
    try:
        from PIL import Image
        text = _ocr_image(Image.open(io.BytesIO(data)).convert("L"))
    except Exception as e:
        return ExtractionResult("accepted", "corrupt", message=f"The image could not be processed ({type(e).__name__}).")
    if not text:
        return ExtractionResult("accepted", "empty", message="OCR ran but found no text.", method="ocr")
    return ExtractionResult("accepted", "text_extracted", text=text, message=OCR_NOTE, method="ocr")


def detect_doc_type(text: str) -> str:
    t = text.upper()
    if "UDYAM REGISTRATION CERTIFICATE" in t or UDYAM_RE.search(t):
        return "udyam_certificate"
    if "GST" in t and GSTIN_RE.search(t):
        return "gst_certificate"
    return "unknown"


def _label(text: str, label: str) -> str | None:
    m = re.search(rf"(?im)^\s*{label}\s*[:\-]\s*(.+?)\s*$", text)
    return m.group(1).strip() if m else None


_ORG_MAP = {"proprietary": "proprietorship", "proprietorship": "proprietorship", "partnership": "partnership",
            "llp": "llp", "private limited": "private_limited", "public limited": "public_limited"}


def extract_fields(text: str, method: str = "text_layer") -> list[Candidate]:
    """Extract ONLY what the text supports. Nothing is guessed.
    method="ocr" downgrades label-based reads (OCR can misread letters); checksum-validated IDs keep their strength."""
    out: list[Candidate] = []
    m = UDYAM_RE.search(text.upper())
    if m:
        out.append(Candidate("udyam_number", m.group(1), "format_validated", m.group(1),
                             "Format matches Udyam pattern; NOT verified on the Udyam portal."))
        out.append(Candidate("udyam_status", "registered", "format_validated", m.group(1), "Implied by a Udyam-format number."))
    for lbl, fld in (("NAME OF ENTERPRISE", "business_name"), ("DISTRICT", "district"), ("STATE", "state")):
        v = _label(text, lbl)
        if v:
            out.append(Candidate(fld, v, "label_match", f"{lbl}: {v}"))
    v = _label(text, "TYPE OF ENTERPRISE")
    if v and v.strip().lower() in ("micro", "small", "medium"):
        out.append(Candidate("enterprise_class_declared", v.strip().lower(), "label_match", f"TYPE OF ENTERPRISE: {v}"))
    v = _label(text, "TYPE OF ORGANISATION")
    if v and v.strip().lower() in _ORG_MAP:
        out.append(Candidate("entity_type", _ORG_MAP[v.strip().lower()], "label_match", f"TYPE OF ORGANISATION: {v}"))
    v = _label(text, "MAJOR ACTIVITY")
    if v and v.strip().lower() in ("manufacturing", "services", "trading"):
        out.append(Candidate("activity", v.strip().lower(), "label_match", f"MAJOR ACTIVITY: {v}"))
    g = GSTIN_RE.search(text.upper())
    if g:
        ok = gstin_valid(g.group(1))
        out.append(Candidate("gstin", g.group(1), "format_validated" if ok else "label_match", g.group(1),
                             "Format and checksum are valid; NOT verified on the GST portal." if ok
                             else "Format found but the checksum is INVALID - possible typo or fake. Review carefully."))
        if ok:
            out.append(Candidate("gst_status", "registered", "format_validated", g.group(1), "Implied by a valid-format GSTIN."))
    if method == "ocr":
        for c in out:
            if c.match_quality == "label_match":
                c.match_quality = "ocr_read"
            c.note = ("Read by OCR. " + c.note).strip()
    return out


def compare_with_profile(cands: list[Candidate], profile: dict, cat: dict | None = None) -> list[Finding]:
    findings: list[Finding] = []
    for c in cands:
        cur = P.get(profile, c.field)
        cur_s = None if cur is None else str(cur)
        if cur_s is None:
            kind = "new"
        elif cur_s.strip().lower() == c.value.strip().lower():
            kind = "match"
        else:
            kind = "mismatch"
        findings.append(Finding(c.field, c.value, cur_s, kind, c.match_quality, c.note))

    # cross-document consistency checks (flag for HUMAN review; never auto-resolve)
    state = P.get(profile, "state")
    for c in cands:
        if c.field == "gstin" and len(c.value) == 15 and state:
            gs = GST_STATE_CODES.get(c.value[:2])
            if gs and gs.lower() != state.lower():
                findings.append(Finding("gstin", c.value, state, "mismatch", "format_validated",
                                        f"GSTIN state code {c.value[:2]} means {gs}, but your profile state is {state}.", advisory=True))
        if c.field == "udyam_number":
            us = UDYAM_STATE_CODES.get(c.value.split("-")[1])
            if us and state and us.lower() != state.lower():
                findings.append(Finding("udyam_number", c.value, state, "mismatch", "format_validated",
                                        f"Udyam number state code means {us}, but your profile state is {state}.", advisory=True))
    declared = next((c.value for c in cands if c.field == "enterprise_class_declared"), None)
    inv, turn = P.get(profile, "investment_inr"), P.get(profile, "turnover_inr")
    if declared and inv is not None and turn is not None:
        computed = P.compute_class(inv, turn, cat)
        if computed != declared:
            findings.append(Finding("enterprise_class_declared", declared, computed, "mismatch", "label_match",
                                    f"Certificate says {declared}, but your investment/turnover numbers compute to {computed} "
                                    "under the 2025 classification. Check your numbers or whether the certificate is outdated.", advisory=True))
    return findings


def apply_decisions(profile: dict, decisions: list[dict], doc_name: str) -> dict:
    """decisions: [{'field','value','action'}], action in accept|overwrite|reject.
    - accept only writes when the field is currently unknown (or identical).
    - a mismatch is written ONLY with action 'overwrite' (explicit human choice).
    """
    p = profile
    for d in decisions:
        act = d.get("action")
        if act == "reject":
            continue
        cur = P.get(p, d["field"])
        if act == "accept" and cur is not None and str(cur).lower() != str(d["value"]).lower():
            continue  # never silently overwrite
        if act in ("accept", "overwrite"):
            val = d["value"]
            if P.FIELDS[d["field"]]["kind"] == "int":
                val = int(val)
            p = P.set_field(p, d["field"], val, source=f"document:{doc_name}")
    return p


def candidates_to_json(c: list[Candidate]) -> list[dict]:
    return [asdict(x) for x in c]
