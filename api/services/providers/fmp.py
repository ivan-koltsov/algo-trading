"""
Financial Modeling Prep (FMP) valuation and Discounted Cash Flow (DCF) provider.
Computes intrinsic value, fair value targets, and valuation premium/discount.
"""
import os
from typing import Optional
import pandas as pd
import yfinance as yf

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    import requests as cffi_requests  # type: ignore

from .base import BaseDataProvider, MarketQuote


class FmpProvider(BaseDataProvider):
    """
    Data provider for Financial Modeling Prep valuation and intrinsic DCF models.
    """

    @property
    def name(self) -> str:
        return "FMP Valuation & DCF"

    @property
    def identifier(self) -> str:
        return "fmp"

    def get_realtime_quote(self, symbol: str) -> Optional[MarketQuote]:
        symbol_clean = symbol.upper().strip()
        fmp_url = f"https://site.financialmodelingprep.com/financial-summary/{symbol_clean}"
        api_key = os.getenv("FMP_API_KEY")

        price = 0.0
        dcf_value = None
        upside_pct = None
        valuation_status = "Fairly Valued"

        # Attempt API query if key is configured
        if api_key:
            try:
                url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{symbol_clean}?apikey={api_key}"
                r = cffi_requests.get(url, timeout=5)
                if r.status_code == 200:
                    items = r.json()
                    if isinstance(items, list) and len(items) > 0:
                        first = items[0]
                        price = float(first.get("Stock Price", 0.0))
                        dcf_val = first.get("dcf")
                        if dcf_val:
                            dcf_value = round(float(dcf_val), 2)
            except Exception:
                pass

        # DCF Intrinsic Cash Flow model calculation
        try:
            ticker = yf.Ticker(symbol_clean)
            info = ticker.info or {}
            price = price or float(info.get("currentPrice") or info.get("regularMarketPrice") or 0.0)

            if dcf_value is None and price > 0:
                cf = ticker.cashflow
                fcf = 0.0
                if cf is not None and "Free Cash Flow" in cf.index and len(cf.loc["Free Cash Flow"]) > 0:
                    fcf = float(cf.loc["Free Cash Flow"].iloc[0])

                shares = float(info.get("sharesOutstanding") or 1)
                if fcf > 0 and shares > 0:
                    growth_rate = 0.08
                    discount_rate = 0.09
                    terminal_multiple = 18.0

                    pv = sum([(fcf * (1 + growth_rate)**t) / ((1 + discount_rate)**t) for t in range(1, 6)])
                    tv = (fcf * (1 + growth_rate)**5 * terminal_multiple) / ((1 + discount_rate)**5)
                    ev = pv + tv
                    dcf_calc = ev / shares
                    dcf_value = round(float(dcf_calc), 2)
        except Exception:
            pass

        # Compute upside/downside and status
        if dcf_value and price > 0:
            upside_pct = round(((dcf_value - price) / price) * 100, 2)
            if upside_pct > 15.0:
                valuation_status = "Undervalued (Buy)"
            elif upside_pct < -15.0:
                valuation_status = "Overvalued (Caution)"
            else:
                valuation_status = "Fairly Valued"

        return MarketQuote(
            symbol=symbol_clean,
            price=price,
            url=fmp_url,
            source="fmp",
            source_name="FMP Valuation & DCF",
            dcf_intrinsic_value=dcf_value,
            dcf_upside_pct=upside_pct,
            valuation_status=valuation_status,
        )

    def get_historical_ohlcv(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        symbol_clean = symbol.upper().strip()
        ticker = yf.Ticker(symbol_clean)
        return ticker.history(period=period)
