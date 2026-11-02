#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PUERTO=8001
if [ -f .env ]; then
  VAL=$(grep -E '^PUERTO=' .env | cut -d= -f2 | tr -d ' \r')
  [ -n "$VAL" ] && PUERTO="$VAL"
fi
echo "Iniciando CodificaMed en http://localhost:$PUERTO"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PUERTO"
