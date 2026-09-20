"""
Market analysis service coordinating data providers, technical analysis, and forecasting.
"""
from typing import Dict, Optional
from fastapi import HTTPException
import pandas as pd

from .providers.base import BaseDataProvider, MarketQuote
from .providers.yahoo import YahooFinanceProvider
from .providers.google import GoogleFinanceProvider
from .technical_analysis import (
    compute_technical_indicators,
    determine_market_trend,
    get_latest_signal_label,
    build_historical_bars,
)
from .forecasting import (
    calculate_drift_and_volatility,
    generate_gbm_forecast,
    calculate_horizon_projection,
)


class MarketService:
    """
    Coordinates data providers and quantitative algorithms.
    """

    def __init__(self):
        self._providers: Dict[str, BaseDataProvider] = {
            "yahoo": YahooFinanceProvider(),
            "google": GoogleFinanceProvider(),
        }

    def get_provider(self, source: str) -> BaseDataProvider:
        key = source.lower().strip() if source else "yahoo"
        return self._providers.get(key, self._providers["yahoo"])

    def fetch_and_calculate_signals(
        self,
        ticker: str = "AAPL",
        period: str = "6mo",
        source: str = "yahoo",
    ) -> dict:
        ticker_clean = ticker.upper().strip()
        provider = self.get_provider(source)

        # 1. Fetch baseline historical data
        try:
            df = provider.get_historical_ohlcv(ticker_clean, period=period)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Failed to fetch market data: {str(e)}")

        if df.empty or len(df) < 5:
            raise HTTPException(
                status_code=404,
                detail=f"No price data found for ticker '{ticker_clean}' over period '{period}'. Please verify the symbol.",
            )

        # 2. Compute technical indicators
        df = compute_technical_indicators(df)

        # 3. Format historical bars
        historical = build_historical_bars(df)

        # 4. Fetch real-time quote if Google Finance or provider override
        close_series = df["Close"].dropna()
        last_price = float(close_series.iloc[-1])
        first_price = float(close_series.iloc[0])

        realtime_quote: Optional[MarketQuote] = None
        if provider.identifier == "google":
            realtime_quote = provider.get_realtime_quote(ticker_clean)

        if realtime_quote and realtime_quote.price > 0:
            last_price = float(realtime_quote.price)
            if len(historical) > 0:
                historical[-1]["close"] = round(last_price, 2)
                if historical[-1]["high"] and last_price > historical[-1]["high"]:
                    historical[-1]["high"] = round(last_price, 2)
                if historical[-1]["low"] and last_price < historical[-1]["low"]:
                    historical[-1]["low"] = round(last_price, 2)

        price_change = round(last_price - first_price, 2)
        price_change_pct = round(((last_price - first_price) / first_price) * 100, 2)
        last_date = df.index[-1]

        # 5. Quantitative Forecasting Engine
        drift, daily_vol, ann_vol = calculate_drift_and_volatility(close_series)
        forecast_series = generate_gbm_forecast(last_price, last_date, drift, daily_vol, days=30)

        target_7d = forecast_series[min(5, len(forecast_series) - 1)]
        target_14d = forecast_series[min(10, len(forecast_series) - 1)]
        target_30d = forecast_series[min(21, len(forecast_series) - 1)]

        # 6. Trend and signals
        latest_signal = int(df["Signal"].iloc[-1])
        signal_label = get_latest_signal_label(latest_signal)

        last_sma_20 = (
            round(float(df["SMA_20"].iloc[-1]), 2)
            if not pd.isna(df["SMA_20"].iloc[-1])
            else None
        )
        last_sma_50 = (
            round(float(df["SMA_50"].iloc[-1]), 2)
            if not pd.isna(df["SMA_50"].iloc[-1])
            else None
        )
        trend = determine_market_trend(last_sma_20, last_sma_50, last_price)

        # 7. Provider metadata
        if provider.identifier == "google":
            source_name = "Google Finance"
            source_url = (
                realtime_quote.url
                if realtime_quote and realtime_quote.url
                else f"https://www.google.com/finance/quote/{ticker_clean}:NASDAQ"
            )
        else:
            source_name = "Yahoo Finance"
            source_url = f"https://finance.yahoo.com/quote/{ticker_clean}"

        return {
            "ticker": ticker_clean,
            "period": period,
            "source": provider.identifier,
            "source_name": source_name,
            "source_url": source_url,
            "current_price": round(last_price, 2),
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "latest_date": last_date.strftime("%Y-%m-%d"),
            "historical": historical,
            "forecast": forecast_series,
            "metrics": {
                "latest_signal": latest_signal,
                "latest_signal_label": signal_label,
                "trend": trend,
                "sma_20": last_sma_20,
                "sma_50": last_sma_50,
                "volatility_annualized_pct": round(ann_vol * 100, 1),
                "forecast_7d": calculate_horizon_projection(target_7d, last_price),
                "forecast_14d": calculate_horizon_projection(target_14d, last_price),
                "forecast_30d": calculate_horizon_projection(target_30d, last_price),
            },
            "disclaimer": (
                "Quantitative forecasts are statistical simulations based on historical drift and "
                "volatility and do not constitute financial advice."
            ),
        }


# Singleton market service instance
market_service = MarketService()
