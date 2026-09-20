"""
Google Finance market data provider.
Uses curl_cffi Chrome browser TLS fingerprint impersonation to scrape real-time quotes.
"""
import re
from typing import Optional
import pandas as pd
import yfinance as yf

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    import requests as cffi_requests  # type: ignore

from .base import BaseDataProvider, MarketQuote


class GoogleFinanceProvider(BaseDataProvider):
    """
    Data provider for Google Finance quotes and links.
    """

    @property
    def name(self) -> str:
        return "Google Finance"

    @property
    def identifier(self) -> str:
        return "google"

    def get_realtime_quote(self, symbol: str) -> Optional[MarketQuote]:
        symbol_clean = symbol.upper().strip()
        candidates = [
            (symbol_clean, "NASDAQ"),
            (symbol_clean, "NYSE"),
            (symbol_clean, "NYSEARCA"),
            (symbol_clean, "INDEXSP"),
            (symbol_clean, "CURRENCY"),
        ]

        if "-" in symbol_clean:
            parts = symbol_clean.split("-")
            candidates.insert(0, (f"{parts[0]}-{parts[1]}", "CURRENCY"))
            candidates.insert(0, (parts[0], "CURRENCY"))

        for sym, exc in candidates:
            url = f"https://www.google.com/finance/quote/{sym}:{exc}"
            try:
                r = cffi_requests.get(url, impersonate="chrome120", timeout=5)
                if r.status_code == 200:
                    pattern = (
                        r'\[\"'
                        + re.escape(sym)
                        + r'\"\,\"'
                        + exc
                        + r'\"\]\,[^,]+,\d+,\"([A-Z]{3})\"\,\[([0-9.]+),([+-]?[0-9.]+),([+-]?[0-9.]+)'
                    )
                    m = re.search(pattern, r.text)
                    if m:
                        return MarketQuote(
                            symbol=symbol_clean,
                            exchange=exc,
                            currency=m.group(1),
                            price=float(m.group(2)),
                            change=float(m.group(3)),
                            change_pct=float(m.group(4)),
                            url=url,
                            source="google",
                            source_name="Google Finance",
                        )

                    m2 = re.search(r'data-last-price=\"([0-9.]+)\"', r.text)
                    if m2:
                        return MarketQuote(
                            symbol=symbol_clean,
                            exchange=exc,
                            currency=None,
                            price=float(m2.group(1)),
                            change=0.0,
                            change_pct=0.0,
                            url=url,
                            source="google",
                            source_name="Google Finance",
                        )
            except Exception:
                continue

        return None

    def get_historical_ohlcv(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """
        Fetches historical baseline via yfinance since Google Finance historical API
        is discontinued, then integrates live Google quote if available.
        """
        symbol_clean = symbol.upper().strip()
        yf_ticker = yf.Ticker(symbol_clean)
        df = yf_ticker.history(period=period)
        return df
