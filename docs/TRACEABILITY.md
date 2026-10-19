# Traceability: what we promised the TEJAS panel → what exists (v0.2)

Sources: TEJAS066.docx (idea round), 3-minute video script (round 2).  “Verified” = covered by an automated test or a command I ran.

| # | Promise (source) | Module | Status | Evidence | Limitation to say honestly |
|---|---|---|---|---|---|
| 1 | Identify relevant schemes (MUDRA, CGTMSE…) (docx Q1/Q2) | `data/schemes.json`, `core/eligibility.py` | PARTIAL: 2 schemes | `test_eligibility.py`, `evaluation` | PMEGP/TN schemes stay unverified backlog |
| 2 | Check eligibility, explain why (docx Q5) | `core/eligibility.py`, `core/insights.py`, `ui/schemes_view.py` | DONE | 17 labelled cases + boundaries; tipping points; “what the rule requires” | Only sourced criteria; some from secondary sources |
| 3 | Documentation checklist | `core/checklist.py` | DONE (limited) | `test_checklist.py` | 1 document per scheme is source-verified |
| 4 | Upload Udyam/GST docs, OCR extract (docx Q2/Q3) | `core/documents.py` | PARTIAL | `test_documents.py` | Text PDFs; OCR only if tesseract installed |
| 5 | Flag missing/mismatched documents before submission (docx Q5) | `core/documents.py`, `services/alerts.py` | DONE (3 cross-checks) | GSTIN state, Udyam state, class vs numbers | Format checks, not portal verification |
| 6 | Tamil/Hindi/Telugu (docx Q1/Q2) | `core/i18n.py` | PARTIAL: EN + TA | `test_i18n.py`, UI smoke both languages | No Hindi/Telugu; Tamil needs native review |
| 7 | WhatsApp channel (docx Q1/Q2, video s3) | `services/whatsapp*.py`, simulator page | PARTIAL → webhook BUILT | signature = Twilio official validator; HTTP round-trip test | Real phone delivery NOT run; needs Twilio account |
| 8 | Voice (docx Q1/Q2) | `ui/voice.py` | EXPERIMENTAL | JS syntax-checked | Not run in a real browser here; Chrome/Edge only |
| 9 | Assist filling forms (docx Q2) | `core/forms.py`, `services/report.py` | PARTIAL | `test_forms.py`, report tests | Worksheet + readiness report, not the bank’s form |
| 10 | To-do list + deadline reminders by WhatsApp/SMS (docx Q2/Q3) | `core/tasks.py`, `services/notifications.py`, `services/alerts.py` | PARTIAL | tasks, alerts, honest send statuses | Twilio send coded; never run live. No scheduler for auto-reminders |
| 11 | Track applications (docx Q1) | `core/tasks.py` | DONE | `test_tasks.py` | Owner-entered status |
| 12 | RAG over official circulars, grounded, cited (docx Q3, video s5) | `services/retrieval.py`, `copilot.py` | PARTIAL | grounding + guard tests, module trace | Structured lookup; no vector DB / circular PDFs |
| 13 | Monitor portals for new schemes; admin verifies before notify (docx Q3, video s5) | `services/monitoring.py`, `scripts/monitor_sources.py`, `.github/workflows/monitor.yml` | PARTIAL → job BUILT | scan/baseline/change/error tests; queue + approval tests | Never run against the live sites from here; dynamic pages may false-alarm; humans must review |
| 14 | “Rules decide, AI explains, owner acts” (video s4) | `core/eligibility.py` + `copilot.guard` | DONE | guard tests | — |
| 15 | Business Digital Twin (video s4) | `core/profile.py` | DONE | `test_profile.py` | — |
| 16 | KPIs: ≥90% eligibility, ≥90% extraction, alerts ≤24 h, cited answers, −40% rejections (video s7) | `evaluation/` | PARTIAL | 34/34 and 15/15 on synthetic sets | Targets, not achievements |
| 17 | Lakshmi journey: Tamil alert, missing doc, dashboard with next steps + deadlines (video s6) | dashboard (next-best-action, alerts, deadlines) | DONE (web) | UI smoke incl. Tamil alert | Alert is a preview unless Twilio is configured and a send succeeds |
