---
description: Documents: real-world OCR + privacy (Docs owner): Make extraction survive phone-photo quality, and guarantee sensitive IDs are never stored.
---
# Phase D - Documents: real-world OCR + privacy (Docs owner)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-d-docs-<yourname>`.

**Goal:** Make extraction survive phone-photo quality, and guarantee sensitive IDs are never stored.
**Why it matters:** Owners upload photos, not clean PDFs. Current OCR is proven only on clean renders.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Install Tesseract (+ Tamil pack). `python scripts/doctor.py` must show OCR ready.

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. In scripts/make_samples.py add DEGRADED variants of the Udyam sample (rotate 3 deg, blur, low contrast, JPEG compression).
2. Measure field accuracy BEFORE any change (python -m evaluation.run_eval with new cases) and record it.
3. Add preprocessing in core/documents.py (grayscale, autocontrast, upscale, simple threshold, small deskew) using Pillow only. Re-measure; keep only changes that help.
4. Privacy: detect 12-digit Aadhaar-like numbers (####  ####  ####). Never extract or store them; show a warning. Add tests. Confirm raw OCR text is never written to SQLite (test).
5. Add 1 more document field if the sample supports it (e.g. date of registration).

**Done when:**
- before/after numbers reported
- Aadhaar never stored (test)
- tests pass with and without tesseract (scripts hide it via PATH)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-d-docs` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
