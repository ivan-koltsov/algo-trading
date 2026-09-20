#!/usr/bin/env bash
# ==============================================================================
# Algo Trading Platform - Start Script
# Runs both Backend API (FastAPI) and Frontend UI (TanStack Start / React)
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env file if available
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.env"
    set +a
fi

API_PORT="${API_PORT:-8000}"
UI_PORT="${UI_PORT:-3000}"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "Usage: ./start.sh [MODE]"
    echo ""
    echo "Modes:"
    echo "  --docker, -d     Run stack via Docker Compose (default if Docker daemon is running)"
    echo "  --build, -b      Build and run stack via Docker Compose"
    echo "  --local, -l      Run stack locally on host (Python venv + Node/Vite)"
    echo "  --stop, -s       Stop running Docker containers"
    echo "  --help, -h       Display this help message"
    echo ""
}

# Check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0 # Port is in use
    else
        return 1 # Port is free
    fi
}

# Run via Docker Compose
run_docker() {
    local build_flag=$1
    print_info "Checking Docker daemon status..."

    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker Desktop or use './start.sh --local'."
        exit 1
    fi

    if [ "$build_flag" = true ]; then
        print_info "Building and starting containers with Docker Compose..."
        docker compose up --build
    else
        print_info "Starting containers with Docker Compose..."
        docker compose up
    fi
}

# Stop Docker Compose containers
stop_docker() {
    print_info "Stopping Docker Compose containers..."
    docker compose down
    print_success "Containers stopped."
}

# Run locally on host
run_local() {
    print_info "Starting Algo Trading stack locally..."

    # Check ports
    if check_port "$API_PORT"; then
        print_warn "Port $API_PORT is already in use. Please terminate the process or configure API_PORT in .env."
    fi
    if check_port "$UI_PORT"; then
        print_warn "Port $UI_PORT is already in use. Please terminate the process or configure UI_PORT in .env."
    fi

    # Determine Python / Uvicorn runner
    UVICORN_CMD=""
    if [ -x "./.venv/bin/uvicorn" ]; then
        UVICORN_CMD="./.venv/bin/uvicorn"
    elif [ -x "./api/.venv/bin/uvicorn" ]; then
        UVICORN_CMD="./api/.venv/bin/uvicorn"
    elif command -v uv >/dev/null 2>&1; then
        UVICORN_CMD="uv run --project api uvicorn"
    elif command -v uvicorn >/dev/null 2>&1; then
        UVICORN_CMD="uvicorn"
    else
        print_error "Could not locate 'uvicorn' in .venv or system PATH. Please run 'pip install -r api/requirements.txt'."
        exit 1
    fi

    # Check Node.js
    if ! command -v npm >/dev/null 2>&1; then
        print_error "Node.js / npm is not installed. Please install Node.js (v20+) or use Docker."
        exit 1
    fi

    # Check UI node_modules
    if [ ! -d "ui/node_modules" ]; then
        print_info "Installing UI dependencies (npm install)..."
        (cd ui && npm install)
    fi

    # Trap to cleanly stop child processes on exit/interrupt
    API_PID=""
    UI_PID=""

    cleanup() {
        echo ""
        print_info "Stopping services..."
        if [ -n "$API_PID" ] && kill -0 "$API_PID" 2>/dev/null; then
            kill "$API_PID" 2>/dev/null || true
        fi
        if [ -n "$UI_PID" ] && kill -0 "$UI_PID" 2>/dev/null; then
            kill "$UI_PID" 2>/dev/null || true
        fi
        wait "$API_PID" 2>/dev/null || true
        wait "$UI_PID" 2>/dev/null || true
        print_success "All services stopped."
        exit 0
    }

    trap cleanup SIGINT SIGTERM EXIT

    # Start Backend API
    print_info "Starting Backend API on http://localhost:${API_PORT}..."
    (cd api && $UVICORN_CMD main:app --reload --port "$API_PORT") &
    API_PID=$!

    # Wait briefly for API initialization
    sleep 2

    # Start Frontend UI
    print_info "Starting Frontend UI on http://localhost:${UI_PORT}..."
    (cd ui && npm run dev -- --port "$UI_PORT") &
    UI_PID=$!

    echo ""
    print_success "Stack is running!"
    echo "  - Backend API: http://localhost:${API_PORT} (Swagger docs: http://localhost:${API_PORT}/docs)"
    echo "  - Frontend UI: http://localhost:${UI_PORT}"
    echo ""
    print_info "Press Ctrl+C to terminate both services."
    echo ""

    # Wait for either background process to exit
    wait -n "$API_PID" "$UI_PID"
}

# Main mode selection
MODE="${1:-}"

case "$MODE" in
    --docker|-d)
        run_docker false
        ;;
    --build|-b)
        run_docker true
        ;;
    --local|-l|--dev)
        run_local
        ;;
    --stop|-s)
        stop_docker
        ;;
    --help|-h)
        show_help
        ;;
    "")
        # Default behavior: prefer docker compose if docker is active, otherwise fallback to local
        if docker info >/dev/null 2>&1; then
            print_info "Docker detected. Starting via Docker Compose (pass --local to run natively)..."
            run_docker true
        else
            print_info "Docker daemon not running. Falling back to local native execution..."
            run_local
        fi
        ;;
    *)
        print_error "Unknown option: $MODE"
        show_help
        exit 1
        ;;
esac
