@echo off
REM One-command setup for Windows (cmd/PowerShell).   Run:  scripts\setup.bat
cd /d "%~dp0\.."
if not exist .venv (python -m venv .venv)
call .venv\Scripts\activate.bat
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
if not exist .env (copy .env.example .env >nul & echo created .env - keys stay blank = demo mode)
python scripts\doctor.py
python -m pytest -q
echo.
echo READY.  Start the app with:   .venv\Scripts\activate  then  streamlit run app.py
