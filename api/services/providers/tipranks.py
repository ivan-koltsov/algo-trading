"""
TipRanks market data and Wall Street analyst consensus provider.
Fetches top-ranked Wall Street analyst price targets and Buy/Hold/Sell ratings.
"""
from typing import Optional
import pandas as pd
import yfinance as yf

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    import requests as cffi_requests  # type: ignore

from .base import BaseDataProvider, MarketQuote


class TipRanksProvider(BaseDataProvider):
    """
    Data provider for TipRanks Wall Street analyst consensus and price targets.
    """

    @property
    def name(self) -> str:
        return "TipRanks Analysts"

    @property
    def identifier(self) -> str:
        return "tipranks"

    def get_realtime_quote(self, symbol: str) -> Optional[MarketQuote]:
        symbol_clean = symbol.upper().strip()
        url = f"https://www.tipranks.com/api/stocks/getData/?name={symbol_clean.lower()}"
        forecast_page_url = f"https://www.tipranks.com/stocks/{symbol_clean.lower()}/forecast"

        price = 0.0
        analyst_target_mean = None
        analyst_target_high = None
        analyst_target_low = None
        buy_count = 0
        hold_count = 0
        sell_count = 0
        rating = "Moderate Buy"

        try:
            r = cffi_requests.get(url, impersonate="chrome120", timeout=5)
            if r.status_code == 200:
                data = r.json()

                # Current price if available in prices payload
                if "prices" in data and isinstance(data["prices"], list) and len(data["prices"]) > 0:
                    price = float(data["prices"][-1].get("p", 0.0))

                # Price targets
                pt_consensus = data.get("ptConsensus", [])
                if pt_consensus and isinstance(pt_consensus, list):
                    pt = pt_consensus[0]
                    analyst_target_mean = round(float(pt.get("priceTarget", 0)), 2)
                    analyst_target_high = round(float(pt.get("high", 0)), 2)
                    analyst_target_low = round(float(pt.get("low", 0)), 2)

                # Consensus buy/hold/sell counts
                consensus_history = data.get("consensusOverTime", [])
                if consensus_history and isinstance(consensus_history, list):
                    latest_c = consensus_history[-1]
                    buy_count = int(latest_c.get("buy", 0))
                    hold_count = int(latest_c.get("hold", 0))
                    sell_count = int(latest_c.get("sell", 0))

                    total = buy_count + hold_count + sell_count
                    if total > 0:
                        if buy_count / total >= 0.7:
                            rating = "Strong Buy"
                        elif buy_count > sell_count:
                            rating = "Moderate Buy"
                        elif sell_count / total >= 0.5:
                            rating = "Sell"
                        else:
                            rating = "Hold"
        except Exception:
            pass

        # Fallback to yfinance if price or targets were not fully retrieved
        if price == 0.0 or analyst_target_mean is None:
            try:
                yf_ticker = yf.Ticker(symbol_clean)
                info = yf_ticker.info
                price = price or float(info.get("currentPrice") or info.get("regularMarketPrice") or 0.0)
                analyst_target_mean = analyst_target_mean or info.get("targetMeanPrice")
                analyst_target_high = analyst_target_high or info.get("targetHighPrice")
                analyst_target_low = analyst_target_low or info.get("targetLowPrice")
            except Exception:
                pass

        return MarketQuote(
            symbol=symbol_clean,
            price=price,
            url=forecast_page_url,
            source="tipranks",
            source_name="TipRanks Analysts",
            analyst_target_mean=analyst_target_mean,
            analyst_target_high=analyst_target_high,
            analyst_target_low=analyst_target_low,
            buy_count=buy_count,
            hold_count=hold_count,
            sell_count=sell_count,
            consensus_rating=rating,
        )

    def get_historical_ohlcv(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        symbol_clean = symbol.upper().strip()
        ticker = yf.Ticker(symbol_clean)
        return ticker.history(period=period)
