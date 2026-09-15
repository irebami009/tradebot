import threading
import time
import pandas as pd
from typing import Optional, Dict, Any
from app.services.market_data import CSVMarketDataProvider
from app.engine.decision_engine import DecisionEngine
from app.engine.emergency import EmergencyRiskController
from app.engine.ml_model import MLSignalClassifier
from app.trading.paper_trader import PaperTrader
from app.database import SessionLocal
from app.models.db_models import SignalModel
from app.config import settings

class BotRunner:
    """
    Ultra-fast background trading daemon running at sub-second tick resolution (0.5s interval).
    Evaluates market conditions, executes orders in < 10ms, and updates live state instantly.
    """
    def __init__(self, data_file: str = settings.DATA_FILE):
        self.data_file = data_file
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.current_candle_idx = 0
        self.latest_signal = "HOLD"
        self.latest_confidence = 0.0
        self.market_regime = "UNCLEAR"
        self.last_candle: Optional[Dict[str, Any]] = None
        self.emergency_controller = EmergencyRiskController()
        self.ml_classifier = MLSignalClassifier()
        self.decision_engine = DecisionEngine(min_confidence=settings.MIN_CONFIDENCE_THRESHOLD)

    def start(self):
        if self.is_running:
            return
        if settings.EMERGENCY_STOP:
            print("[BOT RUNNER] Cannot start bot while EMERGENCY_STOP is active.")
            return
        self.is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[BOT RUNNER] Fast-responding background trading bot started.")

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        print("[BOT RUNNER] Fast-responding background trading bot stopped.")

    def _run_loop(self):
        data_provider = CSVMarketDataProvider(self.data_file)
        df = data_provider.fetch_ohlcv(symbol="BTC/USD", limit=1000)

        while not self._stop_event.is_set():
            if settings.EMERGENCY_STOP:
                self.is_running = False
                break

            try:
                if len(df) > 0:
                    if self.current_candle_idx >= len(df):
                        self.current_candle_idx = min(50, len(df) - 1)

                    slice_df = df.iloc[:self.current_candle_idx + 1]
                    latest_row = slice_df.iloc[-1]
                    self.last_candle = {
                        "timestamp": str(latest_row["timestamp"]),
                        "open": float(latest_row["open"]),
                        "high": float(latest_row["high"]),
                        "low": float(latest_row["low"]),
                        "close": float(latest_row["close"]),
                        "volume": float(latest_row["volume"])
                    }

                    db = SessionLocal()
                    try:
                        trader = PaperTrader(db)

                        # 1. Immediate SL/TP trigger check
                        trader.check_sl_tp_triggers(
                            current_high=float(latest_row["high"]),
                            current_low=float(latest_row["low"])
                        )

                        # 2. Fast Decision Engine Evaluation
                        open_pos = trader.get_open_position()
                        eval_res = self.decision_engine.evaluate(slice_df, has_open_position=open_pos is not None)

                        self.latest_signal = eval_res["signal"]
                        self.latest_confidence = eval_res["confidence"]
                        self.market_regime = eval_res["regime"]

                        # 3. Instant Execution
                        if eval_res["signal"] == "BUY" and open_pos is None:
                            trade = trader.open_position("BTC/USD", current_price=float(latest_row["close"]))
                            if trade:
                                sig = SignalModel(
                                    symbol="BTC/USD",
                                    timeframe="1h",
                                    signal_type="BUY",
                                    confidence_score=eval_res["confidence"],
                                    market_regime=eval_res["regime"],
                                    reasoning_summary=" | ".join(eval_res["reasoning"]),
                                    detailed_scores=eval_res["detailed_scores"],
                                    executed=True
                                )
                                db.add(sig)
                                db.commit()
                        elif eval_res["signal"] == "SELL" and open_pos is not None:
                            trade = trader.close_position(open_pos.id, exit_price=float(latest_row["close"]), reason="DECISION_SIGNAL")
                            if trade:
                                sig = SignalModel(
                                    symbol="BTC/USD",
                                    timeframe="1h",
                                    signal_type="SELL",
                                    confidence_score=eval_res["confidence"],
                                    market_regime=eval_res["regime"],
                                    reasoning_summary=" | ".join(eval_res["reasoning"]),
                                    detailed_scores=eval_res["detailed_scores"],
                                    executed=True
                                )
                                db.add(sig)
                                db.commit()

                    finally:
                        db.close()

                    self.current_candle_idx = (self.current_candle_idx + 1) % len(df)

            except Exception as e:
                print(f"[FAST BOT RUNNER ERROR] {e}")

            time.sleep(0.5)  # Fast 0.5s sub-second tick loop

bot_runner_instance = BotRunner()
