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
| **Phase 3** | Multilingual Expansion (Hindi & Telugu) | **DONE** | Hindi & Telugu integration in `core/i18n.py`, `core/i18n_hi.py`, `core/i18n_te.py`, and UI selector |
| **Phase 4** | Multi-Agent Form Generator | **DONE** | Authentic GovTech loan application worksheet dossier in `ui/forms_view.py` and `core/forms.py` |
| **Phase 5** | WhatsApp & Voice Polish | **DONE** | Native phone-bezel WhatsApp simulator with multi-script auto-detection & Web Speech locale routing |
| **Phase 6** | Finals Pitch & Live KPI Dashboard | **DONE** | Jury Evaluation Telemetry panel on Admin page proving 100% eligibility & 100% extraction |
| **Phase 7** | Dynamic 5-Stage Stepper & Lakshmi Simulator | **DONE** | Pure deterministic stage engine (`core/insights.py`), live Document Agent verification & WhatsApp popover |
| **Phase 8** | Multilingual Channel Inquiries & Voice | **DONE** | 1-click prompt chips in WhatsApp simulator, voice input embedding, cross-lingual keyword matching |
| **Phase 9** | Bank-Ready PDF Dossier Generator | **DONE** | In-memory ReportLab PDF generator (`services/report.py`), branch endorsement block, 1-click download in `ui/forms_view.py` |

### Phase 9 Changelog (Completed)
- **Official Bank-Ready PDF Dossier Generator (`services/report.py`)**: Built `generate_pdf_dossier()` creating a formal, publication-quality A4 PDF dossier in memory with 4 structured sections:
  - *Section A*: Enterprise Digital Twin & Business Identity (declared vs extracted facts, 2025 MSME composite limits).
  - *Section B*: Statutory Eligibility & Rule Evaluation (PASS / FAIL / UNKNOWN status table with exact thresholds).
  - *Section C*: Documentation Checklist & Verification (Udyam, GST, DPR, advisory items).
  - *Section D*: Branch Endorsement & Submission Sign-Off (Signature lines, Branch stamp block, review recommendation).
- **1-Click PDF Download (`ui/forms_view.py`)**: Added primary action button `btn_download_pdf` alongside text worksheet downloads.
- **Full Multilingual Parity**: Added `btn_download_pdf` to `core/i18n.py` (EN/TA), `core/i18n_hi.py` (HI), and `core/i18n_te.py` (TE).
- **Automated Regression Suite**: Added `test_pdf_dossier_generation` in `tests/test_alerts_report.py`. **233 unit/integration tests passing**.

### Phase 8 Changelog (Completed)

- **1-Click WhatsApp Quick Inquiries (`ui/channel_view.py`)**: Embedded 4 responsive prompt chips (*MUDRA Eligibility, CGTMSE Documents, PMEGP Subsidy, Clear Chat*) directly into the simulator, allowing jury members to test multi-turn conversations instantly in English, தமிழ், हिन्दी, or తెలుగు.
- **Embedded Voice Recognition (`ui/channel_view.py`)**: Integrated `voice.render()` directly into the channel interface, enabling Web Speech API voice dictation mapped to `en-IN`, `ta-IN`, `hi-IN`, and `te-IN`.
- **Cross-Lingual Intent & Keyword Matching (`data/schemes.json`, `services/copilot.py`)**: Added Hindi (`मुद्रा`, `सीजीटीएमएसई`, `पीएमईजीपी`) and Telugu (`ముద్ర`, `సిజిటిఎంఎస్ఇ`, `పిఎంఇజిపి`) keywords to verified schemes in `data/schemes.json` and unlocked 4-language deterministic explanation in `services/copilot.py:answer`.

### Phase 7 Changelog (Completed)

