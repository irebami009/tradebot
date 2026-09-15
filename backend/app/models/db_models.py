from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from datetime import datetime, timezone
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class TradeModel(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String, nullable=False, default="BTC/USD")
    side = Column(String, nullable=False, default="BUY")
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    trailing_stop = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True, default=0.0)
    profit_loss_percentage = Column(Float, nullable=True, default=0.0)
    fees = Column(Float, nullable=False, default=0.0)
    slippage = Column(Float, nullable=False, default=0.0)
    status = Column(String, nullable=False, default="OPEN") # OPEN, CLOSED, CANCELLED
    broker_order_id = Column(String, nullable=True)
    reason_closed = Column(String, nullable=True)
    opened_at = Column(DateTime(timezone=True), default=utc_now)
    closed_at = Column(DateTime(timezone=True), nullable=True)

class SignalModel(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False, default="1h")
    signal_type = Column(String, nullable=False)  # BUY, SELL, HOLD
    confidence_score = Column(Float, nullable=False)
    market_regime = Column(String, nullable=False)
    risk_reward_ratio = Column(Float, nullable=True)
    stop_loss_suggested = Column(Float, nullable=True)
    take_profit_suggested = Column(Float, nullable=True)
    reasoning_summary = Column(Text, nullable=False)
    detailed_scores = Column(JSON, nullable=True)
    executed = Column(Boolean, default=False)

class RiskEventModel(Base):
    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
    event_type = Column(String, nullable=False)  # EMERGENCY_STOP, MAX_DAILY_LOSS, COOLDOWN, STALE_DATA
    severity = Column(String, nullable=False, default="HIGH")  # INFO, WARNING, HIGH, CRITICAL
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)

class BotLogModel(Base):
    __tablename__ = "bot_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
    level = Column(String, nullable=False, default="INFO")
    module = Column(String, nullable=False)
    message = Column(Text, nullable=False)

class AccountStateModel(Base):
    __tablename__ = "account_state"

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, nullable=False, default=10000.0)
    peak_balance = Column(Float, nullable=False, default=10000.0)
    daily_starting_balance = Column(Float, nullable=False, default=10000.0)
    consecutive_losses = Column(Integer, default=0)
    cooldown_until = Column(DateTime(timezone=True), nullable=True)
    last_reset_day = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
