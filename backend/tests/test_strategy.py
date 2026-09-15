import pandas as pd
from app.engine.decision_engine import DecisionEngine

def test_strategy_buy_signal():
    engine = DecisionEngine(min_confidence=75.0)
    prices = [100.0 + (i * 2.0) for i in range(60)]
    df = pd.DataFrame({
        "timestamp": [f"2026-01-01 {i:02d}:00:00" for i in range(60)],
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [2000.0] * 60
    })
    
    result = engine.evaluate(df, has_open_position=False)
    assert result["signal"] in ["BUY", "HOLD"]

def test_strategy_hold_when_position_open():
    engine = DecisionEngine(min_confidence=75.0)
    prices = [100.0 + (i * 2.0) for i in range(60)]
    df = pd.DataFrame({
        "timestamp": [f"2026-01-01 {i:02d}:00:00" for i in range(60)],
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [2000.0] * 60
    })
    
    result = engine.evaluate(df, has_open_position=True)
    assert result["signal"] != "BUY"
