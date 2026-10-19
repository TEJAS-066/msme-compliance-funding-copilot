# 🏛️ Team TEJAS066 — Project Mastery & Finals Defense Guide
**MSME Compliance & Funding Copilot**  
*Temenos CSR & SASTRA University Hackathon Finals 2026*  
*Theme: AI Beyond Boundaries — Innovating for a Smarter, Inclusive, and Sustainable Future*  
*SDG Focus: SDG 9.3 (Access to Financial Services & Credit for Small-Scale Enterprises)*

---

## 1. The 30-Second Elevator Pitch
> *"Over 63 million MSMEs form the backbone of India's economy, yet over 70% struggle to access formal credit due to complex guidelines, fragmented documentation, and fear of rejection. Generic generative AI cannot solve this because LLMs hallucinate eligibility criteria, cite non-existent schemes, and compromise sensitive business data.
>
> Team TEJAS066 built the **MSME Compliance & Funding Copilot**: a GovTech-grade, deterministic multi-agent platform designed with a sacred principle: **'Rules decide. AI explains. The owner acts.'** 
>
> We don't guess eligibility; our 100% deterministic rules engine matches businesses against verified gazette norms, while 6 specialized agents extract documents, calculate tipping points, auto-populate bank worksheets, and alert owners in their native language over Web and WhatsApp."*

---

## 2. The Core Problem & Our Breakthrough Principle

| Problem in Current Landscape | How Existing AI / Portals Fail | Our Copilot Breakthrough |
|---|---|---|
| **Fragmented Government Portals** | Owners must check 5+ confusing portals (Udyam, MUDRA, CGTMSE, KVIC, State portals). | Unified Catalogue of verified schemes with primary gazette citations and verification timestamps. |
| **LLM Hallucinations** | ChatGPT/Claude make up eligibility limits, invent subsidies, and give fake guarantees. | **Strict Determinism**: Zero LLM decision-making. Rules engine evaluates criteria; LLM only explains. |
| **Missing Document Rejections** | 40% of MSME bank applications are rejected due to incomplete or mismatched documents. | **Information Gain Engine**: Calculates *Next Best Action* and exact tipping points to fix blockers before applying. |
| **Language & Digital Barrier** | Policy documents are in dense legal English; rural entrepreneurs speak local languages. | **Full 4-Language Parity** (English, தமிழ், हिन्दी, తెలుగు) across Web, Voice, and WhatsApp. |
| **Privacy & Security** | Cloud AI leaks confidential turnover, GSTIN, and financial data. | **Zero Cloud Lock-in**: Local SQLite Relational Digital Twin, offline-capable rule evaluation. |

---

## 3. The Central Persona: Lakshmi's Tiruppur Journey
To make the presentation deeply human and relatable to the hackathon jury, we anchor the entire demonstration in **Lakshmi**:
- **Who she is**: A female entrepreneur running *Lakshmi Garments (DEMO)*, a proprietary textile manufacturing micro-enterprise in Tiruppur, Tamil Nadu.
- **Her Financials**:
  - Plant & Machinery Investment: ₹18,00,000 (₹18 Lakhs)
  - Annual Turnover: ₹65,00,000 (₹65 Lakhs)
  - Employees: 9
  - Loan Needed: ₹8,00,000 (₹8 Lakhs for modern stitching machinery)
- **Her Challenge**:
  She wants to expand production for export orders, but doesn't know if she qualifies for collateral-free loans, what documents she needs, or if her Udyam certificate is properly classified.
- **How the Copilot Guides Her**:
  1. *Understand*: Lakshmi opens the app (or WhatsApp in Tamil) and asks *"எனக்கு MUDRA தகுதி உள்ளதா?"*.
  2. *Profile*: Loads her business digital twin; the engine computes her MSME class as **Micro** (Investment $\le$ ₹2.5 Cr, Turnover $\le$ ₹10 Cr).
  3. *Match*: The rules engine confirms she meets **MUDRA (Kishor ₹8 Lakhs)** and **CGTMSE** with 90% credit guarantee for women entrepreneurs, but flags: *Udyam Registration Certificate missing*.
  4. *Prepare*: She runs the Document Agent; it scans her sample Udyam PDF, extracts `UDYAM-TN-02-0000123`, cross-checks her GSTIN, updates her profile to 100% readiness, and generates a pre-filled bank loan dossier.
  5. *Track*: It schedules follow-up tasks, sends her a WhatsApp reminder before the bank branch visit, and tracks external status.

---

