@echo off
setlocal
cd /d "%~dp0"

call ".venv\Scripts\activate.bat"
python -u ".\main.py"

echo Python exited with %errorlevel%
pause
