# TEJAS066 Upgrade Playbook (v1.0)

Single source for **what to build next, who builds it, how to ask the AI tool, and how to verify the result**.
The same phases exist as Antigravity slash-commands in `.agents/workflows/` (type `/phase-b-data` etc.).

## The loop (every phase)
1. **Prime:** new chat -> `/start-here`-style read of HANDOVER_MASTER.md. Create a branch `feat/<phase>-<name>`.
2. **Do:** run the phase workflow. One small change at a time; tests after each.
3. **Verify:** `python scripts/verify_phase.py --phase <id>` -> produces `verification_report.md` (tests, KPIs, catalogue, secret scan, risky-claim scan).
4. **Review:** paste `verification_report.md` + the agent's final summary + the diff stat into the reviewer chat (Claude) using the template below.
5. **Merge** only when the report says PASS and the reviewer checklist is ticked.

## Review request template (copy into the reviewer chat)
```
PHASE: <id>      BRANCH: <name>      COMMIT: <hash>
1) verification_report.md  -> (paste)
2) Agent's summary of what it changed and why -> (paste)
3) `git diff --stat main` -> (paste)
4) Anything the agent said it could NOT verify -> (paste)
5) My own observations on screen (screenshots for UI phases) -> (attach)
```

## Priorities for the remaining time
MUST: Phase 0, B (data), H (UI polish), I (deploy)  -  SHOULD: C, D, E, F, G  -  LATER: pilot, accounts/consent, more schemes.

## Hard rules (also in `.agents/rules/msme-copilot.md`)
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.


## Phase overview

| Phase | Owner | Priority | Time | Goal |
|---|---|---|---|---|
| `start-here` | All 5 | MUST | 1 h | Everyone can run the app, the tests and the tour, and can explain the architecture back. |
| `phase-b-data` | Lohitha / data owner | MUST | 4-6 h | Every criterion rests on an OFFICIAL source; add 1-3 more schemes only from official text. |
| `phase-c-llm` | Sabarish / tech lead | SHOULD | 3-4 h | Prove the guarded LLM path with a real key, pick the best provider for Tamil, keep the guard strict. |
| `phase-d-docs` | Nandhini / docs owner | SHOULD | 4-5 h | Make extraction survive phone-photo quality, and guarantee sensitive IDs are never stored. |
| `phase-e-channels` | Tech lead + UI owner | SHOULD | 2-3 h | Run the WhatsApp webhook with a real phone and test browser voice; record evidence. |
| `phase-f-monitor` | Data owner | SHOULD | 2 h | Run the monitor against the real source pages and make it quiet on unchanged pages. |
| `phase-g-lang-review` | Harshini / UI owner | SHOULD | 2-3 h | Get Tamil/Hindi/Telugu text reviewed by native speakers and applied safely. |
| `phase-h-ui-polish` | UI owner + whoever sees the screen | MUST | 3-5 h | Make every page obvious in 5 seconds. The author could not see the screen; the human can. |
| `phase-i-deploy` | Tech lead + leader | MUST | 3 h | A public URL that survives several judges at once, plus a local fallback. |

---

## Phase 0 - Get oriented (everyone, ~1 hour, no code changes)

**Owner:** All 5  -  **Priority:** MUST  -  **Time-box:** 1 h  -  **Antigravity:** type `/start-here`

**Goal:** Everyone can run the app, the tests and the tour, and can explain the architecture back.

**Why:** Judges test whether you understand what you built. This is the cheapest insurance.

**Human prep**
- Python 3.10+ installed; run `bash scripts/setup.sh` (Mac/Linux) or `scripts\setup.bat` (Windows).

**Paste-ready prompt** (identical to the slash-command)

```text
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
```

**Acceptance**
- [ ] doctor shows READY
- [ ] pytest all green (JS tests may skip without `cd tests/js && npm install`)
- [ ] explain-back given

**Reviewer checklist** (what the human / Claude checks)
- [ ] Does the explanation name real files/functions?
- [ ] Are numbers (tests, KPIs) copied from real output, not guessed?

---

## Phase B - Verified scheme data (Data owner)

**Owner:** Lohitha / data owner  -  **Priority:** MUST  -  **Time-box:** 4-6 h  -  **Antigravity:** type `/phase-b-data`

**Goal:** Every criterion rests on an OFFICIAL source; add 1-3 more schemes only from official text.

**Why:** Wrong eligibility advice is the fastest way to lose credibility. 4 criteria are still secondary-only; PMEGP's source URLs were not independently opened.

**Human prep**
- Save the OFFICIAL page text/PDF text for each scheme into docs/source_texts/<id>.txt (PMEGP, MUDRA FAQ, CGTMSE guidelines, then TN NEEDS / UYEGP).
- Open the official URL yourself and confirm it loads; note the date.

