import pandas as pd
import numpy as np

def calculate_ema(df: pd.DataFrame, column: str = "close", period: int = 9) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA) using Pandas ewm.
    """
    if column not in df.columns or len(df) == 0:
        return pd.Series(dtype=float)
    return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, column: str = "close", period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI) using Wilder's smoothing algorithm.
    """
    if column not in df.columns or len(df) == 0:
        return pd.Series(dtype=float)
    
    delta = df[column].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    # Wilder's Exponential Moving Average for RSI
    avg_gain = gain.ewm(alpha=1.0/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0/period, min_periods=period, adjust=False).mean()

    # Avoid division by zero
    rs = avg_gain / np.where(avg_loss == 0, 1e-10, avg_loss)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    # Fill NaN for initial periods
    return rsi.fillna(50.0)

def add_indicators(df: pd.DataFrame, ema_fast: int = 9, ema_slow: int = 21, rsi_period: int = 14) -> pd.DataFrame:
    """
    Applies EMA fast, EMA slow, and RSI indicators to an OHLCV DataFrame.
    Returns a copy of the dataframe with added indicator columns.
    """
    df_copy = df.copy()
    df_copy[f"ema_{ema_fast}"] = calculate_ema(df_copy, "close", ema_fast)
    df_copy[f"ema_{ema_slow}"] = calculate_ema(df_copy, "close", ema_slow)
    df_copy["rsi"] = calculate_rsi(df_copy, "close", rsi_period)
    return df_copy
