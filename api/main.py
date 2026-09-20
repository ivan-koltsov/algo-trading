"""
Application entrypoint for Algo Trading API.
Configures FastAPI, CORS middleware, and mounts modular routers.
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure api directory is on sys.path for direct uvicorn invocations
api_dir = Path(__file__).resolve().parent
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

from core.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, CORS_ORIGINS
from routers import health_router, signals_router, forecast_router
from services.market_service import market_service

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register modular sub-routers
app.include_router(health_router)
app.include_router(signals_router)
app.include_router(forecast_router)

# Backward-compatibility alias for direct module access
fetch_and_calculate_signals = market_service.fetch_and_calculate_signals


if __name__ == "__main__":
    y_res = fetch_and_calculate_signals("AAPL", "6mo", source="yahoo")
    g_res = fetch_and_calculate_signals("AAPL", "6mo", source="google")
    print(f"Yahoo: {y_res['source_name']} -> Price: ${y_res['current_price']} | URL: {y_res['source_url']}")
    print(f"Google: {g_res['source_name']} -> Price: ${g_res['current_price']} | URL: {g_res['source_url']}")