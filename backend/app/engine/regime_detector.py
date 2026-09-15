import pandas as pd
from typing import Literal

RegimeType = Literal[
    "TRENDING_BULLISH",
    "TRENDING_BEARISH",
    "RANGING",
    "HIGH_VOLATILITY",
    "LOW_VOLATILITY",
    "UNCLEAR"
]

class MarketRegimeDetector:
    """
    Classifies market state into distinct regimes (Bullish, Bearish, Ranging, High/Low Volatility, Unclear).
    """

    def classify(self, df_ind: pd.DataFrame) -> RegimeType:
        if len(df_ind) < 50:
            return "UNCLEAR"

        curr = df_ind.iloc[-1]
        
        close = float(curr["close"])
        ema20 = float(curr["ema_20"])
        ema50 = float(curr["ema_50"])
        ema200 = float(curr["ema_200"])
        atr = float(curr["atr"])
        avg_atr = float(df_ind["atr"].rolling(window=20).mean().iloc[-1])

        upper_bb = float(curr["upper_band"])
        lower_bb = float(curr["lower_band"])
        bb_bandwidth = (upper_bb - lower_bb) / close if close > 0 else 0.0

        # 1. High Volatility Check
        if avg_atr > 0 and atr > (avg_atr * 2.0):
            return "HIGH_VOLATILITY"

        # 2. Trending Bullish Check (EMA 20 > 50 > 200 and Price > EMA 20)
        if ema20 > ema50 > ema200 and close > ema20:
            return "TRENDING_BULLISH"

        # 3. Trending Bearish Check (EMA 20 < 50 < 200 and Price < EMA 20)
        if ema20 < ema50 < ema200 and close < ema20:
            return "TRENDING_BEARISH"

        # 4. Ranging / Compression Check (Narrow BB Bandwidth < 3% and EMAs tight)
        if bb_bandwidth < 0.03 and abs(ema20 - ema50) / close < 0.005:
            return "RANGING"

        # 5. Low Volatility Check
        if avg_atr > 0 and atr < (avg_atr * 0.5):
            return "LOW_VOLATILITY"

        return "UNCLEAR"
