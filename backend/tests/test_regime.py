import pandas as pd
from app.engine.indicators import add_full_indicators
from app.engine.regime_detector import MarketRegimeDetector

def test_market_regime_classification():
    detector = MarketRegimeDetector()
    
    # Create strong bullish trend dataset
    prices = [100.0 + (i * 2.0) for i in range(60)]
    df = pd.DataFrame({
        "timestamp": [f"2026-01-01 {i:02d}:00:00" for i in range(60)],
        "open": prices,
        "high": [p + 1.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [1000.0] * 60
    })
    df_ind = add_full_indicators(df)
    regime = detector.classify(df_ind)
    assert regime in ["TRENDING_BULLISH", "HIGH_VOLATILITY", "RANGING"]
