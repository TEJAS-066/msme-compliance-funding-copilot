# MSME Compliance & Funding Copilot — Master Hackathon Roadmap (TEJAS066)

> **Team TEJAS066 • Temenos CSR & SASTRA University Hackathon Finals 2026**  
> *Theme: AI Beyond Boundaries – Innovating for a smarter, inclusive and sustainable future (SDG 9.3)*  
> **Core Principle: Rules decide. AI explains. The owner acts.**

---

## 1. Executive Summary & Strategy

The TEJAS066 project is designed specifically to win the **TEJAS 2026 Hackathon Finals** by delivering a trustworthy, mathematically grounded, and rigorously verified product rather than a fragile chatbot wrapper.

### The Four Fatal Hackathon Failure Modes We Eliminate:
1. **A Demo that Crashes**: We utilize a rock-solid, single-stack architecture (Python + Streamlit + SQLite) with an automated master pipeline (`python run_pipeline.py`) and 100% offline-capable synthetic demo mode.
2. **A Chatbot that Hallucinates**: Eligibility is evaluated by a **100% deterministic rule engine** (`core/eligibility.py`). The LLM only explains verified facts behind a strict safety guard (`services/copilot.py:guard`).
3. **Claims the Code Cannot Back Up**: All scheme data originates from official government gazettes with primary source citations in `data/schemes.json`. Unverified schemes are quarantined in a backlog.
4. **Team Members Who Cannot Explain the Architecture**: Every team member has an assigned module with a concise 60-second explanation and rehearsed Q&A responses.

---

## 2. Team Structure & Module Ownership

| Role | Name | Module Ownership | Key Deliverables |
|---|---|---|---|
| **Product & Pitch Lead** | **Nivashini K** | Demo script, presentation deck, Q&A mastery, backup video | 5-minute timed script, slide deck, rehearsal coordination, organizer communications |
| **Tech & Integration Lead** | **Sabarish R** | Master pipeline, `run_pipeline.py`, `services/copilot.py`, `llm.py`, Docker | Pipeline orchestrator, test suite maintenance, API microservice, zero-warning CI |
| **Rules & Documents Owner** | **Nandhini Chelladurai** | `core/eligibility.py`, `core/documents.py`, validation checksums | Udyam/GST extraction, Luhn Mod-36 checksum, cross-check mismatch warnings |
| **Scheme Data & Eval Owner** | **Lohitha R** | `data/schemes.json`, `evaluation/`, `docs/TRACEABILITY.md` | Gazette verification for MUDRA, CGTMSE, PMEGP, 55 evaluation benchmark cases |
| **UI & Indic Languages Owner** | **Harshini S** | `ui/`, `core/i18n.py`, Tamil/Hindi/Telugu localization | Mobile-responsive design, Day/Night toggle, circular ℹ️ component popovers, 4-language parity |

---

## 3. Four-Day Day-by-Day Execution Plan

### Day 1 (Sun 18 Oct): Foundation & Fact Verification
- **All**: Clone repo, set up virtual environment, run 169 starter tests, walk the Lakshmi demo journey.
- **Data Owner**: Verify MUDRA (`mudra.org.in`) and CGTMSE (`cgtmse.in`) against official gazette notifications; identify PMEGP criteria.
- **Tech Lead**: Set up repository branches and configure `.env` secrets.
- **Gate**: All five members can run the app locally; tests pass 100%.

### Day 2 (Mon 19 Oct): Upgrade Core Pipeline (Phases 1–3)
- **Data Owner**: Encode PMEGP with official KVIC/DC-MSME gazette sources; expand evaluation benchmark to 55 cases.
- **Rules Owner**: Implement GSTIN Luhn Mod-36 checksum and 3-state document pipeline (Upload ➔ Extract ➔ Confirm).
- **Tech Lead**: Create `scripts/check_llm.py`; benchmark Gemini/Sarvam on 10 English and 10 Tamil queries.
- **UI Owner**: Implement high-contrast Dark/Light theme toggle and 38px circular `ℹ️` page component popovers.
- **Gate**: ≥3 verified schemes passing catalogue validator; 0 failing tests.

### Day 3 (Tue 20 Oct): Channels, Integration & Rehearsal #1
- **Tech Lead**: Verify Twilio WhatsApp webhook signature verification (`services/whatsapp.py`) and standalone server.
- **All**: Bug bash — test edge cases: corrupt PDFs, state mismatches, unverified scheme queries.
- **Pitch Lead**: First timed rehearsal of the 5-minute pitch script; record Backup Video v1.
- **Gate**: Master pipeline (`python run_pipeline.py`) completes all 6 stages cleanly in under 45 seconds.

