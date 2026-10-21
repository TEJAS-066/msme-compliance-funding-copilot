---
description: Language review pipeline (UI / Tamil owner): Get Tamil/Hindi/Telugu text reviewed by native speakers and applied safely.
---
# Phase G - Language review pipeline (UI / Tamil owner)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-g-lang-review-<yourname>`.

**Goal:** Get Tamil/Hindi/Telugu text reviewed by native speakers and applied safely.
**Why it matters:** All non-English text is an AI draft. Wrong wording in a financial tool hurts trust.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Find one native reviewer per language (even a family member).

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Create scripts/export_strings.py: write every UI string, tour step and catalogue translation to strings_review.csv (key, en, ta, hi, te, status).
2. Create scripts/import_strings.py: read the reviewed CSV; refuse any row whose {placeholders} differ from English; apply to core/i18n*.py and ui/tour_content.py.
3. Add a test that imports a small fixture CSV. Do not change wording yourself - only reviewers do.
4. Add `reviewed_languages` to a config file and show a small 'draft translation' badge for unreviewed languages.

**Done when:**
- export/import round-trip tested
- placeholder mismatch rejected (test)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-g-lang-review` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
