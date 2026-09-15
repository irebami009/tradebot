import pandas as pd
from app.engine.decision_engine import DecisionEngine

def test_decision_engine_scoring():
    engine = DecisionEngine(min_confidence=75.0)
    
    prices = [100.0 + (i * 1.5) for i in range(60)]
    df = pd.DataFrame({
        "timestamp": [f"2026-01-01 {i:02d}:00:00" for i in range(60)],
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [2000.0] * 60
    })

    result = engine.evaluate(df, has_open_position=False)
    assert "signal" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert isinstance(result["confidence"], float)
    assert len(result["reasoning"]) > 0
