---
description: Get oriented (everyone, ~1 hour, no code changes): Everyone can run the app, the tests and the tour, and can explain the architecture back.
---
# Phase 0 - Get oriented (everyone, ~1 hour, no code changes)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/start-here-<yourname>`.

**Goal:** Everyone can run the app, the tests and the tour, and can explain the architecture back.
**Why it matters:** Judges test whether you understand what you built. This is the cheapest insurance.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Python 3.10+ installed; run `bash scripts/setup.sh` (Mac/Linux) or `scripts\setup.bat` (Windows).

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Run `python scripts/doctor.py` and `python -m pytest -q`; report the exact results.
2. Read HANDOVER_MASTER.md, docs/EXPLAINER.md, docs/CONTRACTS.md. Do NOT change code.
3. Explain the project back in 8 lines, then name the 3 modules most likely to be asked about in a jury Q&A and give a 60-second explanation of each, using real function names.
4. List anything in the repo that contradicts HANDOVER_MASTER.md.

**Done when:**
- doctor shows READY
- pytest all green (JS tests may skip without `cd tests/js && npm install`)
- explain-back given

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase start-here` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
