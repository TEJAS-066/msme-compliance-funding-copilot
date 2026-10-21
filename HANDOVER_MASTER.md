# HANDOVER_MASTER — single source of truth (read this first)

**Project:** MSME Compliance & Funding Copilot — Team TEJAS066, TEJAS 2026 finals (22–23 Oct 2026).
**Promise to the panel:** "From *I need help* to *I know what to do next*." Rules decide · AI explains · the owner acts.
**Stack:** Python 3.10+ · Streamlit · SQLite · (optional) Gemini/Sarvam/Claude behind a guard · Tesseract OCR · Twilio WhatsApp webhook.
**Next work is defined in `docs/UPGRADE_PLAYBOOK.md` and as slash-commands in `.agents/workflows/`. Follow them; do not invent a different product.**

## 1. State at handover (all numbers are from real runs)
| Item | Result |
|---|---|
| `python -m pytest -q` | **280 passed** (includes 9 JavaScript tour tests run in a simulated browser and all 10 pages × 4 languages) |
| KPI harness `python -m evaluation.run_eval` | eligibility **67/67** (25 hand-labelled cases, 3 schemes) · extraction **24/24** (with OCR installed; 2 OCR samples are *skipped*, not counted, when it isn't) |
| `python scripts/verify_phase.py` | PASS · no secrets · no risky claims · 4 criteria still secondary-sourced (below) |
| Verified schemes | MUDRA (PMMY), CGTMSE, PMEGP — `partly_verified_official` |
| Languages | English, Tamil, Hindi, Telugu (UI strings have English fallback; **only English is reviewed — all others are AI drafts**) |

**These are regression checks on small synthetic sets. They are NOT proof of real-world accuracy. Never present the 90% / 24-hour / 40% targets as achieved.**

## 2. What exists (done)
Profile with known/unknown fields · deterministic eligibility engine (PASS/FAIL/UNKNOWN/N-A) · insights (next-best-action, what-if tipping points, "what the rule requires") · 3-state document pipeline (upload → extraction incl. **OCR** → owner confirmation) with GSTIN/Udyam/class cross-checks · checklist · grounded copilot with module trace + LLM guard · alerts/deadlines with WhatsApp-style *preview* · readiness report · tasks & application tracking · Twilio WhatsApp webhook (signature-verified, rate-limited) + in-app simulator · source-change monitor + daily CI job + admin approval queue · per-visitor data isolation + admin PIN for shared deployments · **guided tour (speech-bubble coach marks, 4 languages, auto-starts, jumps between pages)** · global ⓘ menu and light/dark switch · dashboard 5-stage method + 6-module panel mapped to the video slides.

## 3. What is NOT done / not proven (be honest in the demo)
1. **Never run live:** LLM calls with a real key · a real WhatsApp message from a phone · monitor job against the real government sites · browser voice input · deployment.
2. **UI never seen on a real screen by the author** (no browser in the build sandbox). The tour and theme were tested in jsdom and against Streamlit's DOM selectors, not visually. Dark-mode contrast and layout polish are **Phase H, driven by human screenshots**.
3. 4 criteria are secondary-sourced only: MUDRA `nonfarm`, `noncorporate`; CGTMSE `not_agri`, `not_excluded_entity`. PMEGP's official URLs were supplied by the previous tool and **not opened** by the reviewer.
4. OCR proven only on clean synthetic renders, not phone photos.
5. All Tamil/Hindi/Telugu text is unreviewed AI drafts.
6. No accounts/consent/encryption; WhatsApp uses ONE shared profile (demo scope). No Hindi/Telugu voice.

## 4. Reviewer audit of the previous tool's work (so you know what changed and why)
Kept: PMEGP data (figures cross-checked against several sources incl. a Lok Sabha reply), 5-stage stepper and 6-module panel on the dashboard, Hindi/Telugu i18n overlays, many extra tests, run_pipeline.py, Docker files.
**Fixed:** PMEGP had no *new-project* rule (it funds new units only) → added `new_project` field/criterion; demo Lakshmi is *expanding* an existing unit, so PMEGP now correctly says "unlikely" · admin page showed hard-coded "Hallucination Rate 0%" / "6/6 Operational" and a fake-100% fallback → replaced by measured numbers only · "Zero Hallucination Guarantee" wording → "LLM never decides eligibility (by design)" · tour was a modal dialog and per-page theme toggles caused reruns → replaced by one global shell (`ui/shell.py`, `ui/assets/shell.js|css`).
**Removed:** `services/api_server.py` (service imported UI code; open CORS exposed profile read/write; fronted a React app that does not exist), `--api` flag, ~400 lines of hard-coded bilingual walkthrough data in `ui/common.py`. The React architecture note is kept as `docs/future/REACT_ARCHITECTURE_PROPOSAL.md` and marked **NOT BUILT**.
**Watch:** dashboard button `btn_sim_udyam` shortcut auto-applies the sample document without the per-field confirmation (demo convenience; label it as such or remove). Do not reintroduce hard-coded metrics.

## 5. Architecture in 10 lines
`core/` pure logic (profile, eligibility, insights, documents/OCR, checklist, forms, tasks, db, i18n, config) · `services/` (retrieval, copilot+guard, llm adapter, alerts, report, notifications, monitoring, whatsapp, channel) · `ui/` display only (`ui/shell.py` injects tour/theme/ⓘ via `st.iframe`; `ui/assets/`) · `data/schemes.json` is the only source of scheme facts · `evaluation/` KPI harness · `scripts/` doctor, verify_phase, check_llm, monitor_sources, whatsapp_server, new_scheme, make_samples, setup.

## 6. Roadmap (follow this order)
MUST: **0 start-here → B data (official sources) → H UI polish (with screenshots) → I deploy/freeze.**
SHOULD: C live LLM · D OCR robustness + Aadhaar privacy · E real WhatsApp/voice evidence · F monitor live run · G language review pipeline.
LATER: pilot with a CSC/bank, accounts + consent + encryption, more schemes, per-sender WhatsApp profiles.
Each phase: prompt, acceptance and reviewer checklist are in `docs/UPGRADE_PLAYBOOK.md`; slash-command `/<phase-id>` in Antigravity.

## 7. Working agreement
Small diffs · tests after each change · `python scripts/verify_phase.py --phase <id>` before claiming done · paste the report + summary to the reviewer (template in the playbook) · never weaken a test or `guard()` · never claim what you did not run · ask before new dependencies or contract changes.

## 8. Update this file
When a phase finishes, edit §1 (numbers from real output), move the item from §3 to §2 only with evidence, and keep §6 current. Do not let this file drift from reality.
