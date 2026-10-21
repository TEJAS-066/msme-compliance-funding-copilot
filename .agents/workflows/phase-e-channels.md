---
description: Real WhatsApp + voice evidence (Tech lead / UI owner): Run the WhatsApp webhook with a real phone and test browser voice; record evidence.
---
# Phase E - Real WhatsApp + voice evidence (Tech lead / UI owner)

Read AGENTS.md, HANDOVER_MASTER.md and docs/CONTRACTS.md first. Work on branch `feat/phase-e-channels-<yourname>`.

**Goal:** Run the WhatsApp webhook with a real phone and test browser voice; record evidence.
**Why it matters:** The webhook is tested locally and against Twilio's validator, but never with a real message.

**Inputs the human must provide (ask for them if missing - do not guess):**
- Twilio account + WhatsApp sandbox joined from a phone; ngrok installed.
- Follow docs/WHATSAPP.md.

**Do, in order (small steps; run `python -m pytest -q` after each):**
1. Help me run scripts/whatsapp_server.py, expose it, and debug the first real message. Never loosen signature verification.
2. Create docs/CHANNEL_TEST_LOG.md: date, steps, the real message text sent/received (English + Tamil), what failed, fixes.
3. Open the app in Chrome; test ui/voice.py in English and Tamil; record exactly what happens. Fix only what you observed.
4. Add rate-limit / unknown-sender behaviour notes to the log.

**Done when:**
- a real Tamil reply received on a phone, logged
- voice result logged honestly (works / fails / browser-dependent)

**Hard rules:**
- RULES DECIDE, AI EXPLAINS, THE OWNER ACTS. The LLM never decides eligibility.
- Scheme facts live ONLY in data/schemes.json with source_ids. Never invent facts, URLs, figures, deadlines or documents. Unknown stays unknown.
- Never claim something happened (sent, submitted, verified, measured, delivered) unless you ran it and saw it.
- User-visible text goes through core/i18n.py (+ ui/tour_content.py for the tour). Keep en/ta/hi/te parity; tests enforce it.
- Small diffs. Run `python -m pytest -q` after each change. Never weaken or delete a test or services/copilot.guard().
- Ask the human before: new dependencies, changing docs/CONTRACTS.md, deleting files, calling external services.
- Never commit secrets (.env). Never send real customer data to any LLM.

**Finish:** run `python scripts/verify_phase.py --phase phase-e-channels` and print the whole report. Then explain in plain words what you changed and why (I am learning), and list anything you could NOT verify. Do not say a phase is complete if the report shows FAIL.