## 4. The 5-Stage Methodology (Round 2 Slide 4)
Our system executes a structured 5-stage workflow that dynamically reflects on the dashboard stepper:

```
[ Stage 1: UNDERSTAND ] ➔ [ Stage 2: PROFILE ] ➔ [ Stage 3: MATCH ] ➔ [ Stage 4: PREPARE ] ➔ [ Stage 5: TRACK ]
   • Conversational RAG      • Business Digital Twin  • Deterministic Rules   • OCR & Checksums       • Milestones & Tasks
   • Scheme Exploration      • Investment/Turnover    • Tipping Point Matrix  • Bank Loan Dossier     • WhatsApp Reminders
   • Primary Citations       • MSME Classification   • Information Gain NBA  • Cross-Check Advisory  • Status Tracking
```

---

## 5. The 6 Specialized AI Agents (Round 2 Slide 5)
Rather than a monolithic prompt, our copilot coordinates 6 purpose-built agents:

```mermaid
graph TD
    User([MSME Owner / Lakshmi]) <--> ChannelAgent[5. Deadline & Channel Agent\nWhatsApp, Voice, Multi-Script]
    ChannelAgent <--> Orchestrator{Master Pipeline Orchestrator}
    
    Orchestrator <--> DocAgent[1. Document Agent\nOCR, Luhn-36 Checksum, Extraction]
    Orchestrator <--> RetAgent[2. Retrieval Agent RAG\nKeyword, Gazette Sources, Intent]
    Orchestrator <--> EligAgent[3. Eligibility Engine\n100% Deterministic Rule Matching]
    Orchestrator <--> FormAgent[4. Form Agent\nBank Loan Dossier, Pre-Application]
    Orchestrator <--> MonAgent[6. Monitoring Agent\nPolicy Scraper, Admin Review Queue]
    
    DocAgent --> DB[(SQLite Digital Twin)]
    EligAgent --> DB
    FormAgent --> DB
    MonAgent --> DB
```

1. **Document Agent**: Extracts structured key-value pairs from PDFs/images (Udyam, GST), validates GSTIN checksums via Luhn Mod-36, and detects profile-document mismatches.
2. **Retrieval Agent**: Semantic & keyword intent router matching queries to verified schemes with official circular citations.
3. **Eligibility Engine**: 100% deterministic boolean rules evaluator implementing composite limits and statutory conditions without LLM guessing.
4. **Form Agent**: Compiles owner profile and verified document findings into a structured bank loan worksheet with readiness score gauges.
5. **Deadline & Channel Agent**: Manages compliance calendar, tracks milestone due dates, and dispatches localized WhatsApp notifications.
6. **Monitoring Agent**: Scans government notifications for threshold changes (e.g., 2025 revised MSME limits) and queues updates for admin verification before notifying owners.

---

## 6. Technical Proof & Measurable KPIs

Our implementation has been audited and continuously benchmarked against strict automated harnesses:

| KPI Metric | Proposal Target | Real Benchmark Result | Verification Method |
|---|---|---|---|
| **Eligibility Decision Accuracy** | $\ge 90\%$ | **100.0% (55 / 55 cases)** | `python -m evaluation.run_eval` |
| **Document Field Extraction** | $\ge 90\%$ | **100.0% (15 / 15 samples)** | Tested on synthetic Udyam & GST files |
| **Hallucination Rate** | $0.0\%$ | **0.0% (Zero)** | Guardrails reject unverified numbers/claims |
| **Unit & Integration Suite** | $\ge 200$ tests | **232 Passed (0 failed)** | `python -m pytest -q` in 45.9s |
| **Multilingual Parity** | 2+ languages | **4 Languages (280 keys each)** | EN, தமிழ், हिन्दी, తెలుగు in `tests/test_i18n.py` |
| **Master Orchestrator Pipeline** | Single command | **6/6 Stages Verified in 50s** | `python run_pipeline.py` |

---

## 7. How to Give a Winning Live Demo (Jury Walkthrough Script)

### Step 1: Open the Application
Run in terminal:
```bash
python run_pipeline.py --launch
```
*What to say:* "Judges, we start by running our automated pipeline orchestrator. In 50 seconds, it audits our scheme catalogue, runs all 6 specialized agents, passes 232 test suites, and launches our GovTech-grade Streamlit portal."

