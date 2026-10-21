# MSME Copilot - workspace rules

Python + Streamlit + SQLite. Layers: core/ (pure logic, no UI/network) -> services/ (orchestration, IO) -> ui/ (display only). Source of truth for state and next work: HANDOVER_MASTER.md. Contracts: docs/CONTRACTS.md.

- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

## Commands
- Run app: `streamlit run app.py`   - Tests: `python -m pytest -q`   - JS tour tests: `cd tests/js && npm test`
- Doctor: `python scripts/doctor.py`   - Verify a phase: `python scripts/verify_phase.py --phase <id>`

## Workflows
Slash-commands in `.agents/workflows/`: /start-here /phase-b-data /phase-c-llm /phase-d-docs /phase-e-channels /phase-f-monitor /phase-g-lang-review /phase-h-ui-polish /phase-i-deploy /verify /explain-module.

## Do not
- Re-add an HTTP API or a React front end (a removed api_server exposed profile data with open CORS).
- Put hard-coded metrics in the UI. Only show numbers that evaluation/run_eval.py or tests actually measured.
- Edit data/schemes.json from memory.
