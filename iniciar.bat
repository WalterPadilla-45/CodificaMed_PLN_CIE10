@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PUERTO=8001
if exist ".env" (
  for /f "tokens=2 delims==" %%a in ('findstr /b "PUERTO=" .env 2^>nul') do set PUERTO=%%a
)

if exist ".venv\Scripts\activate.bat" (
  call .venv\Scripts\activate.bat
)

echo.
echo ================================================================
echo   CodificaMed - Codificacion CIE-10 con PLN
echo ================================================================
echo.

rem Liberar puerto si estaba tomado
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":%PUERTO% .*LISTENING"') do (
  taskkill /f /pid %%a >nul 2>nul
)

rem Iniciar Ollama si no esta corriendo
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if errorlevel 1 (
  echo [!] Iniciando servidor local Ollama en segundo plano...
  if exist "D:\Ollama\ollama.exe" (
    start /min "" "D:\Ollama\ollama.exe" serve
  ) else (
    start /min "" ollama serve
  )
  ping 127.0.0.1 -n 3 >nul
) else (
  echo [OK] Servidor local Ollama detectado en ejecucion.
)

echo.
echo   Servidor web: http://localhost:%PUERTO%
echo   Abriendo navegador en 2 segundos...
echo   Para detener: Ctrl + C
echo.

start "" cmd /c "ping 127.0.0.1 -n 4 >nul ^& start http://localhost:%PUERTO%"

python -m uvicorn app.main:app --host 0.0.0.0 --port %PUERTO%
if errorlevel 1 (
  echo.
  echo [X] Error al ejecutar CodificaMed.
)
pause