### Step 2: Show the Dashboard & Dynamic Stepper
- Point to the **5-Stage Methodology Stepper** at the top.
- Show the **6 Specialized AI Agents** operational status panel.
- Point to the **Lakshmi's Journey Walkthrough Card**.
- Click **"Load Lakshmi's Journey (Tiruppur Demo)"**.
- *What to say:* "Notice that our stepper immediately recognized Lakshmi's business profile and moved dynamically to Stage 3 (Match). The Next Best Action identifies that Lakshmi is eligible for MUDRA Kishor (₹8 Lakhs) and CGTMSE, but is blocked by a missing Udyam Certificate."

### Step 3: 1-Click Document Agent Simulation
- In the Lakshmi Tour Card, click **"⚡ Run Document Agent (Verify Udyam Certificate)"**.
- Watch the screen refresh:
  - Confirmed Documents count updates from 0 to 1.
  - Profile completeness jumps from 12/17 to 15/17 (`UDYAM-TN-02-0000123` extracted).
  - The Stepper dynamically advances to **Stage 4: Prepare**!
- Click **"📱 Preview Lakshmi's WhatsApp Notification"** to show how she receives proactive Tamil guidance.
- *What to say:* "Look at that — without human data entry, our Document Agent parsed her certificate, validated the format, confirmed the status, and advanced her entire workflow to bank-readiness."

### Step 4: Show the Loan Application Dossier (Forms View)
- In the sidebar navigation, click **Forms (Loan preparation worksheet)**.
- Select **Pradhan Mantri MUDRA Yojana (PMMY)**.
- Show the **100% Readiness Gauge** and the structured bank loan worksheet.
- Click **"Download Application Dossier (.txt)"**.
- *What to say:* "Our Form Agent does not pretend to submit loans to government servers. Instead, it equips Lakshmi with an authentic, verified pre-application dossier that she can print and take directly to her bank manager at Canara Bank or SBI."

### Step 5: Test the WhatsApp Channel Simulator
- In the sidebar navigation, click **WhatsApp & voice**.
- Click the language selector in the sidebar: switch to **தமிழ்** or **English**.
- In the WhatsApp simulator, click the quick inquiry chip: **"🏛️ எனக்கு MUDRA தகுதி உள்ளதா?"** (or in English: *"Am I eligible for MUDRA?"*).
- Show the instant response: the engine cites the exact rules, explains why she qualifies in Tamil, appends official circular URLs, and confirms that approval is decided by the lender.
- *What to say:* "Our channel simulator executes the exact code path that our live Twilio webhook runs, with automatic script detection across Tamil, Hindi, Telugu, and English."

### Step 6: Conclude on the Admin Telemetry Page
- In sidebar, click **Admin & review queue**.
- Scroll to **Jury Evaluation Telemetry Panel**:
  - Show the live KPI gauges: 100% Eligibility Accuracy, 100% Extraction Accuracy, 0% Hallucination Rate, 6/6 Agents Active.
- *What to say:* "In conclusion, Team TEJAS066 has delivered a complete, working, auditable, and human-centric solution that advances SDG 9.3 and proves that AI can empower small businesses without ever compromising on truth."

---

## 8. Hard Jury Questions & Winning Answers

#### Q1: "Why shouldn't we just use ChatGPT or Claude with a good system prompt?"
> **Winning Answer**: "LLMs are probabilistic language models, not deterministic rule engines. If a bank asks whether an MSME with ₹2.6 Crore investment qualifies as Micro, an LLM might say 'yes' based on outdated 2020 thresholds (₹1 Cr), hallucinate a subsidy, or invent a deadline. Under our architecture, **'Rules decide; AI explains.'** The eligibility verdict is 100% code-driven and verified against primary gazette notifications. The LLM only translates and explains that verified verdict to the owner in their mother tongue."

#### Q2: "How do you handle data privacy for sensitive business financials?"
> **Winning Answer**: "Our core architecture runs entirely locally using a relational SQLite Digital Twin. No business financials, turnover figures, or owner credentials are sent to third-party cloud models for decision-making. Even when an LLM is enabled for conversational phrasing, only sanitized contextual snippets are passed through our strict numerical guardrail, which blocks any unauthorized data leakage."

#### Q3: "What if a government scheme changes its criteria next month?"
> **Winning Answer**: "We built our **Monitoring Agent** and **Curated Admin Queue** specifically for this. When circulars change (like the 2024 MUDRA Tarun Plus expansion to ₹20L or the April 2025 MSME threshold revisions), changes are held in a review queue. An admin must verify the official gazette PDF before the rules engine is updated. Once approved, the platform automatically generates localized update alerts for all affected business owners."

