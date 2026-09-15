from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List, Optional

class ExchangeInterface(ABC):
    """
    Standardized abstract exchange interface decoupled from specific exchange/broker APIs.
    Allows seamlessly swapping Paper Exchange, CCXT (Binance, Bybit, Kraken), or MetaTrader 5.
    """

    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """
        Returns balance dictionary: {'free': float, 'used': float, 'total': float}
        """
        pass

    @abstractmethod
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns list of open positions.
        """
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, float]:
        """
        Returns ticker dictionary: {'bid': float, 'ask': float, 'last': float}
        """
        pass

    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        """
        Returns DataFrame with columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        pass

    @abstractmethod
    def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Creates an order and returns normalized order dictionary.
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancels an open order.
        """
        pass

    @abstractmethod
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Retrieves order status.
        """
        pass

    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves list of open orders.
        """
        pass
