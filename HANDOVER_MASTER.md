# MSME Compliance & Funding Copilot — Master Project & AI Handover State

> **CRITICAL DIRECTIVE FOR ANY AI ASSISTANT WORKING ON THIS PROJECT:**
> This project is competing in the **TEJAS 2026 Hackathon Finals (Temenos CSR & SASTRA University)** by **Team TEJAS066**.
> We must **strictly fulfill the commitments** made in Round 1 (`TEJAS066.docx`) and Round 2 (`Subtitle_video_presentation.txt` & Canva Presentation).
> Read this file **first** before making any modifications.

---

## 1. Non-Negotiable Core Rules (Do Not Violate)

1. **"Rules decide. AI explains. The owner acts."**
   - Eligibility is **100% deterministic** (`core/eligibility.py`). The LLM **never** decides eligibility.
   - The LLM is strictly used for layman explanation and natural language interface behind a safety guard (`services/copilot.py:guard`).
2. **Every scheme fact must have primary sources**:
   - Facts live in `data/schemes.json` with `source_ids`, `last_verified`, `review_status`.
   - Never invent criteria, URLs, deadlines, amounts, or subsidies. If unverified, keep in backlog or mark `review_status: unverified`.
3. **Unknown stays UNKNOWN**:
   - Never treat missing profile information as `PASS`. It must remain `UNKNOWN`.
4. **No fake successes**:
   - Never claim an application is "submitted", "sent", or "approved" unless verified through live API / user action. Form downloads are worksheets, not submissions.
5. **Strict Bilingual / Multilingual Parity**:
   - Every user-visible string goes through `core/i18n.py`.
   - Automated tests (`tests/test_i18n.py`) enforce that every key has non-empty English and valid Tamil script with identical format placeholders `{placeholder}`.
6. **Architectural Separation**:
   - `core/`: Pure business logic, 0 network, 0 Streamlit dependencies.
   - `services/`: IO, retrieval, notifications, WhatsApp webhook, monitoring.
   - `ui/`: Streamlit presentation only. No business rules in `ui/`.
7. **Regression Testing**:
   - All tests in `tests/` must pass (`python -m pytest -q`).
   - The KPI evaluation harness (`python -m evaluation.run_eval`) must maintain 100% on synthetic benchmarks.

---

## 2. Project Proposal Context (Round 1 & Round 2)

- **Team ID**: TEJAS066
- **Theme**: AI Beyond Boundaries – Innovating for a smarter, inclusive and sustainable future
- **SDG Alignment**: SDG 9.3 (Increase access of small-scale industrial and other enterprises to financial services and credit)
- **Core Narrative / Persona**: **Lakshmi**, small business owner of a textile manufacturing micro-enterprise in Tiruppur, Tamil Nadu. She receives a Tamil alert about MUDRA/CGTMSE/PMEGP, identifies a missing document, and uses her dashboard and WhatsApp to take action before the deadline.
- **5-Stage Methodology**:
  1. **Understand**: Plain-language conversational discovery & scheme catalog exploration.
  2. **Profile**: Building the "Business Digital Twin" (investment, turnover, category, location, entity type).
  3. **Match**: Deterministic eligibility evaluation + what-if tipping points + information-gain next best actions.
  4. **Prepare**: Document upload, OCR/checksum validation, cross-check advisory, and bank worksheet generation.
  5. **Track**: To-Do list, application status tracking, and deadline reminders over Web and WhatsApp.
- **6 Specialized AI Agents** (Slide 5 of Round 2):
  1. *Document Agent*: Extracts details from Udyam, GST, and invoices; runs checksums and cross-checks.
  2. *Retrieval Agent*: RAG grounded in official circulars and verified government schemes.
  3. *Eligibility Agent*: Deterministic rule evaluation matching the digital twin against encoded limits.
  4. *Form Agent*: Helps owners fill complex loan applications & generates readiness worksheets.
  5. *Deadline Agent*: Tracks tasks, application milestones, and issues timely reminders.
  6. *Monitoring Agent*: Scans official portals for policy changes; queues items for human admin review.

---

