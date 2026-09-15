from abc import ABC, abstractmethod
import pandas as pd
import os
from typing import Optional

class BaseMarketDataProvider(ABC):
    """
    Abstract interface for market data sources (CSV files, Binance API, Alpaca, CCXT, etc.).
    Enables swapping live exchange APIs without rewriting strategies or trading logic.
    """
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch OHLCV candlestick data.
        Returns DataFrame with columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        pass

class CSVMarketDataProvider(BaseMarketDataProvider):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def fetch_ohlcv(self, symbol: str = "BTC/USD", limit: int = 1000) -> pd.DataFrame:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Market data file not found: {self.file_path}")

        df = pd.read_csv(self.file_path)
        required_cols = {"timestamp", "open", "high", "low", "close", "volume"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV file must contain columns: {required_cols}")

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        return df.tail(limit).reset_index(drop=True)
