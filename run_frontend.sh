#!/usr/bin/env bash
# Start Frontend Only
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm packages..."
    npm install
fi

echo "🚀 Starting Vite Frontend at http://127.0.0.1:5173 ..."
npm run dev -- --host 127.0.0.1 --port 5173