## 3. Architecture & File Structure

```
├── app.py                      # Main Streamlit application shell & stage navigation
├── core/                       # Pure logic, completely decoupled from UI
│   ├── catalogue.py            # Scheme catalogue reader & validator
│   ├── checklist.py            # Document checklist builder (verified vs unverified)
│   ├── db.py                   # SQLite persistence layer (profile, documents, tasks, reviews)
│   ├── documents.py            # Upload, text extraction, GSTIN/Udyam validation, cross-checks
│   ├── eligibility.py          # Deterministic eligibility engine (PASS/FAIL/UNKNOWN/N-A)
│   ├── forms.py                # Loan preparation worksheet generator
│   ├── i18n.py                 # Bilingual/multilingual strings (EN, TA, + HI/TE hooks)
│   ├── insights.py             # Next-best-action, tipping tables, counterfactuals
│   ├── profile.py              # Business Digital Twin management
│   └── tasks.py                # Task tracking & deadline management
├── services/                   # Orchestration, external I/O & agents
│   ├── alerts.py               # Actionable alert generation & WhatsApp preview builder
│   ├── channel.py              # Multi-channel adapter
│   ├── copilot.py              # Bilingual conversational assistant with safety guard & module trace
│   ├── llm.py                  # Multi-provider LLM adapter (Anthropic, Gemini, Sarvam, Demo)
│   ├── monitoring.py           # Web portal change scanner & admin approval queue
│   ├── notifications.py        # Twilio SMS / WhatsApp dispatcher
│   ├── report.py               # Readiness report generator (HTML/print-friendly)
│   ├── retrieval.py            # Structured retrieval from official sources
│   └── whatsapp.py             # Official Twilio WhatsApp webhook handler with HMAC verification
├── ui/                         # Streamlit views (Human-crafted GovTech design system)
│   ├── common.py               # CSS injection, 5-stage stepper, agent status cards, badges
│   ├── dashboard.py            # Executive dashboard, Lakshmi journey walkthrough, metrics
│   ├── profile_view.py         # Business Digital Twin editor
│   ├── documents_view.py       # Document upload, extraction findings, cross-check alerts
│   ├── schemes_view.py         # Schemes & eligibility viewer + tipping point analysis
│   ├── checklist_view.py       # Document checklist & status
│   ├── chat_view.py            # Grounded Copilot chat with agent trace inspection
│   ├── channel_view.py         # Interactive WhatsApp phone simulator
│   ├── forms_view.py           # Bank loan application worksheet preview & download
│   ├── tasks_view.py           # To-Do list, application status & deadline calendar
│   └── admin_view.py           # Policy change review queue & KPI harness dashboard
├── data/                       # Verified single-source-of-truth datasets
│   ├── schemes.json            # Official scheme criteria, benefits, documents, sources
│   ├── demo_profile.json       # Lakshmi (Tiruppur textile) reference profile
│   └── review_queue.json       # Policy change queue items for admin verification
├── docs/                       # Specifications & traceability
│   ├── CONTRACTS.md            # Immutable data schemas for profile, schemes, findings
│   ├── TRACEABILITY.md         # Promise-by-promise audit against proposal
│   └── WHATSAPP.md             # Twilio WhatsApp webhook setup guide
└── tests/                      # Automated test suite (224+ tests)
```

---

## 4. Phase Plan & Execution Tracking

| Phase | Description | Status | Key Deliverables |
|---|---|---|---|
| **Phase 0** | Starter Foundation | **DONE** | Core rules, 224 unit tests, SQLite DB, basic Streamlit UI |
| **Phase 1** | Human-Crafted GovTech UI & 5-Stage Stepper | **DONE** | Custom CSS design system, 5-stage workflow stepper, Lakshmi demo tour card, multi-agent status bar |
| **Phase 2** | Scheme Catalogue Expansion | **DONE** | Add PMEGP (KVIC official rules) to `data/schemes.json` + evaluation cases |
| **Phase 3** | Multilingual Expansion | **NEXT UP** | Hindi & Telugu integration in `core/i18n.py` and UI selector |
| **Phase 4** | Multi-Agent Form Generator | **PENDING** | Formal MUDRA/CGTMSE printable loan application worksheet |
| **Phase 5** | WhatsApp & Voice Polish | **PENDING** | Native phone-bezel WhatsApp simulator + browser voice input |
| **Phase 6** | Finals Pitch & Live KPI Dashboard | **PENDING** | One-click judge evaluation panel showing $100\%$ determinism & KPI targets |

