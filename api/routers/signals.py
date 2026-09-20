"""
Signals and technical analysis router.
"""
from typing import List, Union
from fastapi import APIRouter, Query

try:
    from models.schemas import SignalAnalysisResponse, LegacyBar
    from services.market_service import market_service
except ImportError:
    from api.models.schemas import SignalAnalysisResponse, LegacyBar
    from api.services.market_service import market_service

router = APIRouter(tags=["Signals"])


@router.get(
    "/signal/{ticker}/{period}",
    summary="Get Technical Signals & Predictive Projections",
    response_model=Union[SignalAnalysisResponse, List[LegacyBar]],
)
def get_signal(
    ticker: str = "AAPL",
    period: str = "6mo",
    source: str = Query("yahoo", description="Data provider source: 'yahoo' or 'google'"),
    legacy: bool = False,
):
    """
    Retrieves historical OHLCV data, computes SMA 20/50 technical indicators,
    detects crossover buy/sell signals, and provides forward multi-week forecasting.
    """
    result = market_service.fetch_and_calculate_signals(ticker=ticker, period=period, source=source)
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
