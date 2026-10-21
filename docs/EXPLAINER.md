# EXPLAINER — what was built, why, and how to say it

Read in this order: §1 (one paragraph), §2 (the 6 ideas), §3 (a request's journey), §4 (module-by-module), §5 (the tour/theme mechanism), §6 (limits).

## 1. One paragraph
A small-business owner (Lakshmi, garment unit, Tiruppur) doesn't know which scheme fits, what is missing, or what to do next. The app builds a **profile** (what is known and what is *not*), reads her **documents** (and asks her to confirm every value), checks **schemes criterion by criterion with sources**, explains in **her language**, and tracks **next steps**. It never submits anything for her and never guesses.

## 2. The six ideas that make it trustworthy
1. **Rules decide; AI explains.** `core/eligibility.py` is plain, tested code. The LLM can only reword what the rules and the catalogue already say. *(Answer to "what if the AI hallucinates?")*
2. **Unknown ≠ pass.** Every profile field is `known` or `unknown`; a missing fact makes a criterion UNKNOWN, never PASS.
3. **One source of facts.** `data/schemes.json`; a validator rejects any criterion without a source. Secondary sources are tagged.
4. **The guard.** `services/copilot.guard()` rejects an LLM answer containing numbers or promises not in the verified context; the app falls back to a template.
5. **Honest states.** Upload ≠ extraction ≠ confirmation. Saved ≠ scheduled ≠ sent. Previews say PREVIEW ONLY.
6. **The owner stays in control.** Nothing is submitted; mismatches are flagged, never silently overwritten.

## 3. One request, end to end ("Am I eligible for MUDRA?" in Tamil)
UI (`ui/chat_view.py`) → `services/copilot.answer()` → **retrieval** finds intent + scheme → **eligibility engine** evaluates every criterion on the *confirmed* profile → context built (facts, unknowns, results, sources) → template (demo mode) or LLM → **guard** → sources appended from catalogue metadata (never from model text) → UI shows the answer, the mode and a **module trace** of which module did what.

## 4. Modules (what / why / 60-second line)
| Module | What | Say this |
|---|---|---|
| `core/profile.py` | Fields as value + known/unknown; size class from the 2025 limits | "We never assume a value the owner didn't give." |
| `core/eligibility.py` | PASS/FAIL/UNKNOWN/N-A per criterion; overall status | "Pure code, no AI, with boundary tests (₹10 lakh, ₹20 lakh, ₹10 crore)." |
| `core/insights.py` | Which missing fact settles the most criteria; tipping points; what the rule requires | "It tells the owner the *one* question to answer next, derived from our own rules." |
| `core/documents.py` | Text PDF + OCR, GSTIN checksum, state and class cross-checks, confirm-before-apply | "A valid-looking ID is a format check, not government verification — and we say so." |
| `services/copilot.py` | Orchestrator + LLM guard + trace | "Rules decide, AI explains, guard checks, sources are attached by code." |
| `services/alerts.py`, `report.py` | Dashboard alerts + readiness report | "Lakshmi leaves with a document she can take to a bank." |
| `services/whatsapp*.py` | Twilio webhook, signature check, rate limit | "Same copilot on WhatsApp; unsigned requests are refused." |
| `services/monitoring.py` | Hash source pages → pending item → admin approves | "Detects change automatically; a human decides before anyone is told." |
| `core/db.py` | SQLite with per-visitor owner | "Judges using the live URL can't see each other's data." |
| `ui/shell.py` + `assets/` | Tour, ⓘ menu, theme switch | §5 |

## 5. The guided tour, theme switch and ⓘ menu
**Problem:** Streamlit reruns the whole script on every click, and a modal dialog can't point at page elements.
**Solution:** `ui/shell.py` builds a small JSON config (language, localised steps, page names) and embeds `ui/assets/shell.js` via `st.iframe`. The script runs in the browser and draws into the parent page: a dim layer with a **spotlight** cut-out, a **speech bubble** (thick outline, offset shadow, tail pointing at the target), progress dots and language pills.
- *Auto-start:* once per browser tab session (`sessionStorage`). *Resume:* every script load rebuilds from stored state, so reruns and language changes are harmless.
- *Pointing:* targets are found by stable selectors — Streamlit's `data-testid`s and `st-key-*` classes from `st.container(key=...)` (see `ui/dashboard.py`: `tour_nba`, `tour_stepper`, `tour_agents`). If a target is missing, the bubble centres; the tour never breaks.
- *Page jumps:* a step on another page clicks that sidebar item once, then continues after Streamlit reruns.
- *Language:* the bubble text comes from `ui/tour_content.py`; clicking a pill clicks the sidebar language radio, the app reruns, and the tour resumes in the new language.
- *Theme:* `data-msme-theme` attribute + CSS overrides in `shell.css`, saved in `localStorage`; no server round-trip.
- *Safety:* text is inserted with `textContent` (no HTML injection); the script is inlined with `</` escaped; tests cover both.
- *Tests:* `tests/js/shell.test.js` runs the real script in jsdom (9 behaviours). **Not** a visual test.

## 6. Limits to state openly
Synthetic-data regression checks, not real accuracy · never run with a real LLM key / real WhatsApp / live government sites · UI not visually verified by the author · OCR proven on clean renders only · non-English text unreviewed · three schemes only, four criteria still secondary-sourced · no accounts or consent flow yet.
