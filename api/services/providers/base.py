"""
Abstract base class and data structures for market data providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import pandas as pd


@dataclass
class MarketQuote:
    symbol: str
    exchange: Optional[str] = None
    currency: Optional[str] = None
    price: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0
    url: str = ""
    source: str = ""
    source_name: str = ""

    # Optional analyst consensus metadata (TipRanks & Wall Street)
    analyst_target_mean: Optional[float] = None
    analyst_target_high: Optional[float] = None
    analyst_target_low: Optional[float] = None
    buy_count: Optional[int] = None
    hold_count: Optional[int] = None
    sell_count: Optional[int] = None
    consensus_rating: Optional[str] = None
    analyst_opinions_count: Optional[int] = None

    # Optional valuation metadata (FMP DCF)
    dcf_intrinsic_value: Optional[float] = None
    dcf_upside_pct: Optional[float] = None
    valuation_status: Optional[str] = None

    # Optional AI prediction metadata (Danelfin)
    ai_score: Optional[int] = None  # 1 to 10
    ai_probability_pct: Optional[float] = None  # e.g. 56.0
    ai_conviction: Optional[str] = None  # Strong Buy / Buy / Neutral
    ai_technical_score: Optional[int] = None
    ai_fundamental_score: Optional[int] = None
    ai_sentiment_score: Optional[int] = None

    extra: Dict[str, Any] = field(default_factory=dict)


class BaseDataProvider(ABC):
    """
    Abstract interface for financial market data providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def identifier(self) -> str:
        """Internal provider slug ('yahoo', 'google', 'tipranks', etc.)."""
        pass

    @abstractmethod
    def get_realtime_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch the most recent real-time quote and metadata for a symbol."""
        pass

    @abstractmethod
    def get_historical_ohlcv(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Fetch historical OHLCV data as a pandas DataFrame."""
        pass
