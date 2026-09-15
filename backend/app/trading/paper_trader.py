from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.db_models import TradeModel, AccountStateModel, SignalModel, RiskEventModel
from app.adapters.paper_adapter import PaperExchangeAdapter
from app.engine.decision_engine import DecisionEngine
from app.engine.trade_validator import TradeValidator
from app.trading.risk_manager import RiskManager
from app.config import settings

def utc_now():
    return datetime.now(timezone.utc)

class PaperTrader:
    def __init__(self, db: Session, starting_balance: float = settings.STARTING_BALANCE):
        self.db = db
        self.adapter = PaperExchangeAdapter(data_file=settings.DATA_FILE, starting_balance=starting_balance)
        self.risk_manager = RiskManager(
            risk_per_trade=settings.RISK_PER_TRADE,
            stop_loss_percent=settings.DEFAULT_STOP_LOSS_PCT,
            take_profit_percent=settings.DEFAULT_TAKE_PROFIT_PCT,
            max_daily_loss=settings.MAX_DAILY_LOSS,
            max_positions=settings.MAX_OPEN_POSITIONS
        )
        self.trade_validator = TradeValidator()
        self.decision_engine = DecisionEngine(min_confidence=settings.MIN_CONFIDENCE_THRESHOLD)
        self._initialize_account_state(starting_balance)

    def _initialize_account_state(self, starting_balance: float):
        state = self.db.query(AccountStateModel).first()
        today_str = utc_now().strftime("%Y-%m-%d")
        if not state:
            state = AccountStateModel(
                id=1,
                balance=starting_balance,
                peak_balance=starting_balance,
                daily_starting_balance=starting_balance,
                consecutive_losses=0,
                last_reset_day=today_str
            )
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
        else:
            if state.last_reset_day != today_str:
                state.daily_starting_balance = state.balance
                state.last_reset_day = today_str
                self.db.commit()

    def get_account_state(self) -> AccountStateModel:
        return self.db.query(AccountStateModel).first()

    def get_open_position(self) -> Optional[TradeModel]:
        return self.db.query(TradeModel).filter(TradeModel.status == "OPEN").first()

    def get_all_trades(self) -> List[TradeModel]:
        return self.db.query(TradeModel).order_by(TradeModel.opened_at.desc()).all()

    def open_position(
        self,
        symbol: str,
        current_price: float,
        timestamp: Optional[datetime] = None
    ) -> Optional[TradeModel]:
        open_pos = self.get_open_position()
        state = self.get_account_state()

        if open_pos is not None:
            return None

        qty, stop_loss, take_profit = self.risk_manager.calculate_position_size(
            account_balance=state.balance,
            entry_price=current_price
        )

        if qty <= 0:
            return None

        # Validate trade with TradeValidator gatekeeper
        allowed, reason = self.trade_validator.validate_trade(
            current_open_positions=1 if open_pos else 0,
            daily_starting_balance=state.daily_starting_balance,
            current_balance=state.balance,
            total_portfolio_exposure=0.0,
            consecutive_losses=state.consecutive_losses,
            entry_price=current_price,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
            last_data_timestamp=timestamp or utc_now()
        )

        if not allowed:
            print(f"[PAPER TRADER REJECTED] {reason}")
            risk_evt = RiskEventModel(
                event_type="TRADE_REJECTED",
                severity="WARNING",
                message=reason
            )
            self.db.add(risk_evt)
            self.db.commit()
            return None

        gross_cost = qty * current_price
        open_fee = gross_cost * settings.TRADING_FEE_PERCENT
        slippage = gross_cost * settings.SLIPPAGE_PERCENT

        if state.balance < gross_cost + open_fee:
            return None

        state.balance -= (gross_cost + open_fee)

        trade = TradeModel(
            symbol=symbol,
            side="BUY",
            entry_price=current_price,
            quantity=qty,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_stop=stop_loss,
            fees=open_fee,
            slippage=slippage,
            status="OPEN",
            opened_at=timestamp or utc_now()
        )

        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        self.db.refresh(state)

        print(f"[PAPER TRADER] BUY {qty:.6f} {symbol} @ ${current_price:.2f} (SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})")
        return trade

    def close_position(
        self,
        trade_id: int,
        exit_price: float,
        timestamp: Optional[datetime] = None,
        reason: str = "SIGNAL"
    ) -> Optional[TradeModel]:
        trade = self.db.query(TradeModel).filter(
            TradeModel.id == trade_id,
            TradeModel.status == "OPEN"
        ).first()

        if not trade:
            return None

        state = self.get_account_state()

        gross_return = trade.quantity * exit_price
        close_fee = gross_return * settings.TRADING_FEE_PERCENT
        net_return = gross_return - close_fee

        trade_cost = trade.quantity * trade.entry_price
        total_fees = trade.fees + close_fee
        pnl = (gross_return - trade_cost) - total_fees
        pnl_percent = (pnl / trade_cost) * 100.0 if trade_cost > 0 else 0.0

        trade.exit_price = exit_price
        trade.profit_loss = round(pnl, 2)
        trade.profit_loss_percentage = round(pnl_percent, 2)
        trade.fees = round(total_fees, 4)
        trade.status = "CLOSED"
        trade.reason_closed = reason
        trade.closed_at = timestamp or utc_now()

        # Update balance & consecutive loss counter
        state.balance += net_return
        if state.balance > state.peak_balance:
            state.peak_balance = state.balance

        if pnl < 0:
            state.consecutive_losses += 1
        else:
            state.consecutive_losses = 0

        self.db.commit()
        self.db.refresh(trade)
        self.db.refresh(state)

        print(f"[PAPER TRADER] SELL {trade.quantity:.6f} {trade.symbol} @ ${exit_price:.2f} | Reason: {reason} | PnL: ${pnl:.2f} ({pnl_percent:.2f}%)")
        return trade

    def check_sl_tp_triggers(self, current_high: float, current_low: float, timestamp: Optional[datetime] = None) -> Optional[TradeModel]:
        open_pos = self.get_open_position()
        if not open_pos:
            return None

        if current_low <= open_pos.stop_loss:
            return self.close_position(open_pos.id, exit_price=open_pos.stop_loss, timestamp=timestamp, reason="STOP_LOSS")

        if current_high >= open_pos.take_profit:
            return self.close_position(open_pos.id, exit_price=open_pos.take_profit, timestamp=timestamp, reason="TAKE_PROFIT")

        return None
