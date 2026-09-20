"""
Application configuration and environment settings.
"""
import os
from typing import List

APP_TITLE = "Algo Trading API"
APP_DESCRIPTION = (
    "Algorithmic trading technical analysis, signal generation, and quantitative "
    "forecasting with Google, Yahoo, TipRanks, Wall Street, FMP, and Danelfin AI providers"
)
APP_VERSION = "0.4.0"

# Environment detection: "development" vs "production"
APP_ENV = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")).lower().strip()
IS_PRODUCTION = APP_ENV == "production"
IS_DEVELOPMENT = not IS_PRODUCTION

# Environment-aware CORS configuration
if IS_PRODUCTION:
    CORS_ORIGINS: List[str] = [
        "https://algo-trading-ui-prod.onrender.com",
        "https://algo-trading-ui-dev.onrender.com",
        "*",  # Allow cross-origin requests for cloud API access
    ]
else:
    CORS_ORIGINS: List[str] = ["*"]

DEFAULT_TICKER = "AAPL"
DEFAULT_PERIOD = "6mo"
DEFAULT_PROVIDER = "google"
SUPPORTED_PROVIDERS = ["google", "yahoo", "tipranks", "wallstreet", "fmp", "danelfin"]
