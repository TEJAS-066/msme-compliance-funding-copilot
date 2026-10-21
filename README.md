# MSME Compliance & Funding Copilot — TEJAS066 (TEJAS 2026 finals)

> From “I need help” to “I know what to do next.” — **Rules decide · AI explains · the owner acts.**

Multilingual (English · தமிழ் · हिन्दी · తెలుగు) copilot that helps a small manufacturer find relevant schemes, see *why* (criterion by criterion, with sources), check documents, and know the next step. It never submits anything.

## Run (3 minutes)
```bash
bash scripts/setup.sh        # Windows: scripts\setup.bat      (venv + install + doctor + tests)
streamlit run app.py         # http://localhost:8501  — a guided tour starts automatically
```
Full guide: [`docs/RUN_GUIDE.md`](docs/RUN_GUIDE.md) · What was built and why: [`docs/EXPLAINER.md`](docs/EXPLAINER.md)

## For the next developer / AI tool
1. Read [`HANDOVER_MASTER.md`](HANDOVER_MASTER.md) — state, honest limits, roadmap.
2. Follow [`docs/UPGRADE_PLAYBOOK.md`](docs/UPGRADE_PLAYBOOK.md) (Antigravity: type `/start-here`, `/phase-b-data` … from `.agents/workflows/`).
3. Verify every change: `python scripts/verify_phase.py --phase <id>`.

## Status (real runs)
`python -m pytest -q` → 280 passed · `python -m evaluation.run_eval` → eligibility 67/67, extraction 24/24 (synthetic regression sets, **not** real-world accuracy) · schemes: MUDRA, CGTMSE, PMEGP.
Not yet proven: live LLM, real WhatsApp message, live government-site monitoring, browser voice, visual polish on every page. See `HANDOVER_MASTER.md` §3.

## Layout
`core/` pure logic · `services/` orchestration/IO · `ui/` display (+ `ui/shell.py`, `ui/assets/` tour & theme) · `data/schemes.json` only source of scheme facts · `evaluation/` · `scripts/` · `tests/` (+ `tests/js`) · `docs/` · `.agents/` Antigravity rules & workflows.
