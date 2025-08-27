@echo off
setlocal
cd /d "%~dp0"

call ".venv\Scripts\activate.bat"
python -u ".\main.py" --log info 2>>error-log.txt

echo Python exited with %errorlevel%
pause
