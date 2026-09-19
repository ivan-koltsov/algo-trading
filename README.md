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

### 1. Build and Start All Services

```bash
docker compose up --build
```

To run in detached (background) mode:

```bash
docker compose up -d --build
```

### 2. Verify Services

Once the containers are up and healthy:

- **Web UI**: Open [http://localhost:3000](http://localhost:3000)
- **API Health / Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs) (Interactive Swagger UI)
- **Sample Signal Request**:
  ```bash
  curl http://localhost:8000/signal/AAPL/6mo
  ```

### 3. Viewing Logs

```bash
# Stream logs for all services
docker compose logs -f

# Stream logs for API only
docker compose logs -f api

# Stream logs for UI only
docker compose logs -f ui
```

### 4. Stopping the Services

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

## Production Deployment Recommendations

1. **Reverse Proxy (Nginx / Caddy / Traefik)**:
   Place an SSL-terminating reverse proxy in front of both services to route traffic (e.g. `/api/*` to the FastAPI container, and `/*` to the UI container) under a single domain with HTTPS.
2. **Cloud Containers**:
   Both Dockerfiles are OCI-compliant and ready to deploy to services like AWS ECS / Fargate, Google Cloud Run, Azure Container Apps, or DigitalOcean App Platform.
3. **Security**:
   Both Docker images run under non-root unprivileged users (`appuser` UID 1000 for API, `reactapp` UID 1001 for UI).