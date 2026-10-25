@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Primero ejecuta setup-windows.cmd para instalar las dependencias.
  pause
  exit /b 1
)
set PYTHONPATH=%CD%\src
.venv\Scripts\python.exe -m orvex
if errorlevel 1 pause
