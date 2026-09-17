#!/usr/bin/env bash
# Start Backend Only
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
fi
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt

echo "🚀 Starting FastAPI Backend at http://127.0.0.1:8000 ..."
echo "📖 Swagger Docs: http://127.0.0.1:8000/docs"
PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
