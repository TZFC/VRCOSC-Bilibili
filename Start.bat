@echo off
:: This script hides the command prompt and runs the PowerShell launcher
if "%~1"=="hidden" goto :run
echo Set objShell = WScript.CreateObject("WScript.Shell") > "%temp%\hide.vbs"
echo objShell.Run "cmd /c """"%~s0"" hidden""", 0, False >> "%temp%\hide.vbs"
cscript //nologo "%temp%\hide.vbs"
del "%temp%\hide.vbs"
exit

:run
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "Launcher.ps1"
