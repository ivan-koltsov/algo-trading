import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import yfinance as yf

app = FastAPI(
    title="Algo Trading API",
    description="Algorithmic trading technical analysis, signal generation, and quantitative forecasting powered by YFinance",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch_and_calculate_signals(ticker: str = "AAPL", period: str = "6mo") -> dict:
    """
    Fetches historical OHLCV data for a ticker, calculates SMA technical indicators,
    detects crossover buy/sell signals, and computes quantitative forecast predictions
    for upcoming days and weeks (7d, 14d, 30d).
    """
    ticker_clean = ticker.upper().strip()
    try:
        yf_ticker = yf.Ticker(ticker_clean)
        df = yf_ticker.history(period=period)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch market data from YFinance: {str(e)}")

    if df.empty or len(df) < 5:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for ticker '{ticker_clean}' over period '{period}'. Please verify the symbol.",
        )

    # Standardize column names
    df = df.copy()

    # Calculate indicators using Pandas rolling windows
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()

    # Generate signals: 1 for bullish (Buy), -1 for bearish (Sell), 0 for neutral/insufficient data
    df["Signal"] = 0
    df.loc[df["SMA_20"] > df["SMA_50"], "Signal"] = 1
    df.loc[df["SMA_20"] < df["SMA_50"], "Signal"] = -1

    # Detect crossover events
    df["Prev_Signal"] = df["Signal"].shift(1).fillna(0)
    df["Crossover"] = None
    df.loc[(df["Signal"] == 1) & (df["Prev_Signal"] != 1), "Crossover"] = "BUY"
    df.loc[(df["Signal"] == -1) & (df["Prev_Signal"] != -1), "Crossover"] = "SELL"

    # Historical OHLCV + signals array formatted for charting
    historical = []
    for idx, row in df.iterrows():
        # idx is a Timestamp
        time_str = idx.strftime("%Y-%m-%d")
        historical.append(
            {
                "time": time_str,
                "open": round(float(row["Open"]), 2) if not pd.isna(row["Open"]) else None,
                "high": round(float(row["High"]), 2) if not pd.isna(row["High"]) else None,
                "low": round(float(row["Low"]), 2) if not pd.isna(row["Low"]) else None,
                "close": round(float(row["Close"]), 2) if not pd.isna(row["Close"]) else None,
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
                "sma_20": round(float(row["SMA_20"]), 2) if not pd.isna(row["SMA_20"]) else None,
                "sma_50": round(float(row["SMA_50"]), 2) if not pd.isna(row["SMA_50"]) else None,
                "signal": int(row["Signal"]),
                "crossover": str(row["Crossover"]) if row["Crossover"] is not None else None,
            }
        )

    # --------------------------------------------------------------------------
    # Quantitative Forecasting Engine (Next Days & Weeks)
    # Uses Drift-adjusted Geometric Brownian Motion & Momentum Slope
    # --------------------------------------------------------------------------
    close_series = df["Close"].dropna()
    log_returns = np.log(close_series / close_series.shift(1)).dropna()

    daily_vol = float(log_returns.std()) if len(log_returns) > 1 else 0.015
    # Ensure a non-zero floor for volatility
    daily_vol = max(daily_vol, 0.005)
    ann_vol = float(daily_vol * np.sqrt(252))

    # Short-term momentum slope using linear regression on log prices over the last 20 bars
    window = min(20, len(close_series))
    recent_log_prices = np.log(close_series.iloc[-window:].values)
    x_axis = np.arange(window)
    if window >= 3:
        slope, _ = np.polyfit(x_axis, recent_log_prices, 1)
    else:
        slope = 0.0

    mean_return = float(log_returns.mean()) if len(log_returns) > 0 else 0.0
    # Blend long-term drift and recent momentum
    drift = 0.4 * mean_return + 0.6 * float(slope)

    last_price = float(close_series.iloc[-1])
    last_date = df.index[-1]
    first_price = float(close_series.iloc[0])
    price_change = round(last_price - first_price, 2)
    price_change_pct = round(((last_price - first_price) / first_price) * 100, 2)

    # Project forward 30 trading days (approx 6 calendar weeks)
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=30)

    forecast_series = []
    # Add connecting anchor point from the latest historical close
    forecast_series.append(
        {
            "time": last_date.strftime("%Y-%m-%d"),
            "predicted_close": round(last_price, 2),
            "upper_bound": round(last_price, 2),
            "lower_bound": round(last_price, 2),
        }
    )

    for i, dt in enumerate(future_dates, 1):
        # Dampen drift over time as uncertainty increases
        dampened_drift = drift * np.exp(-0.02 * i)
        pred_price = last_price * np.exp((dampened_drift - 0.5 * (daily_vol**2)) * i)
        # 90% confidence interval (z ~ 1.645)
        margin = 1.645 * daily_vol * np.sqrt(i)
        upper_bound = pred_price * np.exp(margin)
        lower_bound = pred_price * np.exp(-margin)

        forecast_series.append(
            {
                "time": dt.strftime("%Y-%m-%d"),
                "predicted_close": round(float(pred_price), 2),
                "upper_bound": round(float(upper_bound), 2),
                "lower_bound": round(float(lower_bound), 2),
            }
        )

    # Extract specific target milestones:
    # 7-day target (approx 5 trading days / 1 calendar week)
    target_7d = forecast_series[min(5, len(forecast_series) - 1)]
    # 14-day target (approx 10 trading days / 2 calendar weeks)
    target_14d = forecast_series[min(10, len(forecast_series) - 1)]
    # 30-day target (approx 21 trading days / 1 month)
    target_30d = forecast_series[min(21, len(forecast_series) - 1)]

    def calc_horizon(target: dict) -> dict:
        target_p = target["predicted_close"]
        delta_pct = round(((target_p - last_price) / last_price) * 100, 2)
        if delta_pct > 1.0:
            direction = "Bullish"
        elif delta_pct < -1.0:
            direction = "Bearish"
        else:
            direction = "Neutral"
        return {
            "date": target["time"],
            "target_price": target_p,
            "upper_bound": target["upper_bound"],
            "lower_bound": target["lower_bound"],
            "expected_change_pct": delta_pct,
            "direction": direction,
        }

    latest_signal = int(df["Signal"].iloc[-1])
    if latest_signal == 1:
        signal_label = "BUY"
    elif latest_signal == -1:
        signal_label = "SELL"
    else:
        signal_label = "HOLD"

    last_sma_20 = round(float(df["SMA_20"].iloc[-1]), 2) if not pd.isna(df["SMA_20"].iloc[-1]) else None
    last_sma_50 = round(float(df["SMA_50"].iloc[-1]), 2) if not pd.isna(df["SMA_50"].iloc[-1]) else None

    # Determine general trend
    if last_sma_20 and last_sma_50:
        if last_sma_20 > last_sma_50 and last_price > last_sma_20:
            trend = "STRONG BULLISH"
        elif last_sma_20 > last_sma_50:
            trend = "BULLISH"
        elif last_sma_20 < last_sma_50 and last_price < last_sma_20:
            trend = "STRONG BEARISH"
        else:
            trend = "BEARISH"
    else:
        trend = "NEUTRAL"

    return {
        "ticker": ticker_clean,
        "period": period,
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
            "forecast_7d": calc_horizon(target_7d),
            "forecast_14d": calc_horizon(target_14d),
            "forecast_30d": calc_horizon(target_30d),
        },
        "disclaimer": "Quantitative forecasts are statistical simulations based on historical drift and volatility and do not constitute financial advice.",
    }


