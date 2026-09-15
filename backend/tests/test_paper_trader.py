from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.trading.paper_trader import PaperTrader

def test_paper_trader_flow():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    trader = PaperTrader(db, starting_balance=10000.0)
    
    state = trader.get_account_state()
    assert state.balance == 10000.0

    trade = trader.open_position("BTC/USD", current_price=50000.0)
    assert trade is not None
    assert trade.status == "OPEN"
    assert trader.get_open_position() is not None

    closed_trade = trader.close_position(trade.id, exit_price=52000.0)
    assert closed_trade is not None
    assert closed_trade.status == "CLOSED"
    assert closed_trade.profit_loss > 0
    assert trader.get_open_position() is None