### Day 4 (Wed 21 Oct): CODE FREEZE (12:00 PM) & Stage Rehearsals
- **Until 12:00 PM**: Bug fixes only. Absolutely NO new features.
- **12:00 PM**: Hard Code Freeze. Tag release `v1.0`.
- **Afternoon**: 3 timed rehearsals with team Q&A drills; test on offline secondary laptops and mobile hotspots.
- **Gate**: Backup video and PDF slides saved on USB drive and cloud storage; offline demo verified.

### Day 5 (Thu 22 Oct): Finals Live Presentation
- **Morning**: Cold-start verification on local venue setup (`python run_pipeline.py --launch`).
- **Presentation**: Deliver 5-minute pitch highlighting Lakshmi's journey, the 3 "trust moments", and zero-hallucination guarantee.

---

## 4. Phase-by-Phase Upgrades & Delivery Matrix

| Phase | Milestone | Scope & Deliverables | Priority | Status |
|---|---|---|---|---|
| **Phase 0** | **Foundation** | Core profile Digital Twin, 3-state document pipeline, deterministic rule evaluator, SQLite database. | MUST | **DONE (100%)** |
| **Phase 1** | **Verified Data** | Official gazette facts for PMMY MUDRA, CGTMSE, and PMEGP; 55 benchmark cases; unverified schemes in backlog. | MUST | **DONE (100%)** |
| **Phase 2** | **Document Agent** | Udyam regex, GSTIN Luhn Mod-36 cryptographic checksum, 3 cross-checks (state, activity, classification). | MUST | **DONE (100%)** |
| **Phase 3** | **Live Copilot** | Grounded Indic conversational interface (EN, TA, HI, TE) with `copilot.guard()` blocking hallucinated figures. | MUST | **DONE (100%)** |
| **Phase 4** | **Omnichannel** | WhatsApp HMAC webhook handler, standalone server, interactive phone simulator, Web Speech API voice. | SHOULD | **DONE (100%)** |
| **Phase 5** | **Monitoring** | Source-change scanner (`services/monitoring.py`), portal hash comparison, admin approval queue (`review_queue.json`). | SHOULD | **DONE (100%)** |
| **Phase 6** | **Hardening** | Master orchestrator (`run_pipeline.py`), multi-stage Dockerfile, 233 automated regression tests with **0 warnings**. | MUST | **DONE (100%)** |
| **Phase 7** | **Future Pilot** | Live banking API integration, Aadhaar OTP authentication, Common Service Centre (CSC) field deployment. | LATER | **Roadmap Slide** |

---

## 5. 6-Specialized Multi-Agent Architecture

```
                  ┌───────────────────────────────────────────────┐
                  │             Business Owner (Lakshmi)          │
                  │   Web Browser (Streamlit)  /  WhatsApp Chat   │
                  └───────────────────────┬───────────────────────┘
                                          │
                        ┌─────────────────▼─────────────────┐
                        │     6-Specialized Orchestrator    │
                        │       (services/copilot.py)       │
                        └───────┬─────────┬─────────┬───────┘
                                │         │         │
          ┌─────────────────────┘         │         └─────────────────────┐
          ▼                               ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│  Document Agent  │            │ Retrieval Agent  │            │Eligibility Engine│
│core/documents.py │            │services/retrieval│            │core/eligibility  │
│• PDF extraction  │            │• Official gazette│            │• 100% Determin-  │
│• Luhn Mod-36 GST │            │  circular search │            │  istic evaluation│
│• Cross-checks    │            │• Intent mapping  │            │• 0% Hallucination│
└──────────────────┘            └──────────────────┘            └──────────────────┘
          │                               │                               │
          ├───────────────────────────────┼───────────────────────────────┤
          ▼                               ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│    Form Agent    │            │  Deadline Agent  │            │ Monitoring Agent │
│  core/forms.py   │            │  core/tasks.py   │            │services/monitor  │
│• Auto-fills 9/11 │            │• Statutory alerts│            │• Portal crawler  │
│  bank fields     │            │• WhatsApp preview│            │• Admin approval  │
│• Bank-ready PDF  │            │• "Saved ≠ Sent"  │            │  gatekeeper      │
└──────────────────┘            └──────────────────┘            └──────────────────┘
```

---

## 6. Five-Minute Pitch Script & Trust Moments

