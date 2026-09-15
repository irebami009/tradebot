import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.engine.decision_engine import DecisionEngine
from app.engine.trade_validator import TradeValidator
from app.models.schemas import PerformanceMetrics, TradeSchema, EquityPoint
from app.config import settings

def utc_now():
    return datetime.now(timezone.utc)

class BacktestEngine:
    def __init__(
        self,
        starting_balance: float = settings.STARTING_BALANCE,
        risk_per_trade: float = settings.RISK_PER_TRADE,
        stop_loss_percent: float = settings.DEFAULT_STOP_LOSS_PCT,
        take_profit_percent: float = settings.DEFAULT_TAKE_PROFIT_PCT,
        min_confidence: float = settings.MIN_CONFIDENCE_THRESHOLD,
        trading_fee_percent: float = settings.TRADING_FEE_PERCENT
    ):
        self.starting_balance = starting_balance
        self.fee_percent = trading_fee_percent
        self.decision_engine = DecisionEngine(min_confidence=min_confidence)
        self.trade_validator = TradeValidator()

    def run(self, df: pd.DataFrame, symbol: str = "BTC/USD") -> PerformanceMetrics:
        if len(df) < 50:
            return PerformanceMetrics(
                starting_balance=self.starting_balance,
                ending_balance=self.starting_balance,
                total_return_percent=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate_percent=0.0,
                total_profit=0.0,
                total_loss=0.0,
                max_drawdown_percent=0.0,
                avg_profit_per_trade=0.0,
                avg_loss_per_trade=0.0,
                profit_factor=0.0,
                sharpe_ratio=0.0,
                equity_curve=[],
                trades=[]
            )

        balance = self.starting_balance
        peak_balance = balance
        max_drawdown = 0.0

        active_position = None
        closed_trades: List[TradeSchema] = []
        equity_curve: List[EquityPoint] = []
        daily_returns: List[float] = []

        trade_counter = 1

        for i in range(len(df)):
            current_slice = df.iloc[:i+1]
            candle = df.iloc[i]
            ts = str(candle["timestamp"])
            close_price = float(candle["close"])
            high_price = float(candle["high"])
            low_price = float(candle["low"])

            # 1. Check open position for Stop Loss / Take Profit
            if active_position is not None:
                sl_hit = low_price <= active_position["stop_loss"]
                tp_hit = high_price >= active_position["take_profit"]

                if sl_hit or tp_hit:
                    exit_price = active_position["stop_loss"] if sl_hit else active_position["take_profit"]
                    gross_return = active_position["quantity"] * exit_price
                    close_fee = gross_return * self.fee_percent
                    net_return = gross_return - close_fee

                    cost_basis = active_position["quantity"] * active_position["entry_price"]
                    total_fees = active_position["fees"] + close_fee
                    pnl = (gross_return - cost_basis) - total_fees
                    pnl_pct = (pnl / cost_basis) * 100.0 if cost_basis > 0 else 0.0

                    balance += net_return

                    closed_trade = TradeSchema(
                        id=trade_counter,
                        symbol=symbol,
                        side="BUY",
                        entry_price=round(active_position["entry_price"], 2),
                        exit_price=round(exit_price, 2),
                        quantity=round(active_position["quantity"], 6),
                        stop_loss=round(active_position["stop_loss"], 2),
                        take_profit=round(active_position["take_profit"], 2),
                        trailing_stop=round(active_position["stop_loss"], 2),
                        profit_loss=round(pnl, 2),
                        profit_loss_percentage=round(pnl_pct, 2),
                        fees=round(total_fees, 4),
                        slippage=round(active_position["slippage"], 4),
                        status="CLOSED",
                        reason_closed="STOP_LOSS" if sl_hit else "TAKE_PROFIT",
                        opened_at=active_position["opened_at"],
                        closed_at=utc_now()
                    )
                    closed_trades.append(closed_trade)
                    trade_counter += 1
                    active_position = None

            # 2. Decision Engine Analysis
            if i >= 50:
                has_pos = active_position is not None
                eval_res = self.decision_engine.evaluate(current_slice, has_open_position=has_pos)
                signal = eval_res["signal"]

                if signal == "BUY" and active_position is None:
                    risk_amt = balance * settings.RISK_PER_TRADE
                    sl_dist = close_price * settings.DEFAULT_STOP_LOSS_PCT
                    sl_price = close_price - sl_dist
                    tp_price = close_price + (close_price * settings.DEFAULT_TAKE_PROFIT_PCT)

                    if sl_dist > 0:
                        qty = risk_amt / sl_dist
                        max_qty = balance / close_price
                        if qty > max_qty:
                            qty = max_qty

                        gross_cost = qty * close_price
                        open_fee = gross_cost * self.fee_percent
                        slippage = gross_cost * settings.SLIPPAGE_PERCENT

                        if balance >= gross_cost + open_fee + slippage:
                            balance -= (gross_cost + open_fee + slippage)
                            active_position = {
                                "entry_price": close_price,
                                "quantity": qty,
                                "stop_loss": sl_price,
                                "take_profit": tp_price,
                                "fees": open_fee,
                                "slippage": slippage,
                                "opened_at": utc_now()
                            }

                elif signal == "SELL" and active_position is not None:
                    gross_return = active_position["quantity"] * close_price
                    close_fee = gross_return * self.fee_percent
                    net_return = gross_return - close_fee
                    cost_basis = active_position["quantity"] * active_position["entry_price"]
                    total_fees = active_position["fees"] + close_fee
                    pnl = (gross_return - cost_basis) - total_fees
                    pnl_pct = (pnl / cost_basis) * 100.0 if cost_basis > 0 else 0.0

                    balance += net_return

                    closed_trade = TradeSchema(
                        id=trade_counter,
                        symbol=symbol,
                        side="BUY",
                        entry_price=round(active_position["entry_price"], 2),
                        exit_price=round(close_price, 2),
                        quantity=round(active_position["quantity"], 6),
                        stop_loss=round(active_position["stop_loss"], 2),
                        take_profit=round(active_position["take_profit"], 2),
                        trailing_stop=round(active_position["stop_loss"], 2),
                        profit_loss=round(pnl, 2),
                        profit_loss_percentage=round(pnl_pct, 2),
                        fees=round(total_fees, 4),
                        slippage=round(active_position["slippage"], 4),
                        status="CLOSED",
                        reason_closed="DECISION_SIGNAL",
                        opened_at=active_position["opened_at"],
                        closed_at=utc_now()
                    )
                    closed_trades.append(closed_trade)
                    trade_counter += 1
                    active_position = None

            # Track current equity
            current_equity = balance
            if active_position is not None:
                current_equity += (active_position["quantity"] * close_price)

            if len(equity_curve) > 0:
                prev_eq = equity_curve[-1].balance
                ret = (current_equity - prev_eq) / prev_eq if prev_eq > 0 else 0.0
                daily_returns.append(ret)

            if current_equity > peak_balance:
                peak_balance = current_equity

            drawdown = (peak_balance - current_equity) / peak_balance if peak_balance > 0 else 0.0
            if drawdown > max_drawdown:
                max_drawdown = drawdown

            equity_curve.append(EquityPoint(timestamp=ts, balance=round(current_equity, 2)))

        # Close lingering position
        if active_position is not None:
            last_close = float(df.iloc[-1]["close"])
            gross_return = active_position["quantity"] * last_close
            close_fee = gross_return * self.fee_percent
            cost_basis = active_position["quantity"] * active_position["entry_price"]
            total_fees = active_position["fees"] + close_fee
            pnl = (gross_return - cost_basis) - total_fees
            pnl_pct = (pnl / cost_basis) * 100.0 if cost_basis > 0 else 0.0

            balance += (gross_return - close_fee)

            closed_trade = TradeSchema(
                id=trade_counter,
                symbol=symbol,
                side="BUY",
                entry_price=round(active_position["entry_price"], 2),
                exit_price=round(last_close, 2),
                quantity=round(active_position["quantity"], 6),
                stop_loss=round(active_position["stop_loss"], 2),
                take_profit=round(active_position["take_profit"], 2),
                trailing_stop=round(active_position["stop_loss"], 2),
                profit_loss=round(pnl, 2),
                profit_loss_percentage=round(pnl_pct, 2),
                fees=round(total_fees, 4),
                slippage=round(active_position["slippage"], 4),
                status="CLOSED",
                reason_closed="BACKTEST_END",
                opened_at=active_position["opened_at"],
                closed_at=utc_now()
            )
            closed_trades.append(closed_trade)

        # Performance summary metrics
        total_trades = len(closed_trades)
        winning_trades = [t for t in closed_trades if (t.profit_loss or 0) > 0]
        losing_trades = [t for t in closed_trades if (t.profit_loss or 0) <= 0]

        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100.0) if total_trades > 0 else 0.0

        total_profit = sum(t.profit_loss for t in winning_trades)
        total_loss = abs(sum(t.profit_loss for t in losing_trades))

        avg_profit = (total_profit / win_count) if win_count > 0 else 0.0
        avg_loss = (total_loss / loss_count) if loss_count > 0 else 0.0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else (total_profit if total_profit > 0 else 1.0)

        # Sharpe ratio calculation
        sharpe = 0.0
        if len(daily_returns) > 1:
            mean_ret = np.mean(daily_returns)
            std_ret = np.std(daily_returns)
            if std_ret > 0:
                sharpe = float((mean_ret / std_ret) * np.sqrt(365))

        total_return_pct = ((balance - self.starting_balance) / self.starting_balance) * 100.0

        return PerformanceMetrics(
            starting_balance=round(self.starting_balance, 2),
            ending_balance=round(balance, 2),
            total_return_percent=round(total_return_pct, 2),
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate_percent=round(win_rate, 2),
            total_profit=round(total_profit, 2),
            total_loss=round(total_loss, 2),
            max_drawdown_percent=round(max_drawdown * 100.0, 2),
            avg_profit_per_trade=round(avg_profit, 2),
            avg_loss_per_trade=round(avg_loss, 2),
            profit_factor=round(profit_factor, 2),
            sharpe_ratio=round(sharpe, 2),
            equity_curve=equity_curve,
            trades=closed_trades
        )
