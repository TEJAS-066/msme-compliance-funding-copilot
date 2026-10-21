"""Verification report generator - run after ANY change (yours or an AI tool's), then paste the report to your reviewer.

Run:  python scripts/verify_phase.py                  -> prints + writes verification_report.md
      python scripts/verify_phase.py --phase B-data   -> adds a label to the report

What it checks: full test suite, KPI harness, catalogue validity + source coverage, secret scan, risky-claim scan of every
user-facing string, git change summary. It never prints secret VALUES. Exit code 1 if anything FAILS.
"""
import argparse
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


SECRET_PATTERNS = {
    "Google API key": r"AIza[0-9A-Za-z_\-]{35}",
    "OpenAI/Anthropic-style key": r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{20,}",
    "Twilio Account SID": r"\bAC[a-f0-9]{32}\b",
    "Private key block": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "Generic key assignment": r"""(?i)\b(?:api[_-]?key|secret|token|auth[_-]?token)\b\s*[:=]\s*['"][A-Za-z0-9_\-/+]{20,}['"]""",
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
TEXT_EXT = {".py", ".md", ".json", ".txt", ".toml", ".yml", ".yaml", ".env", ".example", ".cfg", ".ini", ".sh", ".bat", ""}
RISKY = re.compile(r"(?i)\b(guaranteed|you are approved|successfully submitted|has been submitted|was submitted|message (?:was |has been )?sent|delivered)\b")
NEGATION = re.compile(r"(?i)\b(not|no|never|nothing|isn't|aren't|without|unless|only if|cannot|can't)\b")


def run(cmd, timeout=900):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"


def scan_secrets(root=ROOT):
    hits = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT or fn == "verification_report.md":
                continue
            path = os.path.join(base, fn)
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for name, pat in SECRET_PATTERNS.items():
                if re.search(pat, text):
                    hits.append((os.path.relpath(path, root), name))        # file + type only, never the value
    if os.path.isfile(os.path.join(root, ".env")):
        gi = open(os.path.join(root, ".gitignore"), encoding="utf-8").read().split() if os.path.isfile(os.path.join(root, ".gitignore")) else []
        if ".env" not in gi:
            hits.append((".env", ".env exists but is NOT in .gitignore"))
    return hits


def risky_strings():
    from core.catalogue import get_catalogue
    from core.i18n import TR
    out = []
    for k, (en, _ta) in TR.items():
        if RISKY.search(en) and not NEGATION.search(en):
            out.append(f"i18n:{k}: {en[:110]}")
    blob = json.dumps(get_catalogue(), ensure_ascii=False)
    for m in RISKY.finditer(blob):
        out.append(f"catalogue: …{blob[max(0, m.start() - 40):m.end() + 40]}…")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="unspecified")
    ap.add_argument("--out", default=os.path.join(ROOT, "verification_report.md"))
    ap.add_argument("--skip-tests", action="store_true")
    a = ap.parse_args()
    L, fails, warns = [], [], []
    L.append(f"# Verification report — phase: {a.phase}\n")
    L.append(f"- generated: {datetime.now().isoformat(timespec='seconds')}\n- python: {platform.python_version()} on {platform.system()}")
    rc, commit = run(["git", "rev-parse", "--short", "HEAD"])
    L.append(f"- git commit: {commit if rc == 0 else 'not a git repo / no commits'}\n")

    # 1 tests
    if not a.skip_tests:
        rc, out = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"])
        last = out.splitlines()[-1] if out else "(no output)"
        L.append(f"## 1. Test suite\n`{last}`\n")
        if rc != 0:
            fails.append("tests failing")
            L.append("```\n" + "\n".join(out.splitlines()[-25:]) + "\n```\n")
    # 2 eval
    rc, out = run([sys.executable, "-m", "evaluation.run_eval"])
    L.append("## 2. KPI harness (synthetic regression sets)\n```\n" + out.replace("EOF marker not found", "").strip() + "\n```\n")
    if rc != 0 or "FAIL" in out:
        fails.append("evaluation failures")
    # 3 catalogue
    from core import catalogue as C
    with open(C.CATALOGUE_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    problems = C.validate(raw)
    L.append("## 3. Scheme catalogue\n" + ("**INVALID**\n" + "\n".join(f"- {p}" for p in problems) if problems else "valid ✔") + "\n")
    if problems:
        fails.append("catalogue invalid")
    L.append("| scheme | status | criteria | official-backed | secondary-only | unsourced | docs not source-verified |\n|---|---|---|---|---|---|---|")
    for r in C.coverage(raw):
        L.append(f"| {r['scheme_id']} | {r['review_status']} | {r['criteria']} | {len(r['official_backed'])} | {', '.join(r['secondary_only']) or '-'} | {', '.join(r['unsourced']) or '-'} | {', '.join(r['documents_unverified']) or '-'} |")
        if r["secondary_only"]:
            warns.append(f"{r['scheme_id']}: secondary-only criteria {r['secondary_only']}")
    L.append("")
    # 4 secrets
    hits = scan_secrets()
    L.append("## 4. Secret scan\n" + ("none found ✔" if not hits else "**FOUND (values not shown):**\n" + "\n".join(f"- {f}: {n}" for f, n in hits)) + "\n")
    if hits:
        fails.append("possible secrets in repo")
    # 5 risky claims
    risky = risky_strings()
    L.append("## 5. Risky-claim scan of user-facing text\n" + ("nothing flagged ✔" if not risky else "Review these (affirmative wording about submit/sent/approved/guaranteed):\n" + "\n".join(f"- {r}" for r in risky)) + "\n")
    if risky:
        warns.append("risky claim wording to review")
    # 6 git summary
    rc, out = run(["git", "status", "--short"])
    L.append("## 6. Changed files (git)\n" + (f"```\n{out[:3000]}\n```" if rc == 0 and out else "no git changes / not a git repo") + "\n")
    # verdict
    L.append("## Verdict\n" + ("**FAIL** — " + "; ".join(fails) if fails else "**PASS**") + ("\n\nWarnings:\n" + "\n".join(f"- {w}" for w in warns) if warns else ""))
    report = "\n".join(L)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\n[report written to {a.out}]")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
