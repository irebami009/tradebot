import pandas as pd
from typing import Dict, Any, List, Optional
import os
import uuid
from datetime import datetime, timezone
from app.adapters.base import ExchangeInterface
from app.config import settings

class PaperExchangeAdapter(ExchangeInterface):
    """
    Paper Trading exchange adapter simulating market order execution, fee deduction, slippage, and balance tracking.
    """
    def __init__(self, data_file: str = settings.DATA_FILE, starting_balance: float = settings.STARTING_BALANCE):
        self.data_file = data_file
        self.balance_total = starting_balance
        self.balance_free = starting_balance
        self.balance_used = 0.0
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.open_positions: List[Dict[str, Any]] = []

    def get_balance(self) -> Dict[str, float]:
        return {
            "free": round(self.balance_free, 2),
            "used": round(self.balance_used, 2),
            "total": round(self.balance_total, 2)
        }

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        if symbol:
            return [p for p in self.open_positions if p["symbol"] == symbol]
        return self.open_positions

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        df = self.get_ohlcv(symbol, limit=1)
        if len(df) == 0:
            return {"bid": 50000.0, "ask": 50000.0, "last": 50000.0}
        last_price = float(df.iloc[-1]["close"])
        return {
            "bid": round(last_price * 0.9999, 2),
            "ask": round(last_price * 1.0001, 2),
            "last": round(last_price, 2)
        }

    def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file missing: {self.data_file}")
        df = pd.read_csv(self.data_file)
        return df.tail(limit).reset_index(drop=True)

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
        ticker = self.get_ticker(symbol)
        base_price = price or ticker["last"]
        
        # Apply slippage (0.05% default)
        slippage = base_price * settings.SLIPPAGE_PERCENT
        execution_price = base_price + slippage if side == "BUY" else base_price - slippage

        gross_cost = amount * execution_price
        fee = gross_cost * settings.TRADING_FEE_PERCENT
        total_cost = gross_cost + fee

        if side == "BUY" and self.balance_free < total_cost:
            raise ValueError(f"Insufficient funds: available ${self.balance_free:.2f}, required ${total_cost:.2f}")

        order_id = f"paper_ord_{uuid.uuid4().hex[:8]}"
        order = {
            "id": order_id,
            "symbol": symbol,
            "type": type,
            "side": side,
            "amount": amount,
            "price": execution_price,
            "status": "FILLED",
            "filled": amount,
            "remaining": 0.0,
            "fee": fee,
            "slippage": slippage,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.orders[order_id] = order

        if side == "BUY":
            self.balance_free -= total_cost
            self.balance_used += gross_cost
            self.open_positions.append({
                "id": order_id,
                "symbol": symbol,
                "side": side,
                "entry_price": execution_price,
                "amount": amount,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "fee": fee
            })
        elif side == "SELL":
            # Close existing position
            pos = next((p for p in self.open_positions if p["symbol"] == symbol), None)
            if pos:
                self.open_positions.remove(pos)
                self.balance_used -= (pos["amount"] * pos["entry_price"])
            
            gross_return = amount * execution_price
            net_return = gross_return - fee
            self.balance_free += net_return
            self.balance_total = self.balance_free + self.balance_used

        return order

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id]["status"] = "CANCELLED"
            return True
        return False

    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        return self.orders.get(order_id, {"status": "NOT_FOUND"})

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        return [o for o in self.orders.values() if o["status"] == "OPEN"]
