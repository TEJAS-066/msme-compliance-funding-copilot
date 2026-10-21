"""Environment doctor: tells you in 5 seconds what will and won't work on THIS computer.

Run:  python scripts/doctor.py          (exit code 1 only if something REQUIRED is broken)
Never prints secret values - only whether they are set.
"""
import importlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from core import config  # noqa: E402

rows: list[tuple[str, str, str]] = []      # (status, check, detail)


def add(status, check, detail=""):
    rows.append((status, check, detail))


def main() -> int:
    loaded = config.load_env_file()
    v = sys.version_info
    add("OK" if v >= (3, 10) else "FAIL", "Python >= 3.10", f"{v.major}.{v.minor}.{v.micro}")

    for mod, required in (("streamlit", True), ("pypdf", True), ("requests", True), ("pytest", False),
                          ("reportlab", False), ("PIL", False), ("pytesseract", False), ("pypdfium2", False)):
        try:
            m = importlib.import_module(mod)
            add("OK", f"package {mod}", getattr(m, "__version__", ""))
        except ImportError:
            add("FAIL" if required else "WARN", f"package {mod}", "missing -> pip install -r requirements.txt")

    from core import documents as D
    tess = shutil.which("tesseract")
    add("OK" if tess else "WARN", "Tesseract program (OCR)", tess or "not installed: scans/photos will say 'OCR not available' (see docs/RUN_GUIDE.md)")
    if D.ocr_available():
        add("OK", "OCR languages", D._ocr_lang() + ("" if "tam" in D._ocr_lang() else "  (Tamil pack missing: install tesseract-ocr-tam)"))
    add("OK" if D.pdf_ocr_available() else "WARN", "Scanned-PDF OCR ready", "yes" if D.pdf_ocr_available() else "needs tesseract + pytesseract + pypdfium2")

    try:
        from core import catalogue as C
        cat = C.load()
        n = len(C.list_schemes(cat))
        add("OK", "Scheme catalogue valid", f"{n} verified scheme(s), {len(cat['sources'])} sources, version {cat['catalogue_version']}")
        stale = [r for r in __import__("services.monitoring", fromlist=["x"]).stale_schemes(cat) if r["stale"]]
        add("WARN" if stale else "OK", "Catalogue freshness", f"{len(stale)} stale record(s) (>90 days)" if stale else "all records fresh")
    except Exception as e:
        add("FAIL", "Scheme catalogue valid", f"{type(e).__name__}: {e}")

    try:
        with tempfile.TemporaryDirectory() as d:
            os.environ["MSME_DB_PATH"] = os.path.join(d, "t.db")
            from core import db
            db.save_profile({"fields": {}})
            ok = db.load_profile() == {"fields": {}}
        os.environ.pop("MSME_DB_PATH", None)
        add("OK" if ok else "FAIL", "SQLite read/write", "ok" if ok else "round-trip failed")
    except Exception as e:
        add("FAIL", "SQLite read/write", f"{type(e).__name__}")

    add("OK" if os.path.isfile(os.path.join(ROOT, ".env")) else "INFO", ".env file", f"loaded {len(loaded)} setting(s): {', '.join(loaded) or 'none'}" if loaded else "absent - fine for demo mode")
    from services import llm
    prov = llm.get_provider()
    add("OK" if prov else "INFO", "LLM provider", prov or "none configured -> deterministic demo mode (fully usable)")
    from services import notifications as N
    add("OK" if N.whatsapp_configured() else "INFO", "Twilio WhatsApp credentials", "present" if N.whatsapp_configured() else "not set -> sends report NOT_CONFIGURED (simulator still works)")

    gi = os.path.join(ROOT, ".gitignore")
    ignored = os.path.isfile(gi) and ".env" in open(gi, encoding="utf-8").read().split()
    add("OK" if ignored else "FAIL", ".env is git-ignored", "yes" if ignored else "ADD .env TO .gitignore")
    if shutil.which("git") and os.path.isdir(os.path.join(ROOT, ".git")):
        tracked = subprocess.run(["git", "ls-files", ".env"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        add("FAIL" if tracked else "OK", ".env not committed", "COMMITTED - rotate every key in it!" if tracked else "ok")

    width = max(len(r[1]) for r in rows)
    mark = {"OK": "✔", "WARN": "!", "FAIL": "✖", "INFO": "·"}
    for status, check, detail in rows:
        print(f" {mark[status]} {status:<4} {check:<{width}}  {detail}")
    fails = [r for r in rows if r[0] == "FAIL"]
    print("\nRESULT:", "NOT READY - fix the FAIL lines" if fails else "READY (warnings are optional features)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
