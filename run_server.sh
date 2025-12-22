#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Default port
DEFAULT_PORT=44043
MAX_RETRIES=3

start_server() {
    # Kill any existing server on default port
    lsof -ti:$DEFAULT_PORT | xargs kill -9 2>/dev/null || true
    pkill -9 -f "python server.py" 2>/dev/null || true
    sleep 0.5

    # Start the server in the background, fully detached
    nohup uv run python server.py > /dev/null 2>&1 &
    disown

    # Wait for server to start
    for i in {1..10}; do
        sleep 0.5
        if lsof -ti:$DEFAULT_PORT >/dev/null 2>&1; then
            return 0
        fi
    done
    return 1
}

# Try to start server with retries
for attempt in $(seq 1 $MAX_RETRIES); do
    if start_server; then
        echo "Server running at http://localhost:$DEFAULT_PORT"
        echo "Visualizer: http://localhost:$DEFAULT_PORT/index.html"
        exit 0
    fi

    if [ $attempt -lt $MAX_RETRIES ]; then
        echo "Attempt $attempt failed, retrying..." >&2
    fi
done

echo "Failed to start server after $MAX_RETRIES attempts. Try running ./run_server.sh again." >&2
exit 1
