@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem --- run from this script's folder ---
cd /d "%~dp0"

rem --- config ---
set VENV_DIR=.venv
set REQ=requirements.txt
set MAIN=main.py

echo [1/5] Checking for Python 3.13...

rem Try the Python launcher first
py -3.13 -V >NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.13 not found. Attempting installation...

    rem Try winget
    where winget >NUL 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Installing via winget...
        winget install -e --id Python.Python.3.13 --source winget --silent --accept-package-agreements --accept-source-agreements
    ) else (
        echo winget not available, skipping...
    )

    rem Check again
    py -3.13 -V >NUL 2>&1
    if %ERRORLEVEL% NEQ 0 (
        rem Try Chocolatey
        where choco >NUL 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo Installing via Chocolatey...
            choco install python --version=3.13.0 -y --no-progress
        ) else (
            echo Chocolatey not available, skipping...
        )
    )

    rem Check again
    py -3.13 -V >NUL 2>&1
    if %ERRORLEVEL% NEQ 0 (
        rem Fallback: direct download from python.org (3.13.5 amd64)
        set "PYDL=%TEMP%\python-3.13.5-amd64.exe"
        echo Downloading official installer...
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
          "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
           Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.5-amd64.exe' -OutFile '%PYDL%'"
        if exist "%PYDL%" (
            echo Running silent installer...
            start /wait "" "%PYDL%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_pip=1
        ) else (
            echo ERROR: Download failed.
        )
    )
)

rem Final verification
py -3.13 -V >NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python 3.13 is not available after installation attempts.
    echo Please install Python 3.13 manually, ensure 'py -3.13' works, then re-run this script.
    exit /b 1
)

echo [2/5] Creating virtual environment at "%VENV_DIR%" (if missing)...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    py -3.13 -m venv "%VENV_DIR%"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: venv creation failed.
        exit /b 1
    )
)

echo [3/5] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if not defined VIRTUAL_ENV (
    echo ERROR: Failed to activate virtual environment.
    exit /b 1
)

echo [4/5] Upgrading pip/setuptools/wheel...
python -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip upgrade failed.
    exit /b 1
)

if exist "%REQ%" (
    echo Installing requirements from "%REQ%"...
    python -m pip install -r "%REQ%"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: 'pip install -r %REQ%' failed.
        exit /b 1
    )
) else (
    echo WARNING: "%REQ%" not found. Skipping requirements install.
)

if not exist "%MAIN%" (
    echo ERROR: "%MAIN%" not found.
    exit /b 1
)

echo [5/5] Launching app...
python "%MAIN%" --log info
endlocal
