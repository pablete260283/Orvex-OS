@echo off
setlocal
cd /d "%~dp0"
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
  set ORVEX_PY_VER=-3.12
) else (
  py -3.11 --version >nul 2>&1
  if errorlevel 1 (
    echo ORVEX necesita Python 3.12 o 3.11. Instala uno de ellos antes de continuar.
    goto error
  )
  set ORVEX_PY_VER=-3.11
)
py %ORVEX_PY_VER% -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Instalacion finalizada. Abre run-windows.cmd.
pause
exit /b 0
:error
echo No se pudo preparar ORVEX. Revisa Python y la conexion a Internet.
pause
exit /b 1
