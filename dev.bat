@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\dev-restart.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] dev-restart.ps1 failed.
  pause
  exit /b 1
)

exit /b 0