**Paste-ready prompt** (identical to the slash-command)

```text
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
```

**Acceptance**
- [ ] validate_catalogue VALID
- [ ] every criterion has a quote in docs/source_notes
- [ ] eval 100% on new cases written BEFORE the run
- [ ] existing scheme records unchanged (git diff)

**Reviewer checklist** (what the human / Claude checks)
- [ ] Open the official page; confirm each quote exists and means what the criterion says.
- [ ] Check <= vs < at every boundary.
- [ ] Check `unresolved` lists everything the text does not settle.
- [ ] Check nothing was copied from AI memory.

---

## Phase C - Live LLM + Tamil quality (Tech lead)

**Owner:** Sabarish / tech lead  -  **Priority:** SHOULD  -  **Time-box:** 3-4 h  -  **Antigravity:** type `/phase-c-llm`

**Goal:** Prove the guarded LLM path with a real key, pick the best provider for Tamil, keep the guard strict.

**Why:** The LLM code was written from public docs and has never run with a real key.

**Human prep**
- Create keys (Gemini AI Studio, optional Sarvam/Anthropic) and put them in .env only.
- Do NOT use real customer data; free tiers may use prompts to improve products (check the provider's terms).

**Paste-ready prompt** (identical to the slash-command)

```text
Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-c-llm-<yourname>`.

**Goal:** Prove the guarded LLM path with a real key, pick the best provider for Tamil, keep the guard strict.
**Why it matters:** The LLM code was written from public docs and has never run with a real key.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Create keys (Gemini AI Studio, optional Sarvam/Anthropic) and put them in .env only.
- Do NOT use real customer data; free tiers may use prompts to improve products (check the provider's terms).

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Run `python scripts/check_llm.py`; paste the output.
2. Create evaluation/llm_questions.json: 10 English, 10 Tamil, 5 out-of-scope questions with the expected behaviour (answer / refuse).
3. Create scripts/eval_llm.py: for each provider with a key, run all questions; write docs/LLM_RESULTS.md with guard-pass rate, fallback rate, refusal correctness and latency per provider.
4. Improve SYSTEM_PROMPT in services/copilot.py only to raise pass rate. For every failure mode found, add a test using a fake LLM function. Do NOT loosen guard().
5. Ask a native Tamil speaker to rate 10 Tamil answers 1-5; record the scores; choose the default provider.

**Done when:**
- docs/LLM_RESULTS.md has real numbers
- all guard tests still pass; guard() diff only adds checks
- no key in repo (verify_phase secret scan)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-c-llm` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
```

**Acceptance**
- [ ] docs/LLM_RESULTS.md has real numbers
- [ ] all guard tests still pass; guard() diff only adds checks
- [ ] no key in repo (verify_phase secret scan)

**Reviewer checklist** (what the human / Claude checks)
- [ ] Is each number traceable to a real run?
- [ ] Did guard() get stricter or equal?
- [ ] Are failing providers reported, not hidden?

---

## Phase D - Documents: real-world OCR + privacy (Docs owner)

**Owner:** Nandhini / docs owner  -  **Priority:** SHOULD  -  **Time-box:** 4-5 h  -  **Antigravity:** type `/phase-d-docs`

**Goal:** Make extraction survive phone-photo quality, and guarantee sensitive IDs are never stored.

**Why:** Owners upload photos, not clean PDFs. Current OCR is proven only on clean renders.

**Human prep**
- Install Tesseract (+ Tamil pack). `python scripts/doctor.py` must show OCR ready.

**Paste-ready prompt** (identical to the slash-command)

```text
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
```

**Acceptance**
- [ ] before/after numbers reported
- [ ] Aadhaar never stored (test)
- [ ] tests pass with and without tesseract (scripts hide it via PATH)

**Reviewer checklist** (what the human / Claude checks)
- [ ] Are before/after measured on the same set?
- [ ] Any gain only on synthetic data? Say so.
- [ ] grep for raw text persistence.

---

## Phase E - Real WhatsApp + voice evidence (Tech lead / UI owner)

**Owner:** Tech lead + UI owner  -  **Priority:** SHOULD  -  **Time-box:** 2-3 h  -  **Antigravity:** type `/phase-e-channels`

**Goal:** Run the WhatsApp webhook with a real phone and test browser voice; record evidence.

**Why:** The webhook is tested locally and against Twilio's validator, but never with a real message.

**Human prep**
- Twilio account + WhatsApp sandbox joined from a phone; ngrok installed.
- Follow docs/WHATSAPP.md.

**Paste-ready prompt** (identical to the slash-command)

```text
Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-e-channels-<yourname>`.

**Goal:** Run the WhatsApp webhook with a real phone and test browser voice; record evidence.
**Why it matters:** The webhook is tested locally and against Twilio's validator, but never with a real message.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Twilio account + WhatsApp sandbox joined from a phone; ngrok installed.
- Follow docs/WHATSAPP.md.

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Help me run scripts/whatsapp_server.py, expose it, and debug the first real message. Never loosen signature verification.
2. Create docs/CHANNEL_TEST_LOG.md: date, steps, the real message text sent/received (English + Tamil), what failed, fixes.
3. Open the app in Chrome; test ui/voice.py in English and Tamil; record exactly what happens. Fix only what you observed.
4. Add rate-limit / unknown-sender behaviour notes to the log.

**Done when:**
- a real Tamil reply received on a phone, logged
- voice result logged honestly (works / fails / browser-dependent)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-e-channels` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
```

**Acceptance**
- [ ] a real Tamil reply received on a phone, logged
- [ ] voice result logged honestly (works / fails / browser-dependent)

**Reviewer checklist** (what the human / Claude checks)
- [ ] Screenshots or copied message text present?
- [ ] Signature check untouched (git diff services/whatsapp.py).

---

## Phase F - Source monitor: first live run (Data owner)

**Owner:** Data owner  -  **Priority:** SHOULD  -  **Time-box:** 2 h  -  **Antigravity:** type `/phase-f-monitor`

**Goal:** Run the monitor against the real source pages and make it quiet on unchanged pages.

**Why:** Built and unit-tested, but never run against the live sites.

**Human prep**
- Run on a machine with normal internet (the authoring sandbox blocked government sites).

**Paste-ready prompt** (identical to the slash-command)

```text
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
```

**Acceptance**
- [ ] second run reports 0 changes on static pages
- [ ] simulated change creates exactly one pending item
- [ ] approval flow verified in the UI

**Reviewer checklist** (what the human / Claude checks)
- [ ] Are false positives handled by normalisation, not by ignoring changes?
- [ ] Nothing auto-approves.

---

## Phase G - Language review pipeline (UI / Tamil owner)

**Owner:** Harshini / UI owner  -  **Priority:** SHOULD  -  **Time-box:** 2-3 h  -  **Antigravity:** type `/phase-g-lang-review`

**Goal:** Get Tamil/Hindi/Telugu text reviewed by native speakers and applied safely.

**Why:** All non-English text is an AI draft. Wrong wording in a financial tool hurts trust.

**Human prep**
- Find one native reviewer per language (even a family member).

**Paste-ready prompt** (identical to the slash-command)

```text
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
```

**Acceptance**
- [ ] export/import round-trip tested
- [ ] placeholder mismatch rejected (test)

**Reviewer checklist** (what the human / Claude checks)
- [ ] Wording changes in the diff all come from the CSV?
- [ ] Placeholders intact.

---

## Phase H - UI polish with screenshots (UI owner)

**Owner:** UI owner + whoever sees the screen  -  **Priority:** MUST  -  **Time-box:** 3-5 h  -  **Antigravity:** type `/phase-h-ui-polish`

**Goal:** Make every page obvious in 5 seconds. The author could not see the screen; the human can.

**Why:** The owner reported some components look confusing. Fix with evidence, not guesses.

**Human prep**
- Take screenshots of the 3 worst pages (light + dark, desktop + phone width 390px) and attach them to the agent chat.

**Paste-ready prompt** (identical to the slash-command)

```text
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
```

**Acceptance**
- [ ] before/after screenshots
- [ ] tour still passes JS tests
- [ ] all 4 languages render every page (tests/test_shell.py)

**Reviewer checklist** (what the human / Claude checks)
- [ ] Compare screenshots yourself on a phone.
- [ ] Try the tour in Tamil on the Documents page.

---

## Phase I - Deploy, rehearse, freeze (Tech lead)

**Owner:** Tech lead + leader  -  **Priority:** MUST  -  **Time-box:** 3 h  -  **Antigravity:** type `/phase-i-deploy`

**Goal:** A public URL that survives several judges at once, plus a local fallback.

**Why:** A crashing demo loses to a simple working one.

**Human prep**
- Repo pushed to GitHub. Streamlit Community Cloud account.

**Paste-ready prompt** (identical to the slash-command)

```text
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
```

**Acceptance**
- [ ] public URL works on a phone
- [ ] isolation verified in two browsers
- [ ] backup video + local fallback ready

**Reviewer checklist** (what the human / Claude checks)
- [ ] Check Settings > Secrets contains no key committed to git.
- [ ] Cold-start the app 10 minutes before presenting (free apps sleep).
