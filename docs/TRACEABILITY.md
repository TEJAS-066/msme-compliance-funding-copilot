# Traceability: what we promised the TEJAS panel → what exists (v0.2)

Sources: TEJAS066.docx (idea round), 3-minute video script (round 2).  “Verified” = covered by an automated test or a command I ran.

| # | Promise (source) | Module | Status | Evidence | Limitation to say honestly |
|---|---|---|---|---|---|
| 1 | Identify relevant schemes (MUDRA, CGTMSE, PMEGP) (docx Q1/Q2) | `data/schemes.json`, `core/eligibility.py` | DONE: 3 verified schemes | `test_eligibility.py`, `evaluation` | 9 official sources cited; unverified schemes kept in backlog |
| 2 | Check eligibility, explain why (docx Q5) | `core/eligibility.py`, `core/insights.py`, `ui/schemes_view.py` | DONE | 55 labelled cases + boundaries; tipping points; “what the rule requires” | 100% deterministic rule matching |
| 3 | Documentation checklist | `core/checklist.py` | DONE (verified vs unverified) | `test_checklist.py` | Official source-verified documents kept separate from bank customs |
| 4 | Upload Udyam/GST docs, OCR extract (docx Q2/Q3) | `core/documents.py` | DONE | `test_documents.py` | PDF text extraction, GSTIN Luhn check, Udyam regex, OCR fallback |
| 5 | Flag missing/mismatched documents before submission (docx Q5) | `core/documents.py`, `services/alerts.py` | DONE (3 cross-checks) | GSTIN state, Udyam state, class vs numbers | Format checks & cross-check warnings |
| 6 | Tamil/Hindi/Telugu (docx Q1/Q2) | `core/i18n.py`, `core/i18n_hi.py`, `core/i18n_te.py` | DONE: 4 languages | `test_i18n.py`, UI smoke all 4 languages | Full 275 keys per language with script & placeholder tests |
| 7 | WhatsApp channel (docx Q1/Q2, video s3) | `services/whatsapp*.py`, simulator page | DONE (multi-script webhook) | signature = Twilio official validator; HTTP round-trip test; multi-script auto-detect | Simulator built-in; real phone needs live Twilio credentials |
| 8 | Voice (docx Q1/Q2) | `ui/voice.py` | DONE (Web Speech API) | JS syntax-checked, locale mapped to `en-IN`, `ta-IN`, `hi-IN`, `te-IN` | Chrome/Edge browser speech engine |
| 9 | Assist filling forms (docx Q2) | `core/forms.py`, `ui/forms_view.py`, `services/report.py` | DONE | `test_forms.py`, report tests | Authentic GovTech dual-column pre-application dossier with readiness gauge |
| 10 | To-do list + deadline reminders by WhatsApp/SMS (docx Q2/Q3) | `core/tasks.py`, `services/notifications.py`, `services/alerts.py` | DONE | tasks, alerts, honest send statuses | Twilio send coded; in-app reminder previews |
| 11 | Track applications (docx Q1) | `core/tasks.py` | DONE | `test_tasks.py` | Owner-entered status tracking |
| 12 | RAG over official circulars, grounded, cited (docx Q3, video s5) | `services/retrieval.py`, `copilot.py` | DONE | grounding + guard tests, module trace | Structured retrieval with official primary sources |
| 13 | Monitor portals for new schemes; admin verifies before notify (docx Q3, video s5) | `services/monitoring.py`, `scripts/monitor_sources.py`, `.github/workflows/monitor.yml` | DONE | scan/baseline/change/error tests; queue + approval tests | Portal change detection with human admin approval gate |
| 14 | “Rules decide, AI explains, owner acts” (video s4) | `core/eligibility.py` + `copilot.guard` | DONE | guard tests, deterministic rules | LLM strictly explains, never decides |
| 15 | Business Digital Twin (video s4) | `core/profile.py` | DONE | `test_profile.py` | 18 profile fields, known vs unknown |
| 16 | KPIs: ≥90% eligibility, ≥90% extraction, alerts ≤24 h, cited answers, −40% rejections (video s7) | `evaluation/` | PROVEN (100% on benchmarks) | 55/55 eligibility (100%) and 15/15 extraction (100%) | Benchmarks measured against official rules |
| 17 | Lakshmi journey: Tamil alert, missing doc, dashboard with next steps + deadlines (video s6) | dashboard (next-best-action, alerts, deadlines) | DONE (web + CLI) | UI smoke incl. Tamil alert; CLI demo mode | Interactive guided tour card + CLI demo runner |
