"""
Wall Street institutional consensus provider.
Aggregates analyst target price corridors, recommendation ratings, and opinion counts.
"""
from typing import Optional
import pandas as pd
import yfinance as yf

from .base import BaseDataProvider, MarketQuote


class WallStreetProvider(BaseDataProvider):
    """
    Data provider for Wall Street institutional analyst consensus.
    """

    @property
    def name(self) -> str:
        return "Wall Street Consensus"

    @property
    def identifier(self) -> str:
        return "wallstreet"

    def get_realtime_quote(self, symbol: str) -> Optional[MarketQuote]:
        symbol_clean = symbol.upper().strip()
        url = f"https://finance.yahoo.com/quote/{symbol_clean}/analysis"

        price = 0.0
        target_mean = None
        target_high = None
        target_low = None
        opinions_count = None
        rec_key = "Hold"

        try:
            ticker = yf.Ticker(symbol_clean)
            info = ticker.info or {}

            price = float(info.get("currentPrice") or info.get("regularMarketPrice") or 0.0)
            target_mean = info.get("targetMeanPrice")
            if target_mean:
                target_mean = round(float(target_mean), 2)
            target_high = info.get("targetHighPrice")
            if target_high:
                target_high = round(float(target_high), 2)
            target_low = info.get("targetLowPrice")
            if target_low:
                target_low = round(float(target_low), 2)

            opinions_count = info.get("numberOfAnalystOpinions")

            raw_rec = info.get("recommendationKey", "hold")
            rec_map = {
                "strong_buy": "Strong Buy",
                "buy": "Buy",
                "hold": "Hold",
                "underperform": "Underperform",
                "sell": "Sell",
            }
            rec_key = rec_map.get(str(raw_rec).lower(), str(raw_rec).title())
        except Exception:
            pass

        return MarketQuote(
            symbol=symbol_clean,
            price=price,
            url=url,
            source="wallstreet",
            source_name="Wall Street Consensus",
            analyst_target_mean=target_mean,
            analyst_target_high=target_high,
            analyst_target_low=target_low,
            consensus_rating=rec_key,
            analyst_opinions_count=opinions_count,
        )

    def get_historical_ohlcv(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        symbol_clean = symbol.upper().strip()
        ticker = yf.Ticker(symbol_clean)
        return ticker.history(period=period)
