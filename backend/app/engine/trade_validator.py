from typing import Tuple, Optional
from datetime import datetime, timezone
from app.config import settings

class TradeValidator:
    """
    Trade Validation Gatekeeper Engine verifying pre-execution capital preservation rules.
    If ANY single risk condition fails, trade entry is strictly ABORTED (NO TRADE).
    """

    def validate_trade(
        self,
        current_open_positions: int,
        daily_starting_balance: float,
        current_balance: float,
        total_portfolio_exposure: float,
        consecutive_losses: int,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        last_data_timestamp: Optional[datetime] = None
    ) -> Tuple[bool, str]:

        # 1. Emergency Stop Check
        if settings.EMERGENCY_STOP:
            return False, "EMERGENCY_STOP switch active: All new trades prohibited"

        # 2. Account Balance Check
        if current_balance <= 0:
            return False, "Insufficient account equity"

        # 3. Maximum Open Positions Check
        if current_open_positions >= settings.MAX_OPEN_POSITIONS:
            return False, f"Maximum open positions limit reached ({current_open_positions} >= {settings.MAX_OPEN_POSITIONS})"

        # 4. Maximum Daily Loss Check
        if daily_starting_balance > 0:
            daily_loss_pct = (daily_starting_balance - current_balance) / daily_starting_balance
            if daily_loss_pct >= settings.MAX_DAILY_LOSS:
                return False, f"Max daily loss reached ({daily_loss_pct*100:.2f}% >= {settings.MAX_DAILY_LOSS*100:.2f}%)"

        # 5. Maximum Portfolio Exposure Check
        exposure_pct = total_portfolio_exposure / current_balance if current_balance > 0 else 1.0
        if exposure_pct >= settings.MAX_PORTFOLIO_EXPOSURE:
            return False, f"Max portfolio exposure exceeded ({exposure_pct*100:.1f}% >= {settings.MAX_PORTFOLIO_EXPOSURE*100:.1f}%)"

        # 6. Maximum Consecutive Loss Cooldown Check
        if consecutive_losses >= settings.MAX_CONSECUTIVE_LOSSES:
            return False, f"Consecutive loss cooldown active ({consecutive_losses} >= {settings.MAX_CONSECUTIVE_LOSSES})"

        # 7. Stop Loss Distance Check
        sl_dist = abs(entry_price - stop_loss_price)
        tp_dist = abs(take_profit_price - entry_price)
        if sl_dist <= 0:
            return False, "Invalid Stop Loss distance (must be > 0)"

        # 8. Minimum Risk/Reward Ratio Check (Default min 1:2.0)
        rr_ratio = tp_dist / sl_dist
        if rr_ratio < settings.MIN_RISK_REWARD_RATIO:
            return False, f"Risk/Reward ratio insufficient ({rr_ratio:.2f} < {settings.MIN_RISK_REWARD_RATIO:.1f})"

        # 9. Stale Data Freshness Check (< 10 seconds)
        if last_data_timestamp:
            elapsed = (datetime.now(timezone.utc) - last_data_timestamp).total_seconds()
            if elapsed > 10.0:
                return False, f"Market data stale ({elapsed:.1f}s > 10.0s threshold)"

        return True, "All capital preservation checks passed: Trade Approved"
