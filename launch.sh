#!/bin/bash
# KidsPlay AI Studio - Master Launcher Script

APP_DIR="/home/alpesh/kids-game-studio"
PORT=8899
URL="http://127.0.0.1:${PORT}"
PID_FILE="${APP_DIR}/server.pid"
LOG_FILE="${APP_DIR}/server.log"

cd "${APP_DIR}" || exit 1

# Check if server is already responding
if curl -s "http://127.0.0.1:${PORT}/api/health" >/dev/null 2>&1; then
    echo "⚡ KidsPlay AI Studio backend is already running on ${URL}"
else
    UVICORN_BIN="/home/alpesh/.local/bin/uvicorn"
    if [ ! -f "${UVICORN_BIN}" ]; then
        UVICORN_BIN="uvicorn"
    fi
    echo "🚀 Starting KidsPlay AI Studio backend on port ${PORT}..."
    nohup "${UVICORN_BIN}" server.main:app --host 127.0.0.1 --port ${PORT} </dev/null >> "${LOG_FILE}" 2>&1 &
    SERVER_PID=$!
    echo ${SERVER_PID} > "${PID_FILE}"
    disown ${SERVER_PID} 2>/dev/null || true

    # Wait up to 10 seconds for startup
    MAX_WAIT=20
    COUNT=0
    while [ $COUNT -lt $MAX_WAIT ]; do
        if curl -s "http://127.0.0.1:${PORT}/api/health" >/dev/null 2>&1; then
            echo "✅ Backend successfully initialized!"
            break
        fi
        sleep 0.5
        COUNT=$((COUNT + 1))
    done
fi

# Open Desktop App Window / Browser
echo "🎮 Opening KidsPlay AI Studio..."
if command -v firefox >/dev/null 2>&1; then
    nohup firefox --new-window "${URL}" </dev/null >/dev/null 2>&1 &
    disown 2>/dev/null || true
elif command -v google-chrome >/dev/null 2>&1; then
    nohup google-chrome --app="${URL}" </dev/null >/dev/null 2>&1 &
    disown 2>/dev/null || true
elif command -v chromium >/dev/null 2>&1; then
    nohup chromium --app="${URL}" </dev/null >/dev/null 2>&1 &
    disown 2>/dev/null || true
else
    nohup xdg-open "${URL}" </dev/null >/dev/null 2>&1 &
    disown 2>/dev/null || true
fi

exit 0
