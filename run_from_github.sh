#!/usr/bin/env bash
# ====================================================================
# KidsPlay AI Studio • 1-Command Startup Script from GitHub Clone
# ====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎮 ========================================================"
echo "   KidsPlay AI Studio (કિડ્સ ગેમ સ્ટુડિયો) • Launching..."
echo "   Powered by Gemini 4 Argon Frontier AI Engine"
echo "============================================================"

# 1. Check Python version
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

# 2. Setup Virtual Environment if missing
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Install requirements
echo "📦 Checking and installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 4. Initialize .env if missing
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env from .env.example..."
    cp .env.example .env
    echo "💡 Note: Please edit .env with your Google Gemini API Key for online reasoning."
fi

# 5. Ensure data directory exists
mkdir -p data

# 6. Launch Server
PORT="${PORT:-8899}"
HOST="${HOST:-0.0.0.0}"

echo "🚀 Starting KidsPlay AI Studio server on http://localhost:${PORT}"
echo "✨ Open your browser at: http://localhost:${PORT}"
echo "🛑 Press CTRL+C to stop."

exec uvicorn server.main:app --host "$HOST" --port "$PORT"
