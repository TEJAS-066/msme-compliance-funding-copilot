"""Generate SYNTHETIC sample documents for the demo + tests. Nothing here is a real certificate.
Run:  python scripts/make_samples.py
"""
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.documents import gstin_check_char  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")
os.makedirs(OUT, exist_ok=True)


def make_gstin(state_code: str, pan_like: str = "ABCDE1234F") -> str:
    body = f"{state_code}{pan_like}1Z"
    return body + gstin_check_char(body)


def pdf(name: str, lines: list[str]) -> None:
    c = canvas.Canvas(os.path.join(OUT, name), pagesize=A4)
    y = 800
    for ln in lines:
        c.drawString(50, y, ln)
        y -= 22
    c.save()


UDYAM = [
    "UDYAM REGISTRATION CERTIFICATE",
    "*** SYNTHETIC SAMPLE - NOT A REAL CERTIFICATE - FOR DEMO ONLY ***",
    "UDYAM REGISTRATION NUMBER: UDYAM-TN-02-0000123",
    "NAME OF ENTERPRISE: Lakshmi Garments (DEMO)",
    "TYPE OF ENTERPRISE: Micro",
    "TYPE OF ORGANISATION: Proprietary",
    "MAJOR ACTIVITY: Manufacturing",
    "DISTRICT: Tiruppur",
    "STATE: Tamil Nadu",
]
pdf("sample_udyam_lakshmi.pdf", UDYAM)

pdf("sample_gst_lakshmi.pdf", [
    "GST REGISTRATION CERTIFICATE",
    "*** SYNTHETIC SAMPLE - NOT A REAL CERTIFICATE - FOR DEMO ONLY ***",
    f"GSTIN: {make_gstin('33')}",
    "LEGAL NAME: Lakshmi (DEMO)",
])

# Cross-check demo: GSTIN says Karnataka (29) but the owner's profile says Tamil Nadu
pdf("sample_gst_state_mismatch.pdf", [
    "GST REGISTRATION CERTIFICATE",
    "*** SYNTHETIC SAMPLE - state code deliberately inconsistent ***",
    f"GSTIN: {make_gstin('29')}",
])

# Class-mismatch demo: certificate says Small, but demo numbers compute to Micro
pdf("sample_udyam_class_mismatch.pdf", [ln.replace("TYPE OF ENTERPRISE: Micro", "TYPE OF ENTERPRISE: Small") for ln in UDYAM])

# 'Scanned' style PDF: drawn shapes only, no text layer -> extraction must say OCR not available
c = canvas.Canvas(os.path.join(OUT, "sample_scan_no_text_layer.pdf"), pagesize=A4)
c.rect(50, 500, 400, 200)
c.save()

# Corrupt file
with open(os.path.join(OUT, "sample_corrupt.pdf"), "wb") as f:
    f.write(b"%PDF-1.4 this is not really a pdf")

print("samples written to", OUT, sorted(os.listdir(OUT)))
