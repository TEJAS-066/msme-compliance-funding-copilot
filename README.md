# MSME Compliance & Funding Copilot — TEJAS066 MVP (v0.1)

> From “I need help” to “I know what to do next.”  
> **Rules decide. AI explains. The owner acts.**

A runnable, tested MVP for the TEJAS 2026 final: the whole Lakshmi journey from the proposal, built to be *trustworthy* rather than flashy.

## Run it (3 commands)
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 → Dashboard → **Load demo profile** → walk the six steps. No account or API key needed.

## Test it
```bash
python -m pytest -q                 # 224 tests (rules, documents, copilot grounding, webhook, monitor, i18n, UI)
python -m evaluation.run_eval       # KPI harness on synthetic sets
python scripts/make_samples.py      # regenerate synthetic sample documents
```

## What works today (verified by tests)
| Capability | Where | Notes |
|---|---|---|
| Editable business profile, value + known/unknown | `core/profile.py`, `ui/profile_view.py` | unknown is never guessed |
| Source-backed scheme catalogue (MUDRA, CGTMSE) | `data/schemes.json`, `core/catalogue.py` | validator rejects unsourced criteria |
| Deterministic eligibility engine (PASS/FAIL/UNKNOWN/N-A) | `core/eligibility.py` | no LLM involved |
| **Decision support**: next-best-action (information gain), what-if tipping points, "what the rule requires" | `core/insights.py` | all derived from the catalogue's own rules |
| Document upload → extraction → confirmation (3 separate states) + cross-checks | `core/documents.py` | PDF text, GSTIN checksum, state/class mismatch; OCR only if tesseract installed |
| Document checklist | `core/checklist.py` | verified vs “commonly requested (unverified)” kept apart |
| Grounded Copilot EN + Tamil with **module trace**; LLM optional behind a guard | `services/copilot.py` | demo mode by default |
| Alerts & deadlines + WhatsApp-style **preview** | `services/alerts.py`, dashboard | the Lakshmi “Tamil alert” story; never sent from here |
| Readiness report (download) | `services/report.py` | take to bank / CSC; says it is not an application |
| Form help (preparation worksheet) | `core/forms.py` | never claims submission |
| Tasks, application tracking, reminders | `core/tasks.py` | “saved” ≠ “sent” |
| **WhatsApp webhook** (Twilio, signature-verified) + in-app simulator | `services/whatsapp*.py`, `scripts/whatsapp_server.py`, `docs/WHATSAPP.md` | tested over real HTTP locally; real phone needs your Twilio account |
| **Source-change monitor** + admin approval queue + CI cron | `services/monitoring.py`, `scripts/monitor_sources.py`, `.github/workflows/` | detects changed pages; a human must approve before any notice |
| Experimental browser voice input (EN/TA) | `ui/voice.py` | Chrome/Edge Web Speech API; syntax-checked, **not run in a browser here** |
| KPI harness | `evaluation/` | regression check, not real-world proof |

## What is NOT done yet (say so in the demo)
OCR for scans · Hindi/Telugu · more than two verified schemes · live LLM/Twilio runs (written, never executed with real keys) · per-user accounts, consent, encryption · a real pilot for the 90% / 40% targets.
See `docs/TRACEABILITY.md` for promise-by-promise status and `docs/WHATSAPP.md` for the channel.

## Optional: turn on an LLM
Copy `.env.example` → `.env`, set `LLM_PROVIDER` and the matching key. The app loads env vars; for Streamlit Cloud use *Secrets*. Provider payloads (Anthropic / Gemini / Sarvam) were written from public docs and **not run live in this build** — run once and fix model names if needed. Every LLM answer passes `services/copilot.guard()`; on failure the deterministic answer is used.

## Layout
```
app.py            Streamlit shell (language switch + navigation)
core/             business logic, no UI, no network  (profile, eligibility, insights, documents, checklist, tasks, forms, db, i18n, catalogue)
services/         retrieval, llm adapter, copilot, alerts, report, notifications, monitoring, channel, whatsapp(+server)
ui/               one file per page
data/             schemes.json (the only source of scheme facts), demo_profile.json, review_queue.json
tests/ evaluation/ samples/ scripts/ docs/
```

## Safety rules (do not break)
1. Never add a scheme fact without a `source_ids` entry — the validator will fail the build.
2. Missing data is UNKNOWN, never PASS.
3. Never write “approved / guaranteed / submitted / sent” unless it really happened.
4. Keys only in env vars / secrets. Synthetic data only in the repo.
