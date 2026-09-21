#!/usr/bin/env bash
# ==============================================================================
# Algo Trading Platform - Start Script
# Runs both Backend API (FastAPI) and Frontend UI (TanStack Start / React)
# Supports Development (port 8001) and Production (port 8000) profiles.
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

# Parse CLI arguments for environment override
APP_ENV="${APP_ENV:-development}"
for arg in "$@"; do
    case "$arg" in
        --prod)
            APP_ENV="production"
            ;;
        --dev)
            APP_ENV="development"
            ;;
    esac
done

export APP_ENV
export VITE_APP_ENV="$APP_ENV"

# Default ports: Dev FastAPI on 8001 (matching AGENTS.md), Prod FastAPI on 8000
if [ "$APP_ENV" = "production" ]; then
    DEFAULT_API_PORT=8000
else
    DEFAULT_API_PORT=8001
fi

API_PORT="${API_PORT:-$DEFAULT_API_PORT}"
UI_PORT="${UI_PORT:-3000}"
export API_PORT
export UI_PORT
export VITE_API_URL="http://localhost:${API_PORT}"

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
    echo "  --dev, -l, --local  Run stack locally in Development profile (API: 8001, UI: 3000) [default]"
    echo "  --prod              Run stack locally in Production profile (API: 8000, UI: 3000)"
    echo "  --docker, -d        Run stack via Docker Compose"
    echo "  --build, -b         Build and run stack via Docker Compose"
    echo "  --stop, -s          Stop running Docker containers"
    echo "  --help, -h          Display this help message"
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
        print_error "Docker daemon is not running. Please start Docker Desktop or use './start.sh --dev'."
        exit 1
    fi

    if [ "$build_flag" = true ]; then
        print_info "Building and starting containers with Docker Compose in [${APP_ENV^^}] mode..."
        docker compose up --build
    else
        print_info "Starting containers with Docker Compose in [${APP_ENV^^}] mode..."
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
    print_info "Starting Algo Trading stack locally in [${APP_ENV^^}] mode..."

    # Check ports
    if check_port "$API_PORT"; then
        local api_pid
        api_pid=$(lsof -Pi :"$API_PORT" -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true)
        print_warn "Port $API_PORT is already in use (PID ${api_pid}). Please terminate the process or configure API_PORT."
    fi
    if check_port "$UI_PORT"; then
        local ui_pid
        ui_pid=$(lsof -Pi :"$UI_PORT" -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true)
        print_warn "Port $UI_PORT is already in use (PID ${ui_pid}). Please terminate the process or configure UI_PORT."
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
    print_info "Starting Backend API on http://localhost:${API_PORT} [APP_ENV=${APP_ENV}]..."
    (cd api && APP_ENV="$APP_ENV" PORT="$API_PORT" $UVICORN_CMD main:app --reload --port "$API_PORT") &
    API_PID=$!

    # Wait briefly for API initialization
    sleep 2

    # Start Frontend UI
    print_info "Starting Frontend UI on http://localhost:${UI_PORT} [VITE_APP_ENV=${VITE_APP_ENV}, VITE_API_URL=${VITE_API_URL}]..."
    (cd ui && VITE_APP_ENV="$VITE_APP_ENV" VITE_API_URL="$VITE_API_URL" npm run dev -- --port "$UI_PORT") &
    UI_PID=$!

    echo ""
    print_success "Stack is running in [${APP_ENV^^}] mode!"
    echo "  - Environment: ${APP_ENV} (VITE_APP_ENV=${VITE_APP_ENV})"
    echo "  - Backend API: http://localhost:${API_PORT} (Health: http://localhost:${API_PORT}/health)"
    echo "  - Frontend UI: http://localhost:${UI_PORT} (VITE_API_URL=${VITE_API_URL})"
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
    --prod)
        APP_ENV="production"
        DEFAULT_API_PORT=8000
        API_PORT="${API_PORT:-$DEFAULT_API_PORT}"
        export VITE_API_URL="http://localhost:${API_PORT}"
        run_local
        ;;
    --local|-l|--dev)
        APP_ENV="development"
        DEFAULT_API_PORT=8001
        API_PORT="${API_PORT:-$DEFAULT_API_PORT}"
        export VITE_API_URL="http://localhost:${API_PORT}"
        run_local
        ;;
    --stop|-s)
        stop_docker
        ;;
    --help|-h)
        show_help
        ;;
    "")
        # Default behavior: prefer docker compose if docker is active, otherwise fallback to local dev
        if docker info >/dev/null 2>&1; then
            print_info "Docker detected. Starting via Docker Compose (pass --dev or --local to run natively)..."
            run_docker true
        else
            print_info "Docker daemon not running. Falling back to local native execution in [${APP_ENV^^}] mode..."
            run_local
        fi
        ;;
    *)
        print_error "Unknown option: $MODE"
        show_help
        exit 1
        ;;
esac
