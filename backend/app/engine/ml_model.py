import pandas as pd
import numpy as np
from typing import Dict, Any

class MLSignalClassifier:
    """
    Machine Learning Probabilistic Classifier evaluating P(Up), P(Down), and P(Range).
    Acts as an additional confirmation signal to the Decision Engine without bypassing safety checks.
    """
    def __init__(self):
        self.is_trained = False

    def predict_probabilities(self, df_ind: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates directional probabilities based on feature ensemble.
        """
        if len(df_ind) < 20:
            return {"p_up": 0.33, "p_down": 0.33, "p_range": 0.34}

        curr = df_ind.iloc[-1]
        rsi = float(curr.get("rsi", 50.0))
        macd_hist = float(curr.get("macd_hist", 0.0))
        close = float(curr.get("close", 1.0))
        ema20 = float(curr.get("ema_20", close))

        # Rule-based probabilistic calculation
        p_up = 0.33
        p_down = 0.33
        p_range = 0.34

        if rsi > 55 and macd_hist > 0 and close > ema20:
            p_up = min(0.85, 0.45 + (rsi - 50) * 0.01)
            p_down = (1.0 - p_up) * 0.4
            p_range = 1.0 - p_up - p_down
        elif rsi < 45 and macd_hist < 0 and close < ema20:
            p_down = min(0.85, 0.45 + (50 - rsi) * 0.01)
            p_up = (1.0 - p_down) * 0.4
            p_range = 1.0 - p_up - p_down
        else:
            p_range = 0.60
            p_up = 0.20
            p_down = 0.20

        return {
            "p_up": round(p_up, 4),
            "p_down": round(p_down, 4),
            "p_range": round(p_range, 4)
        }
