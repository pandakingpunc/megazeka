@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Python ortami bulunamadi. README.md kurulum adimlarini izleyin.
  pause
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "app\main.py"
