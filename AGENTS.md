> **Start with HANDOVER_MASTER.md (state + roadmap) and docs/UPGRADE_PLAYBOOK.md (phases + prompts).** Verify with `python scripts/verify_phase.py`.

# Instructions for AI coding agents (Antigravity / Claude Code / Cursor)

Project: MSME Compliance & Funding Copilot (Python + Streamlit + SQLite). Read README.md first.

## Non-negotiables
- Rules decide; AI explains; the owner acts. The LLM never decides eligibility.
- Every scheme fact lives in `data/schemes.json` with `source_ids`, `last_verified`, `review_status`. Never invent facts, URLs, deadlines, amounts or documents. If unsure, mark unverified and exclude from recommendations.
- Unknown profile data stays UNKNOWN. Never treat missing as PASS.
- Never show a success message for something that did not happen (submitted, sent, verified, extracted).
- Every user-visible string goes through `core/i18n.py` with BOTH English and Tamil (tests enforce this).
- No secrets in code or git. Use env vars. Synthetic data only.

## Workflow
1. Make a SMALL change. Keep the app launchable (`streamlit run app.py`).
2. Add/adjust tests in `tests/`. Run `python -m pytest -q` — all must pass before you say you are done.
3. Run `python -m evaluation.run_eval` if you touched rules or extraction.
4. Report: files changed, commands run, real test output, known issues. Do not claim you ran something you did not.
5. Ask before: adding dependencies, changing data contracts in `docs/CONTRACTS.md`, deleting files, calling external APIs.

## Boundaries
- `core/` = pure logic, no Streamlit, no network. `services/` = orchestration/IO. `ui/` = display only.
- Don't put business rules in `ui/`. Don't call `requests` from `core/`.
