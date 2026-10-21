# Run guide — from zero to a working demo

## What you need
| Tool | Needed? | Check |
|---|---|---|
| Python 3.10 or newer (3.12 best) | **Yes** | `python --version` (Windows: `py --version`) |
| Git | Yes, to push | `git --version` |
| Tesseract OCR (+ Tamil pack) | Optional — only for photos/scans | `tesseract --version` |
| Node.js 18+ | Optional — only to run the tour's JS tests | `node --version` |
| API keys (Gemini/Sarvam/Claude), Twilio | Optional — the app is fully usable without them | |

## Option A — one command
**Mac / Linux / WSL / Git-Bash:** `bash scripts/setup.sh`   **Windows:** `scripts\setup.bat`
It creates `.venv`, installs requirements, creates `.env`, runs the doctor and the tests. Then start the app (below).

## Option B — by hand
```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1   (cmd: .venv\Scripts\activate.bat)
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env   (leave keys blank = demo mode)
python scripts/doctor.py           # tells you what works on this machine
streamlit run app.py               # opens http://localhost:8501
```

## What you should see (first minute)
1. The page opens and **a speech-bubble tour starts by itself**. Press **Next**; it points at real parts of the screen. Click a language pill inside the bubble — the tour and the app change language. **Esc** or **Skip** ends it.
2. Top-right: the round **ⓘ** (reopen the tour / "about this page") and the **☀/☾ switch** (light/dark, no reload).
3. Click **Load demo profile** → the dashboard fills in: next best action, alerts, stepper, six modules.
4. Try the order: Documents (process *sample_udyam_lakshmi.pdf*) → Schemes → Ask Copilot ("Am I eligible for MUDRA?" / Tamil) → Tasks.

## Tests and checks
```bash
python -m pytest -q                      # expect: 280 passed (JS tests skip unless you do the next line)
cd tests/js && npm install && npm test   # 9 tour tests in a simulated browser (needs Node)
python -m evaluation.run_eval            # KPI harness
python scripts/verify_phase.py --phase my-change   # full report -> verification_report.md (paste to your reviewer)
```

## Optional features
| Feature | How |
|---|---|
| OCR | Install Tesseract: Windows https://github.com/UB-Mannheim/tesseract/wiki (tick Tamil), Mac `brew install tesseract tesseract-lang`, Ubuntu `sudo apt install tesseract-ocr tesseract-ocr-tam`. Re-run `python scripts/doctor.py`. |
| Real LLM answers | In `.env` set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=...`, then `python scripts/check_llm.py`. Answers are still guarded; failures fall back to demo mode. |
| WhatsApp | `docs/WHATSAPP.md` (Twilio sandbox + ngrok). The simulator page works without it. |
| Shared/cloud demo | Secrets: `MSME_MULTIUSER="1"` and `ADMIN_PIN="…"`. Each visitor gets private data; Admin asks for the PIN. |

## Deploy on Streamlit Community Cloud
Push to GitHub → share.streamlit.io → New app → main file `app.py`. Under *Advanced settings* choose Python 3.12 and paste secrets (TOML). `packages.txt` installs Tesseract. Open the URL 10 minutes before presenting (free apps sleep). Settings can change — follow the platform's current docs.

## Push to GitHub (first time)
```bash
git init && git add -A && git commit -m "TEJAS066 MVP v1"
git branch -M main && git remote add origin <your-repo-url> && git push -u origin main
```
`.env` is git-ignored; run `python scripts/verify_phase.py` before pushing — it scans for keys.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `streamlit: command not found` | Activate the venv first; or `python -m streamlit run app.py` |
| PowerShell blocks `Activate.ps1` | `Set-ExecutionPolicy -Scope Process RemoteSigned`, or use cmd |
| Port 8501 busy | `streamlit run app.py --server.port 8502` |
| Tour doesn't start | It starts once per browser tab session. Use the **ⓘ → Guided tour**, or open a new tab. If ⓘ is missing, hard-refresh (Ctrl+Shift+R) and check the browser console. |
| Dark mode looks wrong somewhere | Known polish item (Phase H): send a screenshot; fixes go in `ui/assets/shell.css` |
| "OCR not available" | Install Tesseract (above); photos/scans only — text PDFs work without it |
| Tamil shows boxes | Install a system Tamil font (e.g. Noto Sans Tamil) |
| LLM answers say `demo_fallback` | Run `python scripts/check_llm.py`; read the notes (key, model name, network) |
| Tests fail only on JS | Run `cd tests/js && npm install` |
