# Ready-to-paste prompts (Antigravity / Claude Code)

Start EVERY session with this first message, then add one task prompt below:

> Read README.md, AGENTS.md, docs/CONTRACTS.md and docs/TRACEABILITY.md. Then run `python -m pytest -q` and tell me the result. Do not change anything yet. Explain in 5 lines what this project does and how my area fits, so I understand it before we build.

After each change, end with: **“Run the tests, show me the real output, and explain what you changed and why in simple words.”**

---
## Scheme-data & rules owner
> Add the scheme **PMEGP** to `data/schemes.json`. I will paste the official text/PDF; use ONLY that text. Fill `criteria`, `benefits`, `documents` with `source_ids` pointing to new entries in `sources` (real URL, tier, accessed date). Set `review_status` to `partly_verified_official` only if every criterion is from an official page; otherwise leave it in `unverified_backlog`. Add 4 cases to `evaluation/cases.json` (include boundary values), run `python -m evaluation.run_eval` and `pytest`. If any fact is not in the text I gave you, say so instead of guessing.

## Documents owner
> Extend `core/documents.py` to extract the **Udyam certificate date of registration** and **NIC code** labels, only when present. Add synthetic sample text in `scripts/make_samples.py`, tests in `tests/test_documents.py` (normal, missing, malformed), and update `evaluation/cases.json`. Do not add OCR dependencies without asking me.

## Copilot owner
> Run the app with `LLM_PROVIDER=gemini` and my key in `.env`. Write `scripts/check_llm.py` that sends one grounded question through `services/llm.complete`, prints the raw answer, the guard result and the final mode. Fix model names/payloads if the API rejects them. Never print keys. Then add 5 Tamil test questions to `tests/test_copilot_grounding.py` using a fake LLM function.

## UI / Tamil owner
> Review every Tamil string in `core/i18n.py` and the catalogue Tamil text. I will give you corrections from a native speaker; apply them without changing placeholders like `{name}`. Then improve the Dashboard page: add a progress bar for the six journey steps based on real state (profile known fields, confirmed documents, tasks). Keep `tests/test_ui_smoke.py` passing.

## Integration / tech lead
> Follow docs/WHATSAPP.md with my Twilio sandbox credentials in `.env`. Start `scripts/whatsapp_server.py`, help me expose it with ngrok, and debug the first real message. Do NOT change signature verification. Report exactly what Twilio and the server logs show — never claim delivery you haven't seen. Then add a short “how we tested WhatsApp” section to the README with the real result.

## Monitoring owner
> Run `python scripts/monitor_sources.py` locally with internet. Show me the baseline count and any errors per source. For sources that return errors or always change (dynamic pages), propose a better normalisation in `services/monitoring.normalize` with a test using a saved sample page. Do not weaken the rule that changes only create PENDING queue items.

## Voice / UI owner
> Open the app in Chrome. Test `ui/voice.py` (chat page → Voice input) in English and Tamil, report exactly what happens (permission prompt, transcription, text appearing in the chat box). If it fails, fix `ui/voice.py` and keep the visible error message. Never claim it works until you saw the transcript appear.

## Anyone — safety review
> Act as a hostile reviewer. Search the codebase for: any place a success message is shown without the operation happening, any place unknown data could count as PASS, any place the LLM output is shown without the guard, any hardcoded secret, any scheme fact without a source. List findings with file/line; fix only the ones I approve.
