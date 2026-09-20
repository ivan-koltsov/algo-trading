"""
Application configuration and environment settings.
"""
from typing import List

APP_TITLE = "Algo Trading API"
APP_DESCRIPTION = (
    "Algorithmic trading technical analysis, signal generation, and quantitative "
    "forecasting with Google, Yahoo, TipRanks, Wall Street, FMP, and Danelfin AI providers"
)
APP_VERSION = "0.4.0"

CORS_ORIGINS: List[str] = ["*"]

DEFAULT_TICKER = "AAPL"
DEFAULT_PERIOD = "6mo"
DEFAULT_PROVIDER = "google"
SUPPORTED_PROVIDERS = ["google", "yahoo", "tipranks", "wallstreet", "fmp", "danelfin"]
