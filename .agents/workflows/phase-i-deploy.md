---
description: Deploy, rehearse, freeze (Tech lead): A public URL that survives several judges at once, plus a local fallback.
---
# Phase I - Deploy, rehearse, freeze (Tech lead)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-i-deploy-<yourname>`.

**Goal:** A public URL that survives several judges at once, plus a local fallback.
**Why it matters:** A crashing demo loses to a simple working one.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Repo pushed to GitHub. Streamlit Community Cloud account.

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Deploy main file app.py. packages.txt installs Tesseract; choose Python 3.12 under Advanced settings.
2. Secrets (TOML): MSME_MULTIUSER="1", ADMIN_PIN="<pin>", optionally LLM_PROVIDER + key. Never put keys in the repo.
3. Open the URL in two browsers: confirm data is private per session; confirm Admin asks for the PIN; confirm the tour auto-starts in a fresh tab.
4. Record a 3-minute backup video of the full journey; prepare a local run on two laptops (`bash scripts/setup.sh`).
5. Tag v1.0 and stop adding features.

**Done when:**
- public URL works on a phone
- isolation verified in two browsers
- backup video + local fallback ready

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-i-deploy` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
