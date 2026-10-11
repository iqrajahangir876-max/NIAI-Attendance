@echo off
cd /d "%~dp0backend"
if not exist .venv\Scripts\python.exe (
  echo Creating Python virtual environment...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  python -m pip install --upgrade pip
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)
python -m app.seed
python -m uvicorn app.main:app --reload --port 8001
pause
