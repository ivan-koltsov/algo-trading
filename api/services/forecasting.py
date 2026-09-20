"""
Quantitative forecasting engine.
Uses geometric Brownian motion with log-price momentum drift and confidence intervals.
"""
from typing import List, Tuple
import numpy as np
import pandas as pd


def calculate_drift_and_volatility(close_series: pd.Series) -> Tuple[float, float, float]:
    """
    Computes annualized volatility, daily volatility, and blended momentum drift.
    """
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

    return drift, daily_vol, ann_vol


def generate_gbm_forecast(
    last_price: float,
    last_date: pd.Timestamp,
    drift: float,
    daily_vol: float,
    days: int = 30,
) -> List[dict]:
    """
    Simulates projected price path with 90% confidence corridor over next `days` business days.
    """
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=days)

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

    return forecast_series


def calculate_horizon_projection(target: dict, last_price: float) -> dict:
    """
    Computes expected price change and direction for a target forecast point.
    """
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
