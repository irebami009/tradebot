import pandas as pd
from typing import Literal
from app.strategy.indicators import add_indicators

SignalType = Literal["BUY", "SELL", "HOLD"]

class EMACrossoverRSIStrategy:
    def __init__(
        self,
        ema_fast_period: int = 9,
        ema_slow_period: int = 21,
        rsi_period: int = 14,
        rsi_buy_threshold: float = 50.0,
        rsi_sell_threshold: float = 50.0
    ):
        self.ema_fast_period = ema_fast_period
        self.ema_slow_period = ema_slow_period
        self.rsi_period = rsi_period
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold

    def evaluate_signal(self, df: pd.DataFrame, has_open_position: bool) -> SignalType:
        """
        Evaluate market indicators on the given DataFrame and return 'BUY', 'SELL', or 'HOLD'.
        Assumes df contains at least the required period length of OHLCV data.
        """
        if len(df) < max(self.ema_slow_period, self.rsi_period) + 1:
            return "HOLD"

        # Compute indicators
        df_ind = add_indicators(
            df,
            ema_fast=self.ema_fast_period,
            ema_slow=self.ema_slow_period,
            rsi_period=self.rsi_period
        )

        curr_candle = df_ind.iloc[-1]
        prev_candle = df_ind.iloc[-2]

        ema_fast_col = f"ema_{self.ema_fast_period}"
        ema_slow_col = f"ema_{self.ema_slow_period}"

        curr_ema_fast = curr_candle[ema_fast_col]
        curr_ema_slow = curr_candle[ema_slow_col]
        prev_ema_fast = prev_candle[ema_fast_col]
        prev_ema_slow = prev_candle[ema_slow_col]
        curr_rsi = curr_candle["rsi"]

        # Crossover logic
        bullish_crossover = (prev_ema_fast <= prev_ema_slow) and (curr_ema_fast > curr_ema_slow)
        bearish_crossover = (prev_ema_fast >= prev_ema_slow) and (curr_ema_fast < curr_ema_slow)

        # BUY Condition
        if bullish_crossover and curr_rsi > self.rsi_buy_threshold and not has_open_position:
            return "BUY"

        # SELL Condition
        if bearish_crossover and curr_rsi < self.rsi_sell_threshold and has_open_position:
            return "SELL"

        return "HOLD"
