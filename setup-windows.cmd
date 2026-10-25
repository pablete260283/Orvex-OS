@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Instalacion finalizada. Abre run-windows.cmd.
pause
exit /b 0
:error
echo No se pudo instalar. Revisa que Python 3.11 o superior este instalado y que tengas conexion.
pause
exit /b 1
