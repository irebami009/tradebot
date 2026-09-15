from app.engine.trade_validator import TradeValidator
from app.config import settings

def test_trade_validator_gatekeeper():
    validator = TradeValidator()

    # Valid trade test
    allowed, reason = validator.validate_trade(
        current_open_positions=0,
        daily_starting_balance=10000.0,
        current_balance=10000.0,
        total_portfolio_exposure=0.0,
        consecutive_losses=0,
        entry_price=50000.0,
        stop_loss_price=49000.0,  # $1000 risk
        take_profit_price=52000.0 # $2000 reward -> R/R = 2.0
    )
    assert allowed
    assert "passed" in reason.lower()

    # Reject on poor Risk/Reward (< 2.0)
    allowed, reason = validator.validate_trade(
        current_open_positions=0,
        daily_starting_balance=10000.0,
        current_balance=10000.0,
        total_portfolio_exposure=0.0,
        consecutive_losses=0,
        entry_price=50000.0,
        stop_loss_price=49000.0,  # $1000 risk
        take_profit_price=51000.0 # $1000 reward -> R/R = 1.0 < 2.0
    )
    assert not allowed
    assert "Risk/Reward" in reason
