#!/usr/bin/env bash
# CodificaMed - Instalación en Linux / macOS
set -e
cd "$(dirname "$0")"
echo "=== CodificaMed: Instalación de entorno ==="
if ! command -v python3 >/dev/null 2>&1; then
  echo "[X] No se encontró python3. Instala Python 3.11 o superior."
  exit 1
fi
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
echo
echo "=== Listo ==="
echo "Ejecuta: ./iniciar.sh"
