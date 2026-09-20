"""
Technical analysis service for computing moving averages and crossover signals.
"""
from typing import List, Optional, Tuple
import pandas as pd


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes SMA_20 and SMA_50, generates bullish (1), bearish (-1), or neutral (0)
    signals, and pinpoints golden/death crossover events.
    """
    df = df.copy()

    # Rolling simple moving averages
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()

    # Base signal
    df["Signal"] = 0
    df.loc[df["SMA_20"] > df["SMA_50"], "Signal"] = 1
    df.loc[df["SMA_20"] < df["SMA_50"], "Signal"] = -1

    # Crossover detection
    df["Prev_Signal"] = df["Signal"].shift(1).fillna(0)
    df["Crossover"] = None
    df.loc[(df["Signal"] == 1) & (df["Prev_Signal"] != 1), "Crossover"] = "BUY"
    df.loc[(df["Signal"] == -1) & (df["Prev_Signal"] != -1), "Crossover"] = "SELL"

    return df


def determine_market_trend(
    sma_20: Optional[float],
    sma_50: Optional[float],
    last_price: float,
) -> str:
    """
    Determines verbal market trend from moving averages and current price.
    """
    if not sma_20 or not sma_50:
        return "NEUTRAL"

    if sma_20 > sma_50 and last_price > sma_20:
        return "STRONG BULLISH"
    elif sma_20 > sma_50:
        return "BULLISH"
    elif sma_20 < sma_50 and last_price < sma_20:
        return "STRONG BEARISH"
    elif sma_20 < sma_50:
        return "BEARISH"
    return "NEUTRAL"


def get_latest_signal_label(signal: int) -> str:
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    return "HOLD"


def build_historical_bars(df: pd.DataFrame) -> List[dict]:
    """
    Formats DataFrame rows into a clean list of historical bar dicts for charting.
    """
    bars = []
    for idx, row in df.iterrows():
        time_str = idx.strftime("%Y-%m-%d")
        bars.append(
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
    return bars
