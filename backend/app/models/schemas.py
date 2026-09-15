from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TradeSchema(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    stop_loss: float
    take_profit: float
    trailing_stop: Optional[float] = None
    profit_loss: Optional[float] = 0.0
    profit_loss_percentage: Optional[float] = 0.0
    fees: float
    slippage: float
    status: str
    broker_order_id: Optional[str] = None
    reason_closed: Optional[str] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SignalSchema(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    symbol: str
    timeframe: str = "1h"
    signal_type: str  # BUY, SELL, HOLD
    confidence_score: float
    market_regime: str
    risk_reward_ratio: Optional[float] = None
    stop_loss_suggested: Optional[float] = None
    take_profit_suggested: Optional[float] = None
    reasoning_summary: str
    detailed_scores: Optional[Dict[str, float]] = None
    executed: bool = False

    model_config = ConfigDict(from_attributes=True)

class AccountBalance(BaseModel):
    virtual_balance: float
    equity: float
    unrealized_pnl: float
    realized_pnl: float
    daily_pnl_percent: float
    consecutive_losses: int
    mode: str

class PositionSchema(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    current_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    trailing_stop: Optional[float] = None
    unrealized_pnl: float
    unrealized_pnl_percent: float

class BotStatusSchema(BaseModel):
    is_running: bool
    mode: str = "PAPER"
    emergency_stop: bool = False
    warning: str = "PAPER TRADING — SIMULATION"
    latest_signal: str = "HOLD"
    latest_confidence: float = 0.0
    market_regime: str = "UNCLEAR"
    active_positions_count: int = 0
    active_position: Optional[PositionSchema] = None
    last_processed_candle: Optional[Dict[str, Any]] = None

class RiskEventSchema(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    severity: str
    message: str
    details: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class BotLogSchema(BaseModel):
    id: int
    timestamp: datetime
    level: str
    module: str
    message: str

    model_config = ConfigDict(from_attributes=True)

class BacktestRequest(BaseModel):
    symbol: str = "BTC/USD"
    starting_balance: float = 10000.0
    risk_per_trade: float = 0.01
    stop_loss_percent: float = 0.02
    take_profit_percent: float = 0.04
    min_confidence: float = 75.0

class EquityPoint(BaseModel):
    timestamp: str
    balance: float

class PerformanceMetrics(BaseModel):
    starting_balance: float
    ending_balance: float
    total_return_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_percent: float
    total_profit: float
    total_loss: float
    max_drawdown_percent: float
    avg_profit_per_trade: float
    avg_loss_per_trade: float
    profit_factor: float
    sharpe_ratio: float = 0.0
    equity_curve: List[EquityPoint] = []
    trades: List[TradeSchema] = []

class CandleSchema(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    atr: Optional[float] = None
    upper_band: Optional[float] = None
    lower_band: Optional[float] = None