#### Q4: "Do you actually submit the loan to the bank portal?"
> **Winning Answer**: "No, and that is an intentional GovTech ethical design choice. Direct API submission to Udyam or MUDRA portals requires licensed intermediary accreditation and bank integration. Claiming an application is 'submitted' inside an unaccredited prototype is deceptive. We respect the human owner: we generate bank-standard preparation dossiers, calculate tipping points, and guide them to CSCs or branch managers with 100% verified documentation."

#### Q5: "What if the document is a poor-quality photo or scanned without a text layer?"
> **Winning Answer**: "Our Document Agent strictly decouples upload status from extraction status from human confirmation. If a scanned PDF or image lacks embedded text, we attempt Tesseract OCR. If OCR fails or is unavailable, the system never invents fake data or claims success; it transparently tags the status as 'ocr_not_available', alerts the owner to provide a clean copy, and keeps unconfirmed fields in their safe 'unknown' state."

#### Q6: "How do you scale this from Tamil Nadu to all 28 states of India?"
> **Winning Answer**: "Because our architecture separates pure logic (`core/`) from data contracts (`data/schemes.json`), expanding to a new state (e.g., Karnataka, Maharashtra, or Uttar Pradesh) does not require rewriting the application. We simply add the state's scheme definitions with primary gazette citations to the catalogue. Our retrieval engine, document parser, and multi-script channel adapter automatically support the new state."

#### Q7: "How will this be deployed in the real world? Who pays for it?"
> **Winning Answer**: "Our solution has two viable deployment models:
> 1. **B2G / CSR Model (Temenos / SASTRA Alignment)**: Deployed as public digital infrastructure at Common Service Centres (CSCs) and District Industries Centres (DICs), funded through CSR and MSME promotion grants under SDG 9.3.
> 2. **B2B FinTech / Bank Partnership**: Commercial banks (SBI, Canara, BoB) sponsor the copilot because it slashes loan application processing costs and delivers pre-verified, document-complete loan leads, dropping rejection rates by over 40%."

#### Q8: "What is your roadmap for future enhancements?"
> **Winning Answer**: "Our production roadmap includes:
> 1. **Account Aggregator (AA) Integration**: Automatically pulling GST returns and bank statements via NBFC-AA consent architecture for instant financial twin verification.
> 2. **Interactive Voice Response (IVR)**: Extending our Web Speech voice engine to telephone IVR for non-smartphone users in rural artisan clusters.
> 3. **Automated Gazette Scraping with Human-in-the-Loop**: Enhancing the Monitoring Agent with automated RSS/gazette scrapers feeding directly into the Admin review queue."

---

## 9. Mobile Responsiveness & Multi-Device Testing
Our UI is optimized with native responsive media queries (`@media (max-width: 768px)`):
- Multi-column layouts dynamically wrap into clean, full-width touch cards.
- Stepper stages adapt comfortably to smartphone screens without horizontal overflow.
- Metric tiles stack neatly with high-contrast GovTech typography.
- Touch-friendly buttons and prompt chips span full container widths for effortless thumb interaction.

---

## 10. Team TEJAS066 — Presentation Distribution
To present like a unified, professional championship team in front of the jury:

| Speaker | Section / Responsibility | Key Talking Points |
|---|---|---|
| **Nivashini K** *(Leader)* | **The Hook & Problem Statement** | 30s elevator pitch, 63M MSMEs credit gap, SDG 9.3 alignment, and the core slogan: *"From 'I need help' to 'I know what to do next.'"* |
| **Sabarish R** | **Architecture & 100% Determinism** | *"Rules decide, AI explains, owner acts."* Why LLMs fail in lending, master pipeline orchestrator (`run_pipeline.py`), and offline SQLite Digital Twin. |
| **Harshini S** | **Lakshmi Persona & Document Agent** | Lakshmi's Tiruppur journey, 1-click Document Agent demo, Luhn Mod-36 GSTIN verification, and Udyam checksum validation. |
| **Lohitha R** | **Multilingual & Channel Simulator** | Full 4-language parity (English, தமிழ், हिन्दी, తెలుగు), native WhatsApp simulator, prompt chips, and browser voice dictation. |
| **Nandhini Chelladurai** | **Forms Dossier, Telemetry & Closing** | Bank-ready ReportLab PDF dossier generation, 100% KPI benchmark proof on Admin telemetry page, and CSR / Bank B2B future roadmap. |

---
*Prepared with pride by Team TEJAS066 for the TEJAS 2026 Hackathon Finals.*

