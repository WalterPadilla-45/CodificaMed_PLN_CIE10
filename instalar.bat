@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ================================================================
echo   CodificaMed: Instalacion de Dependencias
echo ================================================================
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo [X] No se encontro Python en el PATH. Instala Python 3.11+.
  pause
  exit /b 1
)
if not exist ".venv" (
  echo Creando entorno virtual .venv...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo [X] Fallo la instalacion de dependencias.
  pause
  exit /b 1
)
if not exist ".env" copy .env.example .env >nul
echo.
echo ================================================================
echo   [OK] Instalacion completada con exito
echo ================================================================
echo Para iniciar ejecuta: iniciar.bat
echo.
pause
