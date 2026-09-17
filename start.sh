#!/usr/bin/env bash
# ==============================================================================
# ProcureShield AI — Turnkey Full-Stack Startup Script
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "  🛡️  Starting ProcureShield AI Platform"
echo "=========================================================="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.10+."
    exit 1
fi

# 2. Check Node
if ! command -v npm &> /dev/null; then
    echo "⚠️  Node/npm not found. Backend will serve pre-compiled frontend at http://127.0.0.1:8000"
    SERVE_STANDALONE=true
else
    SERVE_STANDALONE=false
fi

# 3. Backend Virtual Environment Setup
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment in backend/venv..."
    python3 -m venv backend/venv
fi

echo "📦 Activating virtual environment & verifying dependencies..."
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt

# 4. Check Database
if [ ! -f "backend/procureshield.db" ]; then
    echo "⚙️ Initializing database..."
    python3 -m scripts.seed_database
fi

# 5. Launch Backend
echo "🚀 Launching FastAPI Backend on http://127.0.0.1:8000 ..."
PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Trap signals for graceful shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down ProcureShield AI services..."
    kill $BACKEND_PID 2>/dev/null || true
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo "✓ All processes stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 6. Launch Frontend if npm is available
if [ "$SERVE_STANDALONE" = false ]; then
    echo "🚀 Starting Vite Frontend dev server..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing npm dependencies (first run only)..."
        npm install --silent
    fi
    npm run dev -- --host 127.0.0.1 --port 5173 &
    FRONTEND_PID=$!
    cd ..
fi

echo ""
echo "=========================================================="
echo "  ✅ ProcureShield AI is Live and Ready!"
echo "=========================================================="
if [ "$SERVE_STANDALONE" = false ]; then
    echo "  🖥️  Web App (Vite):       http://127.0.0.1:5173"
fi
echo "  ⚡ Backend API & App:     http://127.0.0.1:8000"
echo "  📖 Swagger API Docs:      http://127.0.0.1:8000/docs"
echo "=========================================================="
echo "  Demo Credentials:"
echo "  - Investigator:  sarah.chen@procureshield.gov.in (investigator123)"
echo "  - Citizen:       rohan.verma@gmail.com (citizen123)"
echo "=========================================================="
echo "  Press Ctrl+C to stop all servers."
echo "=========================================================="

wait
