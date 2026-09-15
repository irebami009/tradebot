import pandas as pd
from typing import Dict, Any, Tuple
from app.engine.indicators import add_full_indicators, detect_support_resistance
from app.engine.regime_detector import MarketRegimeDetector
from app.config import settings

class DecisionEngine:
    """
    Weighted confidence scoring engine evaluating Trend (25%), Momentum (20%), Price Action (20%),
    Volume (10%), Volatility (10%), and Support/Resistance (15%).
    Generates confidence score (0-100%) and auditable 'WHY' reasoning strings.
    """
    def __init__(self, min_confidence: float = settings.MIN_CONFIDENCE_THRESHOLD):
        self.min_confidence = min_confidence
        self.regime_detector = MarketRegimeDetector()

    def evaluate(self, df: pd.DataFrame, has_open_position: bool) -> Dict[str, Any]:
        if len(df) < 50:
            return {
                "signal": "HOLD",
                "confidence": 0.0,
                "regime": "UNCLEAR",
                "reasoning": ["Insufficient candle history for analysis"],
                "detailed_scores": {}
            }

        df_ind = add_full_indicators(df)
        curr = df_ind.iloc[-1]
        prev = df_ind.iloc[-2]
        regime = self.regime_detector.classify(df_ind)

        close = float(curr["close"])
        ema20 = float(curr["ema_20"])
        ema50 = float(curr["ema_50"])
        ema200 = float(curr["ema_200"])
        rsi = float(curr["rsi"])
        macd = float(curr["macd"])
        macd_sig = float(curr["macd_signal"])
        vol = float(curr["volume"])
        vol_sma = float(curr["volume_sma"])

        supports, resistances = detect_support_resistance(df)

        reasoning = []
        scores = {
            "trend": 0.0,
            "momentum": 0.0,
            "price_action": 0.0,
            "volume": 0.0,
            "volatility": 0.0,
            "support_resistance": 0.0
        }

        # 1. Trend Analysis (25% Weight)
        if ema20 > ema50 > ema200 and close > ema20:
            scores["trend"] = 100.0
            reasoning.append("Strong Bullish Trend: EMA 20 > 50 > 200 and Price > EMA 20")
        elif ema20 > ema50 and close > ema50:
            scores["trend"] = 70.0
            reasoning.append("Bullish Trend: EMA 20 > 50 and Price > EMA 50")
        elif ema20 < ema50 < ema200:
            scores["trend"] = 0.0
            reasoning.append("Bearish Trend Structure")
        else:
            scores["trend"] = 40.0
            reasoning.append("Neutral/Mixed Trend Structure")

        # 2. Momentum Analysis (20% Weight)
        momentum_score = 0.0
        if rsi > 50 and macd > macd_sig:
            momentum_score = 100.0
            reasoning.append(f"Bullish Momentum: RSI = {rsi:.1f} (>50) & MACD histogram positive")
        elif rsi > 50:
            momentum_score = 60.0
            reasoning.append(f"Moderate Momentum: RSI = {rsi:.1f}")
        else:
            momentum_score = 20.0
            reasoning.append(f"Weak Momentum: RSI = {rsi:.1f}")
        scores["momentum"] = momentum_score

        # 3. Price Action (20% Weight)
        pa_score = 0.0
        curr_open = float(curr["open"])
        if close > curr_open and (close - curr_open) > (float(curr["high"]) - float(curr["low"])) * 0.6:
            pa_score = 100.0
            reasoning.append("Strong Bullish Expansion Candle")
        elif close > prev["close"]:
            pa_score = 70.0
            reasoning.append("Higher Close price action")
        else:
            pa_score = 30.0
            reasoning.append("Bearish/Neutral price candle")
        scores["price_action"] = pa_score

        # 4. Volume Confirmation (10% Weight)
        if vol > vol_sma * 1.5:
            scores["volume"] = 100.0
            reasoning.append(f"Volume Spike: Current volume ({vol:.0f}) > 1.5x average ({vol_sma:.0f})")
        elif vol > vol_sma:
            scores["volume"] = 70.0
            reasoning.append("Above-average trading volume")
        else:
            scores["volume"] = 40.0
            reasoning.append("Below-average trading volume")

        # 5. Volatility Regime (10% Weight)
        if regime in ["TRENDING_BULLISH", "LOW_VOLATILITY"]:
            scores["volatility"] = 90.0
            reasoning.append(f"Optimal Volatility Regime: {regime}")
        elif regime == "HIGH_VOLATILITY":
            scores["volatility"] = 30.0
            reasoning.append("Caution: High Volatility regime detected")
        else:
            scores["volatility"] = 60.0
            reasoning.append(f"Regime: {regime}")

        # 6. Support & Resistance Level (15% Weight)
        sr_score = 50.0
        if resistances:
            nearest_res = min(resistances)
            if close < nearest_res and (nearest_res - close) / close < 0.005:
                sr_score = 10.0
                reasoning.append(f"Caution: Trading directly underneath resistance level (${nearest_res:.2f})")
            elif close > nearest_res:
                sr_score = 100.0
                reasoning.append(f"Breakout above resistance level (${nearest_res:.2f})")
        if supports:
            nearest_sup = max(supports)
            if (close - nearest_sup) / close < 0.01:
                sr_score = 90.0
                reasoning.append(f"Bouncing off strong support level (${nearest_sup:.2f})")
        scores["support_resistance"] = sr_score

        # Weighted Total Confidence Calculation
        total_confidence = (
            (scores["trend"] * 0.25) +
            (scores["momentum"] * 0.20) +
            (scores["price_action"] * 0.20) +
            (scores["volume"] * 0.10) +
            (scores["volatility"] * 0.10) +
            (scores["support_resistance"] * 0.15)
        )

        signal = "HOLD"
        if regime in ["RANGING", "HIGH_VOLATILITY", "UNCLEAR"] and total_confidence < 85.0:
            reasoning.append(f"Market regime '{regime}' requires higher confidence; defaulting to HOLD")
            signal = "HOLD"
        elif total_confidence >= self.min_confidence:
            if not has_open_position and scores["trend"] >= 70.0 and scores["momentum"] >= 60.0:
                signal = "BUY"
            elif has_open_position and (scores["trend"] < 40.0 or rsi < 40.0):
                signal = "SELL"

        return {
            "signal": signal,
            "confidence": round(total_confidence, 2),
            "regime": regime,
            "reasoning": reasoning,
            "detailed_scores": scores
        }
