import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.adapters.base import ExchangeInterface

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


class MT5ExchangeAdapter(ExchangeInterface):
    """
    MetaTrader 5 Production Integration Adapter.
    Communicates with MT5 terminal running on Windows for live Forex, Crypto, Indices & Commodities trading.
    """
    def __init__(
        self,
        symbol: str = "EURUSD",
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        path: Optional[str] = None
    ):
        self.symbol = symbol
        self.login = login
        self.password = password
        self.server = server
        self.path = path
        self.connected = False
        self._init_mt5()

    def _init_mt5(self) -> bool:
        if not MT5_AVAILABLE:
            print("[MT5 ADAPTER WARNING] MetaTrader5 Python package not available.")
            return False

        init_kwargs = {}
        if self.path:
            init_kwargs["path"] = self.path
        if self.login and self.password and self.server:
            init_kwargs["login"] = int(self.login)
            init_kwargs["password"] = str(self.password)
            init_kwargs["server"] = str(self.server)

        if not mt5.initialize(**init_kwargs):
            err = mt5.last_error()
            print(f"[MT5 ADAPTER ERROR] MT5 initialize failed: {err}")
            self.connected = False
            return False

        if self.login and self.password and self.server:
            authorized = mt5.login(login=int(self.login), password=str(self.password), server=str(self.server))
            if not authorized:
                print(f"[MT5 ADAPTER ERROR] MT5 login failed for account {self.login} on server {self.server}: {mt5.last_error()}")
                self.connected = False
                return False

        self.connected = True
        acc_info = mt5.account_info()
        if acc_info:
            print(f"[MT5 ADAPTER SUCCESS] Connected to MT5 Account #{acc_info.login} ({acc_info.company}) — Balance: ${acc_info.balance}")
        return True

    def get_balance(self) -> Dict[str, float]:
        if not self.connected and not self._init_mt5():
            return {"free": 10000.0, "used": 0.0, "total": 10000.0, "equity": 10000.0}

        acc = mt5.account_info()
        if acc is None:
            return {"free": 0.0, "used": 0.0, "total": 0.0, "equity": 0.0}

        return {
            "free": float(acc.margin_free),
            "used": float(acc.margin),
            "total": float(acc.balance),
            "equity": float(acc.equity)
        }

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.connected and not self._init_mt5():
            return []

        target_symbol = symbol or self.symbol
        positions = mt5.positions_get(symbol=target_symbol) if target_symbol else mt5.positions_get()
        if positions is None:
            return []

        result = []
        for pos in positions:
            result.append({
                "id": str(pos.ticket),
                "symbol": pos.symbol,
                "side": "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
                "amount": float(pos.volume),
                "entry_price": float(pos.price_open),
                "current_price": float(pos.price_current),
                "stop_loss": float(pos.sl),
                "take_profit": float(pos.tp),
                "unrealized_pnl": float(pos.profit),
                "magic": pos.magic,
                "comment": pos.comment
            })
        return result

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        if not self.connected and not self._init_mt5():
            return {"bid": 0.0, "ask": 0.0, "last": 0.0}

        mt5.symbol_select(symbol, True)
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return {"bid": 0.0, "ask": 0.0, "last": 0.0}

        return {
            "bid": float(tick.bid),
            "ask": float(tick.ask),
            "last": float(tick.last or tick.bid)
        }

    def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        if not self.connected and not self._init_mt5():
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

        tf_map = {
            "1m": mt5.TIMEFRAME_M1,
            "5m": mt5.TIMEFRAME_M5,
            "15m": mt5.TIMEFRAME_M15,
            "1h": mt5.TIMEFRAME_H1,
            "4h": mt5.TIMEFRAME_H4,
            "1d": mt5.TIMEFRAME_D1,
        }
        mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)

        mt5.symbol_select(symbol, True)
        rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, limit)
        if rates is None or len(rates) == 0:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

        df = pd.DataFrame(rates)
        df["timestamp"] = pd.to_datetime(df["time"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
        df["volume"] = df["tick_volume"].astype(float)
        return df[["timestamp", "open", "high", "low", "close", "volume"]]

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
        if not self.connected and not self._init_mt5():
            raise RuntimeError("MetaTrader 5 terminal connection failed. Please ensure MT5 terminal is open.")

        mt5.symbol_select(symbol, True)
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise ValueError(f"Symbol {symbol} not found on MT5 broker terminal.")

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"Failed to retrieve current price tick for {symbol}")

        order_type = mt5.ORDER_TYPE_BUY if side.upper() == "BUY" else mt5.ORDER_TYPE_SELL
        exec_price = tick.ask if side.upper() == "BUY" else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(amount),
            "type": order_type,
            "price": float(exec_price),
            "sl": float(stop_loss) if stop_loss else 0.0,
            "tp": float(take_profit) if take_profit else 0.0,
            "deviation": 20,
            "magic": 234000,
            "comment": "Apex Automated Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            err_msg = result.comment if result else "Unknown MT5 order execution error"
            retcode = result.retcode if result else "NONE"
            raise RuntimeError(f"MT5 Order Execution Failed (Retcode: {retcode}): {err_msg}")

        return {
            "id": str(result.order),
            "symbol": symbol,
            "side": side.upper(),
            "amount": float(result.volume),
            "price": float(result.price),
            "status": "FILLED",
            "timestamp": datetime.utcnow().isoformat(),
            "retcode": result.retcode
        }

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        if not self.connected and not self._init_mt5():
            return False

        # Close position by ticket
        ticket = int(order_id)
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False

        pos = positions[0]
        tick = mt5.symbol_info_tick(pos.symbol)
        opposite_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": pos.ticket,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": opposite_type,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Apex Bot Close Position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        res = mt5.order_send(request)
        return res is not None and res.retcode == mt5.TRADE_RETCODE_DONE

    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        if not self.connected and not self._init_mt5():
            return {"status": "NOT_FOUND"}

        orders = mt5.history_orders_get(ticket=int(order_id))
        if orders and len(orders) > 0:
            o = orders[0]
            return {
                "id": str(o.ticket),
                "symbol": o.symbol,
                "amount": float(o.volume_initial),
                "status": "FILLED" if o.state == mt5.ORDER_STATE_FILLED else "OPEN"
            }
        return {"status": "NOT_FOUND"}

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.connected and not self._init_mt5():
            return []
        orders = mt5.orders_get(symbol=symbol) if symbol else mt5.orders_get()
        if not orders:
            return []
        return [{"id": str(o.ticket), "symbol": o.symbol, "amount": o.volume_initial} for o in orders]
