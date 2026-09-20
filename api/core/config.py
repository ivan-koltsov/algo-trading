"""
Application configuration and environment settings.
"""
from typing import List

APP_TITLE = "Algo Trading API"
APP_DESCRIPTION = (
    "Algorithmic trading technical analysis, signal generation, and quantitative "
    "forecasting with Google & Yahoo Finance providers"
)
APP_VERSION = "0.3.0"

CORS_ORIGINS: List[str] = ["*"]

DEFAULT_TICKER = "AAPL"
DEFAULT_PERIOD = "6mo"
DEFAULT_PROVIDER = "yahoo"
SUPPORTED_PROVIDERS = ["yahoo", "google"]
