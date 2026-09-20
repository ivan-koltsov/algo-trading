# Algo Trading Platform

A full-stack algorithmic trading analysis platform featuring a high-performance **FastAPI** backend for financial data processing and technical signal generation, paired with a modern **TanStack Start (React 19)** web application.

---

## Architecture Overview

| Service | Technology | Internal Port | Host Port | Description |
| :--- | :--- | :--- | :--- | :--- |
| **API** | Python 3.12, FastAPI, Pandas, yfinance | `8000` | `http://localhost:8000` | Historical OHLCV data fetching & SMA signal calculations |
| **UI** | Node 22, React 19, TanStack Start / Nitro | `3000` | `http://localhost:3000` | Interactive web dashboard and visual trading signals |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+ recommended)
- [Docker Compose](https://docs.docker.com/compose/) (v2.0+ recommended)

---

## Quick Start (Docker Compose)

The easiest way to run the entire stack is with Docker Compose:

### 1. One-Click Start Script

You can use the provided `start.sh` script to run both services either with Docker Compose or locally:

```bash
# Start with Docker Compose (builds and runs both containers)
./start.sh

# Or start locally on host (Python FastAPI + Node/Vite concurrently)
./start.sh --local

# Show all options
./start.sh --help
```

### 2. Manual Docker Compose

Alternatively, run docker compose directly:

```bash
docker compose up --build
```

To run in detached (background) mode:

```bash
docker compose up -d --build
```

### 3. Verify Services

Once the containers are up and healthy:

- **Web UI**: Open [http://localhost:3000](http://localhost:3000)
- **API Health / Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs) (Interactive Swagger UI)
- **Sample Signal Request**:
  ```bash
  curl http://localhost:8000/signal/AAPL/6mo
  ```

### 4. Viewing Logs

```bash
# Stream logs for all services
docker compose logs -f

# Stream logs for API only
docker compose logs -f api

# Stream logs for UI only
docker compose logs -f ui
```

### 5. Stopping the Services

```bash
# Stop containers
docker compose stop

# Stop and remove containers and networks
docker compose down

# Stop, remove containers, and remove volumes
docker compose down -v
```

---

## Standalone Docker Commands

If you prefer building and running containers individually without Docker Compose:

### Backend API

```bash
# 1. Build the image
docker build -t algo-trading-api ./api

# 2. Run the container
docker run -d \
  --name algo-trading-api \
  -p 8000:8000 \
  algo-trading-api

# 3. View logs
docker logs -f algo-trading-api

# 4. Stop and remove container
docker stop algo-trading-api && docker rm algo-trading-api
```

### Frontend UI

```bash
# 1. Build the image
docker build -t algo-trading-ui ./ui

# 2. Run the container
docker run -d \
  --name algo-trading-ui \
  -p 3000:3000 \
  -e VITE_API_URL=http://localhost:8000 \
  algo-trading-ui

# 3. View logs
docker logs -f algo-trading-ui

# 4. Stop and remove container
docker stop algo-trading-ui && docker rm algo-trading-ui
```

---

## Configuration & Environment Variables

### API Service (`api`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port for the Uvicorn ASGI server |
| `PYTHONUNBUFFERED` | `1` | Ensures standard output and error are flushed immediately |

### UI Service (`ui`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `NODE_ENV` | `production` | Node runtime environment |
| `PORT` | `3000` | Port for the Nitro HTTP server |
| `HOST` | `0.0.0.0` | Host binding interface |
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL accessible from the client or server |

---

## Local Development (Without Docker)

### Backend API

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend UI

```bash
cd ui
npm install
npm run dev
```

---

## Troubleshooting

### Port Already in Use
If port `8000` or `3000` is in use by another process:
```bash
# Find and stop processes on macOS / Linux:
lsof -i :8000
lsof -i :3000
```
Alternatively, modify the host port mappings in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000" # Maps host 8001 to container 8000
```

### Rebuilding After Code or Dependency Changes
Docker caches build layers for speed. To force a clean rebuild without cache:
```bash
docker compose build --no-cache
docker compose up -d
```

### Container Health Check Failing
Check container health status and detailed logs:
```bash
docker inspect --format='{{json .State.Health}}' algo-trading-api
docker inspect --format='{{json .State.Health}}' algo-trading-ui
```

---

## Deployment Options

### Option 1: Render (1-Click Blueprint)
The repository includes a [`render.yaml`](render.yaml) Blueprint file configuring both services:
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New +** -> **Blueprint**.
3. Connect your repository. Render will automatically build and deploy both the FastAPI backend and TanStack Start frontend.

### Option 2: Railway
1. Install Railway CLI (`npm i -g @railway/cli`) or connect GitHub on [railway.app](https://railway.app).
2. Create two services:
   - **API**: Root directory `/api` (uses `api/Dockerfile`)
   - **UI**: Root directory `/ui` (uses `ui/Dockerfile`), with environment variable `VITE_API_URL` set to the API public domain.

### Option 3: Cloud VPS (DigitalOcean / Hetzner / AWS EC2)
Using the existing Docker Compose setup:
```bash
git clone <your-repo-url>
cd algo-trading
./start.sh --build
```
You can place a reverse proxy like Caddy, Traefik, or Nginx in front for automatic SSL termination.