| Time | Action & Screen | Verbal Script & "Trust Moments" |
|---|---|---|
| **0:00 – 0:30** | Slide 1–2 / Problem Statement | *"Meet Lakshmi, a micro-textile manufacturer in Tiruppur. She is eligible for ₹10 Lakhs in collateral-free funding, but circular complexity and fear of bank rejection keep her locked out. Most AI bots hallucinate loan approvals; our solution guarantees: Rules decide, AI explains, and the owner acts."* |
| **0:30 – 1:00** | Dashboard → Click **Load Lakshmi (DEMO)** | *"With one click, we load Lakshmi's synthetic Digital Twin. Notice the banner: all data is private, local, and synthetic. Missing facts stay UNKNOWN—we never guess."* **[Trust Moment #1: Honest Data Integrity]** |
| **1:00 – 2:00** | Documents → Upload Udyam & GST Samples | *"Watch our Document Agent: it extracts her Udyam number in 1 second, runs a mathematical Luhn Mod-36 checksum on her GSTIN, and warns her of a state mismatch before she ever steps into a bank."* **[Trust Moment #2: Pre-Submission Fraud Prevention]** |
| **2:00 – 3:00** | Schemes & Eligibility Matrix | *"Our rules engine evaluates MUDRA, CGTMSE, and PMEGP criterion-by-criterion with official Gazette citations. When we adjust her loan amount, the eligibility badge updates deterministically—zero LLM guessing."* |
| **3:00 – 4:00** | Copilot Chat (English ➔ Tamil) | *"Lakshmi asks in Tamil: 'எனக்கு MUDRA தகுதி உள்ளதா?' The Copilot explains her exact standing in pure Tamil, citing Ministry of MSME circulars. If asked for unverified schemes or loan guarantees, it strictly refuses."* **[Trust Moment #3: Grounded Safety Guard]** |
| **4:00 – 4:30** | Bank Forms & Statutory Tasks | *"Instead of hours of manual paperwork, our Form Agent auto-fills 9 out of 11 fields on the standard MSME Bank Worksheet, compiling an official printable PDF dossier with branch endorsement blocks."* |
| **4:30 – 5:00** | Admin View & KPI Benchmarks | *"In our Admin panel, portal policy updates require human verification before notifying users. Our automated test harness proves 100% eligibility accuracy (55/55) and 0% hallucinations across 233 passing tests. Thank you."* |

---

## 7. Judge Q&A Bank (14 Hard Questions & Exact Responses)

#### Q1: "What if your AI hallucinates a loan amount or promises approval?"
> **Answer**: *"Our LLM never decides eligibility. Eligibility is calculated by a 100% deterministic rule engine in `core/eligibility.py` using version-controlled gazettes in `data/schemes.json`. The LLM only rewords the rule output, and every response passes through `copilot.guard()`. Any unverified number or promise immediately triggers a fallback to deterministic text."*

#### Q2: "How accurate is your model? Your slide claims 90%."
> **Answer**: *"90% is our target for real-world field pilots. Today, we prove 100% accuracy on our automated regression suite of 55 hand-labelled eligibility cases and 15 document extraction samples across 233 automated pytest checks."*

#### Q3: "Why not just use ChatGPT or a WhatsApp wrapper?"
> **Answer**: *"A general chatbot has no knowledge of your documents, cannot perform cryptographic Luhn checksums, invents outdated subsidy percentages, and cannot be audited by a bank. We combine deterministic rules with explainable AI."*

#### Q4: "How do you keep scheme information up to date?"
> **Answer**: *"Every scheme in `data/schemes.json` tracks `last_verified`, `source_ids`, and `review_status`. Our Monitoring Agent scans official government portals for hash changes and queues updates for human administrator approval before any business owner is notified."*

#### Q5: "How is this different from government portals like myScheme?"
> **Answer**: *"myScheme is a citizen-level discovery portal. We take the business owner from discovery to application readiness: extracting verified facts from Udyam PDFs, flagging state/PAN discrepancies, generating bank worksheets, and tracking compliance deadlines."*

#### Q6: "Does your tool actually submit applications to government portals?"
> **Answer**: *"No, and we explicitly disclose this to users. Government portals require Aadhaar OTP and biometric authentication. We prepare an official, audit-ready Bank Worksheet Dossier so the entrepreneur walks into the bank completely prepared."*

#### Q7: "How do you ensure data privacy for sensitive business financials?"
> **Answer**: *"All business data is stored locally in an encrypted SQLite database on the owner's machine. Documents are parsed locally via text extraction. No customer financial documents are ever sent to an external LLM."*

#### Q8: "How do you handle micro-entrepreneurs who cannot read English?"
> **Answer**: *"Our entire platform offers full bilingual and multilingual parity across English, Tamil, Hindi, and Telugu (275 keys each). Users can speak via Web Speech API or chat in Tamil script over WhatsApp."*

---

## 8. Say vs. Don't Say Guardrails

| What You CAN Say | What You Must NOT Say |
|---|---|
| *"Rules decide, AI explains, the owner acts."* | *"Our AI automatically approves or guarantees loans."* |
| *"100% accurate across 55 hand-labelled benchmark cases."* | *"Our AI is 90% accurate in real-world commercial banking."* |
| *"Reminders and WhatsApp alerts are previewed in-app."* | *"We sent live WhatsApp messages to millions of phones."* |
| *"We generate an official printable Bank Loan Worksheet."* | *"We auto-submitted the application to the Ministry portal."* |
| *"3 verified schemes backed by Gazette of India citations."* | *"We have indexed all 500 government schemes."* |
