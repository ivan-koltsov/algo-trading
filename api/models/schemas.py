"""
Pydantic schemas for request validation and response serialization.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class HistoricalBar(BaseModel):
    time: str = Field(..., description="Date formatted as YYYY-MM-DD")
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: int = 0
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    signal: int = Field(0, description="1 for Buy, -1 for Sell, 0 for Hold")
    crossover: Optional[str] = Field(None, description="'BUY' or 'SELL' on crossover days")


class ForecastPoint(BaseModel):
    time: str = Field(..., description="Date formatted as YYYY-MM-DD")
    predicted_close: float
    upper_bound: float
    lower_bound: float


class HorizonProjection(BaseModel):
    date: str
    target_price: float
    upper_bound: float
    lower_bound: float
    expected_change_pct: float
    direction: str = Field(..., description="'Bullish', 'Bearish', or 'Neutral'")


class ForecastMetrics(BaseModel):
    latest_signal: int
    latest_signal_label: str
    trend: str
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    volatility_annualized_pct: float
    forecast_7d: HorizonProjection
    forecast_14d: HorizonProjection
    forecast_30d: HorizonProjection


class AnalystConsensus(BaseModel):
    target_mean: Optional[float] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    consensus_rating: Optional[str] = None
    buy_count: Optional[int] = None
    hold_count: Optional[int] = None
    sell_count: Optional[int] = None
    analyst_opinions_count: Optional[int] = None


class ValuationDCF(BaseModel):
    intrinsic_value: Optional[float] = None
    upside_pct: Optional[float] = None
    status: Optional[str] = None


class AIPrediction(BaseModel):
    score: Optional[int] = None
    outperformance_probability_pct: Optional[float] = None
    conviction: Optional[str] = None


class ProviderInsights(BaseModel):
    analyst_consensus: Optional[AnalystConsensus] = None
    valuation_dcf: Optional[ValuationDCF] = None
    ai_prediction: Optional[AIPrediction] = None


class SignalAnalysisResponse(BaseModel):
    ticker: str
    period: str
    source: str
    source_name: str
    source_url: str
    current_price: float
    price_change: float
    price_change_pct: float
    latest_date: str
    historical: List[HistoricalBar]
    forecast: List[ForecastPoint]
    metrics: ForecastMetrics
    provider_insights: Optional[ProviderInsights] = None
    disclaimer: str


class ForecastResponse(BaseModel):
    ticker: str
    source: str
    source_name: str
    source_url: str
    current_price: float
    latest_date: str
    forecast: List[ForecastPoint]
    metrics: ForecastMetrics
    provider_insights: Optional[ProviderInsights] = None
    disclaimer: str


class LegacyBar(BaseModel):
    Date: str
    Close: Optional[float] = None
    SMA_20: Optional[float] = None
    SMA_50: Optional[float] = None
    Signal: int
