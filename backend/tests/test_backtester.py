import pandas as pd
from app.trading.backtester import BacktestEngine

def test_backtester_metrics():
    # Synthetic dataset
    timestamps = [f"2026-01-01 {i:02d}:00:00" for i in range(50)]
    closes = [50000.0 + (i * 100 if i < 25 else -i * 50) for i in range(50)]
    df = pd.DataFrame({
        "timestamp": timestamps,
        "open": closes,
        "high": [c + 50 for c in closes],
        "low": [c - 50 for c in closes],
        "close": closes,
        "volume": [100.0] * 50
    })

    engine = BacktestEngine(starting_balance=1000.0)
    results = engine.run(df, symbol="BTC/USD")

    assert results.starting_balance == 1000.0
    assert results.total_trades >= 0
    assert isinstance(results.win_rate_percent, float)
    assert len(results.equity_curve) == 50