@app.get("/signal/{ticker}/{period}")
def get_signal(ticker: str = "AAPL", period: str = "6mo", legacy: bool = False):
    """
    API endpoint to retrieve technical signals and forward predictive projections.
    Set `legacy=true` to receive the previous flat array structure.
    """
    result = fetch_and_calculate_signals(ticker=ticker, period=period)
    if legacy:
        # Backward compatibility format
        return [
            {
                "Date": h["time"],
                "Close": h["close"],
                "SMA_20": h["sma_20"],
                "SMA_50": h["sma_50"],
                "Signal": h["signal"],
            }
            for h in result["historical"]
        ]
    return result


@app.get("/forecast/{ticker}")
def get_forecast(ticker: str = "AAPL", period: str = "6mo"):
    """
    Dedicated endpoint returning only future predictive projections for the given ticker.
    """
    data = fetch_and_calculate_signals(ticker=ticker, period=period)
    return {
        "ticker": data["ticker"],
        "current_price": data["current_price"],
        "latest_date": data["latest_date"],
        "forecast": data["forecast"],
        "metrics": data["metrics"],
        "disclaimer": data["disclaimer"],
    }


if __name__ == "__main__":
    test_result = fetch_and_calculate_signals("AAPL", "6mo")
    print(f"Ticker: {test_result['ticker']} | Price: ${test_result['current_price']}")
    print(f"Metrics: {test_result['metrics']}")
    print(f"Forecast 7d: {test_result['metrics']['forecast_7d']}")
    print(f"Historical points: {len(test_result['historical'])} | Forecast points: {len(test_result['forecast'])}")