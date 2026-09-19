import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import yfinance as yf

app = FastAPI(
  title = 'Algo Trading API',
  version = '0.0.1'
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

def fetch_and_calculate_signals(ticker="AAPL", period="6mo"):
    """
    Fetches historical OHLCV data for a ticker and calculates simple moving average signals.
    """
    try:
      ticker = yf.Ticker(ticker)
      df = ticker.history(period=period)

      # Calculate indicators using Pandas rolling windows
      df['SMA_20'] = df['Close'].rolling(window=20).mean()
      df['SMA_50'] = df['Close'].rolling(window=50).mean()

      # Generate signals: 1 for bullish (Buy), -1 for bearish (Sell)
      df['Signal'] = 0
      df.loc[df['SMA_20'] > df['SMA_50'], 'Signal'] = 1
      df.loc[df['SMA_20'] < df['SMA_50'], 'Signal'] = -1

      return df[['Close', 'SMA_20', 'SMA_50', 'Signal']]
    except Exception as e:
        raise e

@app.get("/signal/{ticker}/{period}")
def get_signal(ticker: str = "AAPL", period: str = "6mo"):
    """
    API endpoint to retrieve trading signals for a given ticker and period.
    """
    df = fetch_and_calculate_signals(ticker=ticker, period=period)
    return json.loads(df.reset_index().to_json(orient="records", date_format="iso"))

# Example test execution
if __name__ == "__main__":
    df_signals = fetch_and_calculate_signals("AAPL", "6mo")
    print(df_signals.tail(10))