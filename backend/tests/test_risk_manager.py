from app.trading.risk_manager import RiskManager

def test_risk_manager_position_sizing():
    rm = RiskManager(risk_per_trade=0.01, stop_loss_percent=0.02, take_profit_percent=0.04)
    balance = 1000.0
    entry = 50000.0

    qty, sl, tp = rm.calculate_position_size(balance, entry)

    # 1% risk = $10. SL dist = 2% of $50k = $1000. Qty = 10 / 1000 = 0.01 BTC
    assert qty == 0.01
    assert sl == 49000.0
    assert tp == 52000.0

def test_risk_manager_limits():
    rm = RiskManager(max_daily_loss=0.05, max_positions=1)
    
    # Exceed max positions
    allowed, reason = rm.is_trade_allowed(current_open_positions=1, daily_starting_balance=1000.0, current_balance=1000.0)
    assert not allowed
    assert "positions limit" in reason

    # Exceed max daily loss (current balance 940 vs starting 1000 = 6% loss)
    allowed, reason = rm.is_trade_allowed(current_open_positions=0, daily_starting_balance=1000.0, current_balance=940.0)
    assert not allowed
    assert "daily loss" in reason
