"""
Dedicated forecasting router.
"""
from fastapi import APIRouter, Query

try:
    from models.schemas import ForecastResponse
    from services.market_service import market_service
except ImportError:
    from api.models.schemas import ForecastResponse
    from api.services.market_service import market_service

router = APIRouter(tags=["Forecast"])


@router.get(
    "/forecast/{ticker}",
    summary="Get Multi-Week Horizon Forecast",
    response_model=ForecastResponse,
)
def get_forecast(
    ticker: str = "AAPL",
    period: str = "6mo",
    source: str = Query("yahoo", description="Data provider source: 'yahoo' or 'google'"),
):
    """
    Dedicated endpoint returning future predictive projections and horizon targets for the given ticker.
    """
    data = market_service.fetch_and_calculate_signals(ticker=ticker, period=period, source=source)
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