### Phase 2 Changelog (Completed)
- **PMEGP Promoted to Verified Scheme (`data/schemes.json`)**: Added official scheme definition with primary sources (`kvic_pmegp_guidelines` & `msme_pmegp_portal`).
- **PMEGP Rules Encoded**: Micro-enterprise restriction, non-farm activity requirement, corporate entity exclusion, ₹50L manufacturing / ₹20L service cost ceilings, and Special Category subsidies (up to 35% margin money & 5% own contribution for women/rural entrepreneurs like Lakshmi).
- **Keyword Hygiene**: Cleaned generic keywords like "subsidy" to prevent intent collisions with unverified backlog schemes.
- **UI Schemes View (`ui/schemes_view.py`)**: Added `PMEGP` metric chip and interactive criteria inspection across all 3 schemes.
- **Evaluation Benchmark Expansion (`evaluation/cases.json`)**: Scaled eligibility benchmark from 34 to 55 test cases, achieving **100% (55/55)** accuracy.
- **Test Suite Updates**: 225 unit/integration tests passing (`python -m pytest -q`).

### Phase 1 Changelog (Completed & Hardened)
- **UI Code-Leak Hardening**: Diagnosed and eliminated markdown-it code-block leakage where 4-space indented HTML/CSS strings were parsed as `<pre><code>`. Migrated custom cards and components to 100% native Streamlit components (`st.container(border=True)`, `st.columns`, `st.caption`) and `st.html()` for CSS injection.
- **Full 10-Page Programmatic Audit**: Verified via automated `AppTest` crawl across all 10 views (`nav_dashboard` through `nav_admin`) that **zero** raw code blocks, zero unescaped `<pre>/<code>` tags, and zero broken DOM elements exist.
- **5-Stage Methodology Stepper (`ui/common.py`)**: Implemented responsive, native-card `render_stepper()` displaying the 5 stages (*Understand ➔ Profile ➔ Match ➔ Prepare ➔ Track*) reflecting Round 2 Slide 4.
- **Lakshmi Demo Walkthrough (`ui/dashboard.py`)**: Added an interactive tour card allowing one-click activation of Lakshmi's Tiruppur micro-textiles scenario, matching Round 2 Slide 6.
- **Multi-Agent Architecture Inspector (`ui/common.py`, `ui/dashboard.py`)**: Surfaced the 6 specialized AI agents (*Document, Retrieval, Eligibility, Form, Deadline, Monitoring*) with live status chips directly on the dashboard.
- **Strict Bilingual Verification (`core/i18n.py`)**: Added all new English & Tamil keys with complete Tamil script and placeholder parity; verified by `tests/test_i18n.py`.
- **Testing Verification**: All 224 tests passing (`python -m pytest -q`) and KPI evaluation at 100% (`python -m evaluation.run_eval`).

---

## 5. Verification Commands

Run these commands to verify any changes before committing:

```bash
# 1. Run all unit and integration tests (must be 224+ passed, 0 failed)
python -m pytest -q

# 2. Run KPI evaluation harness on synthetic datasets (must be 100% eligibility & extraction)
python -m evaluation.run_eval

# 3. Smoke test the Streamlit UI
python -m pytest tests/test_ui_smoke.py

# 4. Verify i18n parity
python -m pytest tests/test_i18n.py
```

---

## 6. How to Continue as an AI Assistant

If you are a new AI taking over this conversation:
1. Run `python -m pytest -q` first to confirm system health.
2. Check Section 4 above for the current Phase in progress.
3. Keep code strictly adhering to Section 1 (Core Rules).
4. Update this document (`HANDOVER_MASTER.md`) with your completed work before ending your turn.