- **Deterministic 5-Stage Stepper Engine (`core/insights.py`)**: Built `compute_active_stage(profile, confirmed_types, tasks, apps)` to dynamically transition the UI across the 5 project stages:
  - *Stage 1 (Understand)*: Uninitialized / empty digital twin.
  - *Stage 2 (Profile)*: Partial profile undergoing owner data entry.
  - *Stage 3 (Match)*: Digital twin established, matching schemes identified, missing documents highlighted (Lakshmi's initial state).
  - *Stage 4 (Prepare)*: Required documents uploaded and confirmed (Udyam certificate confirmed), dossier ready.
  - *Stage 5 (Track)*: Active tasks tracked with due dates or applications submitted outside the app.
- **Interactive Lakshmi Simulation Actions (`ui/dashboard.py`)**:
  - `btn_sim_udyam` (*"⚡ Run Document Agent (Verify Udyam Certificate)"*): 1-click execution that extracts `UDYAM-TN-02-0000123` from `samples/sample_udyam_lakshmi.pdf`, updates Lakshmi's profile from 12 to 15 known fields, marks Udyam as confirmed in DB, and dynamically advances the stepper to Stage 4.
  - `btn_sim_wa` (*"📱 Preview Lakshmi's WhatsApp Notification"*): Interactive localized WhatsApp channel popover previewing Lakshmi's proactive funding notification in Tamil, Hindi, Telugu, or English.
- **Full Multilingual Parity**: Added all 5 simulation keys to `core/i18n.py` (EN/TA), `core/i18n_hi.py` (HI), and `core/i18n_te.py` (TE) with 100% script and placeholder parity.
- **Test Suite Updates**: Added `test_compute_active_stage` in `tests/test_insights.py`. All 232 tests passing.

### Phase 6 Changelog (Completed)
- **Jury Evaluation Telemetry Panel (`ui/admin_view.py`)**: Built an executive evaluation card directly on the Admin page presenting automated proof of the targets pitched in Round 2:
  - Eligibility Accuracy: Target $\ge 90\%$ $\rightarrow$ **100% (55/55 passed)**
  - Extraction Accuracy: Target $\ge 90\%$ $\rightarrow$ **100% (15/15 passed)**
  - Hallucination Rate: Target $0\%$ $\rightarrow$ **0% (100% deterministic rules)**
  - Specialized AI Agents: **6 / 6 Operational** (Document, Retrieval, Eligibility, Form, Deadline, Monitoring).


### Phase 5 Changelog (Completed)
- **Multi-Script WhatsApp Routing (`services/channel.py`, `services/whatsapp.py`)**: Expanded `detect_language` to automatically identify Tamil, Devanagari (Hindi), and Telugu unicode ranges, responding automatically in the user's native script.
- **Multilingual Greetings**: Added Hindi (`नमस्ते`, `प्रणाम`) and Telugu (`నమస్కారం`) to instant greeting router.
- **Browser Speech Recognition Locales (`ui/voice.py`)**: Mapped voice input to `en-IN`, `ta-IN`, `hi-IN`, and `te-IN`.

### Phase 4 Changelog (Completed)
- **Authentic GovTech Dossier Layout (`ui/forms_view.py`)**: Transformed raw field lists into a structured, dual-column loan application dossier with readiness score indicator (`ready_pct%`), pre-filled metrics, and clear warnings for missing fields.
- **Multilingual Worksheets (`core/forms.py`)**: Added full English, Tamil, Hindi, and Telugu labels and hints, eliminating `KeyError` crashes on non-English locales.

### Phase 3 Changelog (Completed)
- **Multilingual Architecture (`core/i18n.py`, `core/i18n_hi.py`, `core/i18n_te.py`)**: Preserved `TR` English/Tamil tuple structure to guarantee 100% backward compatibility while integrating complete 275-key dictionaries for Hindi (`TR_HI`) and Telugu (`TR_TE`).
- **Profile Field & Option Labels**: Added Hindi & Telugu translations for all 18 business profile fields and select options in `core/profile.py`.
- **4-Language UI Selector (`app.py`)**: Added English, தமிழ், हिन्दी, and తెలుగు to the sidebar language switcher.
- **Intent Recognition (`services/retrieval.py`)**: Extended `INTENT_WORDS` with Hindi and Telugu keywords for eligibility, documents, amounts, next steps, deadlines, and forms.
- **Multilingual Unit Tests (`tests/test_i18n.py`)**: Added automated validation confirming 100% script parity and placeholder matching across all 275 keys.

### Phase 2 Changelog (Completed)
- **PMEGP Promoted to Verified Scheme (`data/schemes.json`)**: Added official scheme definition with primary sources (`kvic_pmegp_guidelines` & `msme_pmegp_portal`).
- **PMEGP Rules Encoded**: Micro-enterprise restriction, non-farm activity requirement, corporate entity exclusion, ₹50L manufacturing / ₹20L service cost ceilings, and Special Category subsidies (up to 35% margin money & 5% own contribution for women/rural entrepreneurs like Lakshmi).
- **Keyword Hygiene**: Cleaned generic keywords like "subsidy" to prevent intent collisions with unverified backlog schemes.
- **UI Schemes View (`ui/schemes_view.py`)**: Added `PMEGP` metric chip and interactive criteria inspection across all 3 schemes.
- **Evaluation Benchmark Expansion (`evaluation/cases.json`)**: Scaled eligibility benchmark from 34 to 55 test cases, achieving **100% (55/55)** accuracy.
- **Test Suite Updates**: 231 unit/integration tests passing (`python -m pytest -q`).

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

Run the master pipeline orchestrator for full automated verification:

```bash
# 1. Master Pipeline Orchestrator (All 6 stages: env, catalogue, 6 agents, pytest, eval)
python run_pipeline.py

# 2. Master Pipeline with auto-launch of Streamlit UI
python run_pipeline.py --launch

# 3. Interactive Lakshmi demo journey in terminal
python run_pipeline.py --demo

# 4. Interactive WhatsApp simulator in terminal
python run_pipeline.py --wa

# 5. Direct test commands
python -m pytest -q                 # 233 tests (0 failed)
python -m evaluation.run_eval       # 100% eligibility (55/55) & 100% extraction (15/15)


```

---

## 6. How to Continue as an AI Assistant

If you are a new AI taking over this conversation:
1. Run `python -m pytest -q` first to confirm system health.
2. Check Section 4 above for the current Phase in progress.
3. Keep code strictly adhering to Section 1 (Core Rules).
4. Update this document (`HANDOVER_MASTER.md`) with your completed work before ending your turn.
