from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.schemas import TradeSchema, PositionSchema
from app.models.db_models import TradeModel
from app.trading.paper_trader import PaperTrader
from app.services.bot_runner import bot_runner_instance

router = APIRouter(tags=["Trades"])

@router.get("/trades", response_model=List[TradeSchema])
def get_trades(db: Session = Depends(get_db)):
    trader = PaperTrader(db)
    return trader.get_all_trades()

@router.get("/positions", response_model=List[PositionSchema])
def get_positions(db: Session = Depends(get_db)):
    trader = PaperTrader(db)
    pos = trader.get_open_position()
    if not pos:
        return []

    current_price = pos.entry_price
    if bot_runner_instance.last_candle:
        current_price = bot_runner_instance.last_candle.get("close", pos.entry_price)

    gross = pos.quantity * current_price
    cost = pos.quantity * pos.entry_price
    unrealized_pnl = gross - cost - pos.fees
    unrealized_pnl_pct = (unrealized_pnl / cost * 100.0) if cost > 0 else 0.0

    return [
        PositionSchema(
            id=pos.id,
            symbol=pos.symbol,
            side=pos.side,
            entry_price=pos.entry_price,
            current_price=current_price,
            quantity=pos.quantity,
            stop_loss=pos.stop_loss,
            take_profit=pos.take_profit,
            trailing_stop=pos.trailing_stop,
            unrealized_pnl=round(unrealized_pnl, 2),
            unrealized_pnl_percent=round(unrealized_pnl_pct, 2)
        )
    ]
