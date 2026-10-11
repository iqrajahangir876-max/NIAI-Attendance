@echo off
cd /d "%~dp0frontend"
if not exist node_modules (
  echo Installing frontend packages...
  npm install
)
npm run dev
pause
