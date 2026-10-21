---
description: Verified scheme data (Data owner): Every criterion rests on an OFFICIAL source; add 1-3 more schemes only from official text.
---
# Phase B - Verified scheme data (Data owner)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-b-data-<yourname>`.

**Goal:** Every criterion rests on an OFFICIAL source; add 1-3 more schemes only from official text.
**Why it matters:** Wrong eligibility advice is the fastest way to lose credibility. 4 criteria are still secondary-only; PMEGP's source URLs were not independently opened.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Save the OFFICIAL page text/PDF text for each scheme into docs/source_texts/<id>.txt (PMEGP, MUDRA FAQ, CGTMSE guidelines, then TN NEEDS / UYEGP).
- Open the official URL yourself and confirm it loads; note the date.

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Run `python scripts/validate_catalogue.py`; list the secondary-only criteria (MUDRA: nonfarm, noncorporate; CGTMSE: not_agri, not_excluded_entity).
2. For each, using ONLY docs/source_texts/*.txt, either add an official source and upgrade it, or keep it tagged secondary and say why.
3. Re-check PMEGP: criterion `new_project` wording, ceilings, and that `loan_needed_inr` is only a proxy for project cost (see `unresolved`).
4. New scheme: `python scripts/new_scheme.py --id <id> --name "<name>"`, fill the draft from the text only, using existing profile fields. If a criterion needs a new field, STOP and propose it.
5. Write docs/source_notes/<id>.md: a table `criterion id | quote from the source (<=25 words) | file+line`. A criterion without a quote is not allowed.
6. Hand-derive 4+ evaluation cases (include boundaries) in evaluation/cases.json BEFORE running; then run `python -m evaluation.run_eval`.
7. Move the draft into data/schemes.json, set review_status honestly, add Tamil/Hindi/Telugu names marked for review.

**Done when:**
- validate_catalogue VALID
- every criterion has a quote in docs/source_notes
- eval 100% on new cases written BEFORE the run
- existing scheme records unchanged (git diff)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-b-data` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
