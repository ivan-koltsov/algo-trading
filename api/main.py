import json
import re
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import yfinance as yf

# Try importing curl_cffi for Google Finance TLS fingerprint impersonation
try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    import requests as cffi_requests  # type: ignore

app = FastAPI(
    title="Algo Trading API",
    description="Algorithmic trading technical analysis, signal generation, and quantitative forecasting with Google & Yahoo Finance providers",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_google_finance_quote(symbol: str) -> Optional[dict]:
    """
    Fetches real-time market quote from Google Finance using curl_cffi browser impersonation.
    """
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
            # Impersonate modern Chrome browser
            r = cffi_requests.get(url, impersonate="chrome120", timeout=5)
            if r.status_code == 200:
                # Embedded data array pattern in Google Finance page
                pattern = (
                    r'\[\"'
                    + re.escape(sym)
                    + r'\"\,\"'
                    + exc
                    + r'\"\]\,[^,]+,\d+,\"([A-Z]{3})\"\,\[([0-9.]+),([+-]?[0-9.]+),([+-]?[0-9.]+)'
                )
                m = re.search(pattern, r.text)
                if m:
                    return {
                        "symbol": symbol_clean,
                        "exchange": exc,
                        "currency": m.group(1),
                        "price": float(m.group(2)),
                        "change": float(m.group(3)),
                        "change_pct": float(m.group(4)),
                        "url": url,
                        "source": "google",
                        "source_name": "Google Finance",
                    }

                # Secondary fallback: data-last-price attribute
                m2 = re.search(r'data-last-price=\"([0-9.]+)\"', r.text)
                if m2:
                    return {
                        "symbol": symbol_clean,
                        "exchange": exc,
                        "price": float(m2.group(1)),
                        "change": 0.0,
                        "change_pct": 0.0,
                        "url": url,
                        "source": "google",
                        "source_name": "Google Finance",
                    }
        except Exception:
            continue

    return None


def fetch_and_calculate_signals(ticker: str = "AAPL", period: str = "6mo", source: str = "yahoo") -> dict:
    """
    Fetches market data from either Yahoo Finance or Google Finance,
    calculates SMA technical indicators, detects crossover buy/sell signals,
    and computes quantitative forecast predictions for upcoming days and weeks (7d, 14d, 30d).
    """
    ticker_clean = ticker.upper().strip()
    source_clean = source.lower().strip() if source else "yahoo"
    if source_clean not in ["yahoo", "google"]:
        source_clean = "yahoo"

    # Fetch baseline historical data from yfinance
    try:
        yf_ticker = yf.Ticker(ticker_clean)
        df = yf_ticker.history(period=period)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch market data: {str(e)}")

    if df.empty or len(df) < 5:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for ticker '{ticker_clean}' over period '{period}'. Please verify the symbol.",
        )

    df = df.copy()

    # If Google Finance is selected, fetch real-time quote from Google Finance
    google_quote = None
    if source_clean == "google":
        google_quote = get_google_finance_quote(ticker_clean)

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

    # Update latest close if Google Finance live quote was retrieved
    close_series = df["Close"].dropna()
    last_price = float(close_series.iloc[-1])
    first_price = float(close_series.iloc[0])

    if google_quote and google_quote.get("price"):
        last_price = float(google_quote["price"])
        if len(historical) > 0:
            historical[-1]["close"] = round(last_price, 2)
            if historical[-1]["high"] and last_price > historical[-1]["high"]:
                historical[-1]["high"] = round(last_price, 2)
            if historical[-1]["low"] and last_price < historical[-1]["low"]:
                historical[-1]["low"] = round(last_price, 2)

    price_change = round(last_price - first_price, 2)
    price_change_pct = round(((last_price - first_price) / first_price) * 100, 2)
    last_date = df.index[-1]

    # --------------------------------------------------------------------------
    # Quantitative Forecasting Engine (Next Days & Weeks)
    # --------------------------------------------------------------------------
    log_returns = np.log(close_series / close_series.shift(1)).dropna()

    daily_vol = float(log_returns.std()) if len(log_returns) > 1 else 0.015
    daily_vol = max(daily_vol, 0.005)
    ann_vol = float(daily_vol * np.sqrt(252))

    window = min(20, len(close_series))
    recent_log_prices = np.log(close_series.iloc[-window:].values)
    x_axis = np.arange(window)
    if window >= 3:
        slope, _ = np.polyfit(x_axis, recent_log_prices, 1)
    else:
        slope = 0.0

    mean_return = float(log_returns.mean()) if len(log_returns) > 0 else 0.0
    drift = 0.4 * mean_return + 0.6 * float(slope)

    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=30)

    forecast_series = [
        {
            "time": last_date.strftime("%Y-%m-%d"),
            "predicted_close": round(last_price, 2),
            "upper_bound": round(last_price, 2),
            "lower_bound": round(last_price, 2),
        }
    ]

    for i, dt in enumerate(future_dates, 1):
        dampened_drift = drift * np.exp(-0.02 * i)
        pred_price = last_price * np.exp((dampened_drift - 0.5 * (daily_vol**2)) * i)
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

    target_7d = forecast_series[min(5, len(forecast_series) - 1)]
    target_14d = forecast_series[min(10, len(forecast_series) - 1)]
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

    # Provider metadata
    if source_clean == "google":
        source_name = "Google Finance"
        source_url = google_quote["url"] if google_quote else f"https://www.google.com/finance/quote/{ticker_clean}:NASDAQ"
    else:
        source_name = "Yahoo Finance"
        source_url = f"https://finance.yahoo.com/quote/{ticker_clean}"

    return {
        "ticker": ticker_clean,
        "period": period,
        "source": source_clean,
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
            "forecast_7d": calc_horizon(target_7d),
            "forecast_14d": calc_horizon(target_14d),
            "forecast_30d": calc_horizon(target_30d),
        },
        "disclaimer": "Quantitative forecasts are statistical simulations based on historical drift and volatility and do not constitute financial advice.",
    }


@app.get("/signal/{ticker}/{period}")
def get_signal(
    ticker: str = "AAPL",
    period: str = "6mo",
    source: str = Query("yahoo", description="Data provider source: 'yahoo' or 'google'"),
    legacy: bool = False,
):
    """
    API endpoint to retrieve technical signals and forward predictive projections.
    Supports source='yahoo' or source='google'.
    """
    result = fetch_and_calculate_signals(ticker=ticker, period=period, source=source)
    if legacy:
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
def get_forecast(
    ticker: str = "AAPL",
    period: str = "6mo",
    source: str = Query("yahoo", description="Data provider source: 'yahoo' or 'google'"),
):
    """
    Dedicated endpoint returning only future predictive projections for the given ticker.
    """
    data = fetch_and_calculate_signals(ticker=ticker, period=period, source=source)
    return {
        "ticker": data["ticker"],
        "source": data["source"],
        "source_name": data["source_name"],
        "source_url": data["source_url"],
        "current_price": data["current_price"],
        "latest_date": data["latest_date"],
        "forecast": data["forecast"],
        "metrics": data["metrics"],
        "disclaimer": data["disclaimer"],
    }


if __name__ == "__main__":
    y_res = fetch_and_calculate_signals("AAPL", "6mo", source="yahoo")
    g_res = fetch_and_calculate_signals("AAPL", "6mo", source="google")
    print(f"Yahoo: {y_res['source_name']} -> Price: ${y_res['current_price']} | URL: {y_res['source_url']}")
    print(f"Google: {g_res['source_name']} -> Price: ${g_res['current_price']} | URL: {g_res['source_url']}")