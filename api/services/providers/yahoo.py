"""
Yahoo Finance market data provider using yfinance.
"""
from typing import Optional
import pandas as pd
import yfinance as yf

from .base import BaseDataProvider, MarketQuote


class YahooFinanceProvider(BaseDataProvider):
    """
    Data provider for Yahoo Finance historical OHLCV and market quotes.
    """

    @property
    def name(self) -> str:
        return "Yahoo Finance"

    @property
    def identifier(self) -> str:
        return "yahoo"

    def get_realtime_quote(self, symbol: str) -> Optional[MarketQuote]:
        symbol_clean = symbol.upper().strip()
        try:
            ticker = yf.Ticker(symbol_clean)
            fast_info = getattr(ticker, "fast_info", None)
            price = None
            if fast_info:
                price = getattr(fast_info, "last_price", None)

            if price is None:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])

            if price is not None:
                return MarketQuote(
                    symbol=symbol_clean,
                    price=float(price),
                    url=f"https://finance.yahoo.com/quote/{symbol_clean}",
                    source="yahoo",
                    source_name="Yahoo Finance",
                )
        except Exception:
            pass

        return MarketQuote(
            symbol=symbol_clean,
            price=0.0,
            url=f"https://finance.yahoo.com/quote/{symbol_clean}",
            source="yahoo",
            source_name="Yahoo Finance",
        )

    def get_historical_ohlcv(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        symbol_clean = symbol.upper().strip()
        ticker = yf.Ticker(symbol_clean)
        df = ticker.history(period=period)
        return df
