---
description: Live LLM + Tamil quality (Tech lead): Prove the guarded LLM path with a real key, pick the best provider for Tamil, keep the guard strict.
---
# Phase C - Live LLM + Tamil quality (Tech lead)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-c-llm-<yourname>`.

**Goal:** Prove the guarded LLM path with a real key, pick the best provider for Tamil, keep the guard strict.
**Why it matters:** The LLM code was written from public docs and has never run with a real key.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Create keys (Gemini AI Studio, optional Sarvam/Anthropic) and put them in .env only.
- Do NOT use real customer data; free tiers may use prompts to improve products (check the provider's terms).

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Run `python scripts/check_llm.py`; paste the output.
2. Create evaluation/llm_questions.json: 10 English, 10 Tamil, 5 out-of-scope questions with the expected behaviour (answer / refuse).
3. Create scripts/eval_llm.py: for each provider with a key, run all questions; write docs/LLM_RESULTS.md with guard-pass rate, fallback rate, refusal correctness and latency per provider.
4. Improve SYSTEM_PROMPT in services/copilot.py only to raise pass rate. For every failure mode found, add a test using a fake LLM function. Do NOT loosen guard().
5. Ask a native Tamil speaker to rate 10 Tamil answers 1-5; record the scores; choose the default provider.

**Done when:**
- docs/LLM_RESULTS.md has real numbers
- all guard tests still pass; guard() diff only adds checks
- no key in repo (verify_phase secret scan)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-c-llm` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
