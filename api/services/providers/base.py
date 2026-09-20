"""
Abstract base class and data structures for market data providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
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
        """Internal provider slug ('yahoo', 'google', etc.)."""
        pass

    @abstractmethod
    def get_realtime_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch the most recent real-time quote for a symbol."""
        pass

    @abstractmethod
    def get_historical_ohlcv(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Fetch historical OHLCV data as a pandas DataFrame."""
        pass
