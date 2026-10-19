# MSME Compliance & Funding Copilot — TEJAS066 MVP (v0.1)

> From “I need help” to “I know what to do next.”  
> **Rules decide. AI explains. The owner acts.**

A runnable, tested MVP for the TEJAS 2026 final: the whole Lakshmi journey from the proposal, built to be *trustworthy* rather than flashy.

## One-Click Master Pipeline Orchestrator (Recommended)
Run the full multi-agent pipeline, integrity checks, and evaluation benchmark with a single command:
```bash
python run_pipeline.py             # Runs all 6 pipeline verification stages
python run_pipeline.py --launch    # Verifies pipeline and opens Streamlit UI
python run_pipeline.py --demo      # Lakshmi's Tiruppur journey walkthrough in CLI
python run_pipeline.py --wa        # Interactive multi-script WhatsApp CLI simulator
python run_pipeline.py --api       # Launches headless FastAPI REST microservice
```

### Docker Support (Containerized Run)
```bash
docker build -t msme-copilot .
docker run -p 8501:8501 msme-copilot
```

## Run the Web Application
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 → Dashboard → **Load demo profile** → walk the six steps. No account or API key needed.

## Test it
```bash
python -m pytest -q                 # 233 tests (rules, documents, copilot grounding, webhook, monitor, i18n, UI)
python -m evaluation.run_eval       # KPI harness on synthetic sets (55 eligibility + 15 extraction)
python scripts/check_llm.py         # LLM benchmark on 20 Indic/English queries with safety guard check
python scripts/make_samples.py      # regenerate synthetic sample documents
```

## What works today (verified by tests)
| Capability | Where | Notes |
|---|---|---|
| Editable business profile, value + known/unknown | `core/profile.py`, `ui/profile_view.py` | unknown is never guessed |
| Source-backed scheme catalogue (MUDRA, CGTMSE, PMEGP) | `data/schemes.json`, `core/catalogue.py` | validator rejects unsourced criteria; official KVIC/DC-MSME/PIB sources |
| Deterministic eligibility engine (PASS/FAIL/UNKNOWN/N-A) | `core/eligibility.py` | 100% deterministic rule logic; no LLM involved |
| **Decision support**: next-best-action (information gain), what-if tipping points, "what the rule requires" | `core/insights.py` | all derived from the catalogue's own rules |
| Document upload → extraction → confirmation (3 separate states) + cross-checks | `core/documents.py` | PDF text, GSTIN Luhn checksum, state/class mismatch; OCR only if tesseract installed |
| Document checklist | `core/checklist.py` | verified vs “commonly requested (unverified)” kept apart |
| Grounded Copilot (English, தமிழ், हिन्दी, తెలుగు) with **module trace** | `services/copilot.py` | multi-language intent detection & safety guard |
| Alerts & deadlines + WhatsApp-style **preview** | `services/alerts.py`, dashboard | the Lakshmi “Tamil alert” story; never sent from here |
| Readiness report & Form Dossier (download) | `services/report.py`, `core/forms.py` | structured pre-application worksheet dossier |
| Tasks, application tracking, reminders | `core/tasks.py` | “saved” ≠ “sent” |
| **WhatsApp webhook & Multi-script Simulator** | `services/whatsapp*.py`, `ui/channel_view.py` | auto-detects Tamil, Hindi, Telugu, English scripts |
| **Source-change monitor** + admin approval queue + CI cron | `services/monitoring.py`, `scripts/monitor_sources.py` | detects changed pages; human approval queue |
| Browser voice input (EN/TA/HI/TE) | `ui/voice.py` | Chrome/Edge Web Speech API with language routing |
| **Master Pipeline Orchestrator** | `run_pipeline.py` | 6-stage automated health, verification, test & benchmark runner |
| KPI harness (55 eligibility + 15 extraction cases) | `evaluation/` | 100% accuracy on synthetic benchmark sets |
| **Enterprise UI/UX** | `ui/` | Day/Night theme toggle, circular ℹ️ component guides, mobile responsive |

## What is NOT done yet (say so in the demo)
Tesseract OCR for image scans (pure PDF text extraction is active) · live SMS/Twilio telecommunication runs (written, verified with simulated HMAC webhooks, not run with paid production keys) · multi-tenant enterprise auth and cloud sync (intentionally kept local and private on encrypted SQLite) · external production banking API integrations (simulated as bank-ready printable dossiers).
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
