import pandas as pd
import numpy as np
from app.strategy.indicators import calculate_ema, calculate_rsi, add_indicators

def test_calculate_ema():
    prices = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0]
    df = pd.DataFrame({"close": prices})
    ema9 = calculate_ema(df, "close", period=9)
    assert len(ema9) == len(prices)
    assert not ema9.isna().any()
    assert ema9.iloc[-1] > ema9.iloc[0]

def test_calculate_rsi():
    # Increasing price series should yield high RSI (>50)
    prices = [10.0 + i for i in range(20)]
    df = pd.DataFrame({"close": prices})
    rsi = calculate_rsi(df, "close", period=14)
    assert len(rsi) == len(prices)
    assert rsi.iloc[-1] > 70.0  # Strong uptrend

def test_add_indicators():
    df = pd.DataFrame({
        "timestamp": ["2026-01-01"] * 30,
        "open": [100.0] * 30,
        "high": [105.0] * 30,
        "low": [95.0] * 30,
        "close": [100.0 + i for i in range(30)],
        "volume": [1000.0] * 30
    })
    df_ind = add_indicators(df, ema_fast=9, ema_slow=21, rsi_period=14)
    assert "ema_9" in df_ind.columns
    assert "ema_21" in df_ind.columns
    assert "rsi" in df_ind.columns
