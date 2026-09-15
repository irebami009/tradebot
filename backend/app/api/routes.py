from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.schemas import (
    BotStatusSchema,
    AccountBalance,
    BacktestRequest,
    PerformanceMetrics,
    PositionSchema,
    SignalSchema,
    RiskEventSchema,
    BotLogSchema
)
from app.models.db_models import SignalModel, RiskEventModel, BotLogModel
from app.trading.paper_trader import PaperTrader
from app.trading.backtester import BacktestEngine
from app.services.market_data import CSVMarketDataProvider
from app.services.bot_runner import bot_runner_instance
from app.engine.emergency import EmergencyRiskController
from app.config import settings

router = APIRouter()
emergency_controller = EmergencyRiskController()

@router.get("/status", response_model=BotStatusSchema)
def get_status(db: Session = Depends(get_db)):
    trader = PaperTrader(db)
    pos = trader.get_open_position()

    active_pos_schema = None
    if pos:
        current_price = pos.entry_price
        if bot_runner_instance.last_candle:
            current_price = bot_runner_instance.last_candle.get("close", pos.entry_price)

        gross = pos.quantity * current_price
        cost = pos.quantity * pos.entry_price
        unrealized = gross - cost - pos.fees
        unrealized_pct = (unrealized / cost * 100.0) if cost > 0 else 0.0

        active_pos_schema = PositionSchema(
            id=pos.id,
            symbol=pos.symbol,
            side=pos.side,
            entry_price=pos.entry_price,
            current_price=current_price,
            quantity=pos.quantity,
            stop_loss=pos.stop_loss,
            take_profit=pos.take_profit,
            trailing_stop=pos.trailing_stop,
            unrealized_pnl=round(unrealized, 2),
            unrealized_pnl_percent=round(unrealized_pct, 2)
        )

    warning_text = "PAPER TRADING — SIMULATION MODE"
    if settings.MODE == "LIVE":
        warning_text = "🔴 REAL MONEY — LIVE TRADING ACTIVE"

    return BotStatusSchema(
        is_running=bot_runner_instance.is_running,
        mode=settings.MODE,
        emergency_stop=settings.EMERGENCY_STOP,
        warning=warning_text,
        latest_signal=bot_runner_instance.latest_signal,
        latest_confidence=bot_runner_instance.latest_confidence,
        market_regime=bot_runner_instance.market_regime,
        active_positions_count=1 if pos else 0,
        active_position=active_pos_schema,
        last_processed_candle=bot_runner_instance.last_candle
    )

@router.get("/balance", response_model=AccountBalance)
def get_balance(db: Session = Depends(get_db)):
    trader = PaperTrader(db)
    state = trader.get_account_state()
    pos = trader.get_open_position()

    unrealized_pnl = 0.0
    if pos:
        current_price = pos.entry_price
        if bot_runner_instance.last_candle:
            current_price = bot_runner_instance.last_candle.get("close", pos.entry_price)
        gross = pos.quantity * current_price
        cost = pos.quantity * pos.entry_price
        unrealized_pnl = gross - cost - pos.fees

    equity = state.balance + unrealized_pnl
    realized_pnl = state.balance - settings.STARTING_BALANCE

    daily_pnl_pct = 0.0
    if state.daily_starting_balance > 0:
        daily_pnl_pct = ((equity - state.daily_starting_balance) / state.daily_starting_balance) * 100.0

    return AccountBalance(
        virtual_balance=round(state.balance, 2),
        equity=round(equity, 2),
        unrealized_pnl=round(unrealized_pnl, 2),
        realized_pnl=round(realized_pnl, 2),
        daily_pnl_percent=round(daily_pnl_pct, 2),
        consecutive_losses=state.consecutive_losses,
        mode=settings.MODE
    )

@router.get("/signals", response_model=List[SignalSchema])
def get_signals(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(SignalModel).order_by(SignalModel.timestamp.desc()).limit(limit).all()

@router.get("/risk/events", response_model=List[RiskEventSchema])
def get_risk_events(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(RiskEventModel).order_by(RiskEventModel.timestamp.desc()).limit(limit).all()

@router.post("/bot/start")
def start_bot():
    if settings.EMERGENCY_STOP:
        raise HTTPException(status_code=400, detail="Cannot start bot while EMERGENCY_STOP is active.")
    bot_runner_instance.start()
    return {"status": "success", "message": "Trading bot started successfully", "is_running": True}

@router.post("/bot/stop")
def stop_bot():
    bot_runner_instance.stop()
    return {"status": "success", "message": "Trading bot stopped successfully", "is_running": False}

@router.post("/emergency/trigger")
def trigger_emergency():
    bot_runner_instance.stop()
    res = emergency_controller.trigger_emergency_stop("User Manual Emergency Trigger from Dashboard")
    return res

@router.post("/emergency/reset")
def reset_emergency():
    res = emergency_controller.reset_emergency_stop()
    return res

@router.get("/performance", response_model=PerformanceMetrics)
def get_performance(db: Session = Depends(get_db)):
    data_provider = CSVMarketDataProvider(settings.DATA_FILE)
    df = data_provider.fetch_ohlcv(symbol="BTC/USD", limit=1000)

    engine = BacktestEngine(
        starting_balance=settings.STARTING_BALANCE,
        risk_per_trade=settings.RISK_PER_TRADE,
        stop_loss_percent=settings.DEFAULT_STOP_LOSS_PCT,
        take_profit_percent=settings.DEFAULT_TAKE_PROFIT_PCT,
        min_confidence=settings.MIN_CONFIDENCE_THRESHOLD
    )
    return engine.run(df, symbol="BTC/USD")

@router.post("/backtest", response_model=PerformanceMetrics)
def run_custom_backtest(req: BacktestRequest):
    try:
        data_provider = CSVMarketDataProvider(settings.DATA_FILE)
        df = data_provider.fetch_ohlcv(symbol=req.symbol, limit=1000)

        engine = BacktestEngine(
            starting_balance=req.starting_balance,
            risk_per_trade=req.risk_per_trade,
            stop_loss_percent=req.stop_loss_percent,
            take_profit_percent=req.take_profit_percent,
            min_confidence=req.min_confidence
        )
        return engine.run(df, symbol=req.symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")
