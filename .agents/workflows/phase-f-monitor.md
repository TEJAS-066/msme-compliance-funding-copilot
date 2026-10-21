---
description: Source monitor: first live run (Data owner): Run the monitor against the real source pages and make it quiet on unchanged pages.
---
# Phase F - Source monitor: first live run (Data owner)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-f-monitor-<yourname>`.

**Goal:** Run the monitor against the real source pages and make it quiet on unchanged pages.
**Why it matters:** Built and unit-tested, but never run against the live sites.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Run on a machine with normal internet (the authoring sandbox blocked government sites).

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Run `python scripts/monitor_sources.py`; paste baseline count and the per-source error list.
2. Run it again immediately; any 'changed' source is a false alarm -> add a per-source normalisation rule in services/monitoring.normalize with a saved HTML fixture test.
3. Edit data/source_hashes.json for one source to simulate a change; confirm a PENDING item appears and nothing is notifiable until approved in the Admin page.
4. Enable the monitor workflow via workflow_dispatch in GitHub Actions and report the run result.

**Done when:**
- second run reports 0 changes on static pages
- simulated change creates exactly one pending item
- approval flow verified in the UI

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-f-monitor` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
