---
description: UI polish with screenshots (UI owner): Make every page obvious in 5 seconds. The author could not see the screen; the human can.
---
# Phase H - UI polish with screenshots (UI owner)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-h-ui-polish-<yourname>`.

**Goal:** Make every page obvious in 5 seconds. The author could not see the screen; the human can.
**Why it matters:** The owner reported some components look confusing. Fix with evidence, not guesses.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Take screenshots of the 3 worst pages (light + dark, desktop + phone width 390px) and attach them to the agent chat.

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. For each screenshot list concrete problems (alignment, contrast, density, unclear labels, hidden actions). Propose fixes BEFORE editing.
2. Rules: one primary action per page; <= 7 elements above the fold; plain-language labels; every empty state says what to do next; no new pages.
3. Dark mode: fix contrast in ui/assets/shell.css only (selectors are Streamlit data-testids). Light mode: ui/common.py apply_custom_styles.
4. Keep ui/assets/shell.js behaviour; run `cd tests/js && npm test` and pytest after each change.
5. Re-take the screenshots and attach before/after.

**Done when:**
- before/after screenshots
- tour still passes JS tests
- all 4 languages render every page (tests/test_shell.py)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-h-ui-polish` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
