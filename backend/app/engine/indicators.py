import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List

def calculate_ema(df: pd.DataFrame, column: str = "close", period: int = 20) -> pd.Series:
    if column not in df.columns or len(df) == 0:
        return pd.Series(dtype=float)
    return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, column: str = "close", period: int = 14) -> pd.Series:
    if column not in df.columns or len(df) == 0:
        return pd.Series(dtype=float)
    delta = df[column].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1.0/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / np.where(avg_loss == 0, 1e-10, avg_loss)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)

def calculate_macd(df: pd.DataFrame, column: str = "close", fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = calculate_ema(df, column, fast)
    ema_slow = calculate_ema(df, column, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    if len(df) == 0:
        return pd.Series(dtype=float)
    high = df["high"]
    low = df["low"]
    close = df["close"].shift(1)
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0/period, min_periods=period, adjust=False).mean().fillna(0.0)

def calculate_bollinger_bands(df: pd.DataFrame, column: str = "close", period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    if column not in df.columns or len(df) == 0:
        s = pd.Series(dtype=float)
        return s, s, s
    sma = df[column].rolling(window=period).mean()
    rolling_std = df[column].rolling(window=period).std()
    upper = sma + (rolling_std * std_dev)
    lower = sma - (rolling_std * std_dev)
    return sma, upper.fillna(df[column]), lower.fillna(df[column])

def detect_support_resistance(df: pd.DataFrame, window: int = 5) -> Tuple[List[float], List[float]]:
    """
    Detects key swing high (resistance) and swing low (support) pivot levels.
    """
    supports = []
    resistances = []
    if len(df) < (window * 2) + 1:
        return supports, resistances

    for i in range(window, len(df) - window):
        low_window = df["low"].iloc[i-window:i+window+1]
        high_window = df["high"].iloc[i-window:i+window+1]

        if df["low"].iloc[i] == low_window.min():
            supports.append(round(float(df["low"].iloc[i]), 2))
        if df["high"].iloc[i] == high_window.max():
            resistances.append(round(float(df["high"].iloc[i]), 2))

    return supports[-3:], resistances[-3:]

def add_full_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies complete indicator suite to OHLCV DataFrame.
    """
    df_copy = df.copy()
    df_copy["ema_20"] = calculate_ema(df_copy, "close", 20)
    df_copy["ema_50"] = calculate_ema(df_copy, "close", 50)
    df_copy["ema_200"] = calculate_ema(df_copy, "close", 200)
    df_copy["rsi"] = calculate_rsi(df_copy, "close", 14)
    macd, macd_sig, macd_hist = calculate_macd(df_copy, "close", 12, 26, 9)
    df_copy["macd"] = macd
    df_copy["macd_signal"] = macd_sig
    df_copy["macd_hist"] = macd_hist
    df_copy["atr"] = calculate_atr(df_copy, 14)
    sma_bb, upper_bb, lower_bb = calculate_bollinger_bands(df_copy, "close", 20, 2.0)
    df_copy["upper_band"] = upper_bb
    df_copy["lower_band"] = lower_bb
    df_copy["volume_sma"] = df_copy["volume"].rolling(window=20).mean().fillna(df_copy["volume"])
    df_copy["volume_spike"] = df_copy["volume"] > (df_copy["volume_sma"] * 1.5)
    return df_copy
