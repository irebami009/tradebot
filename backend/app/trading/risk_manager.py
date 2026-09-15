from typing import Tuple, Optional

class RiskManager:
    def __init__(
        self,
        risk_per_trade: float = 0.01,
        stop_loss_percent: float = 0.02,
        take_profit_percent: float = 0.04,
        max_daily_loss: float = 0.05,
        max_positions: int = 1
    ):
        self.risk_per_trade = risk_per_trade
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.max_daily_loss = max_daily_loss
        self.max_positions = max_positions

    def is_trade_allowed(
        self,
        current_open_positions: int,
        daily_starting_balance: float,
        current_balance: float
    ) -> Tuple[bool, str]:
        """
        Validates whether a new trade can be opened based on position count & daily drawdown limits.
        """
        if current_open_positions >= self.max_positions:
            return False, f"Maximum open positions limit reached ({self.max_positions})"

        # Check maximum daily loss limit
        if daily_starting_balance > 0:
            daily_loss_pct = (daily_starting_balance - current_balance) / daily_starting_balance
            if daily_loss_pct >= self.max_daily_loss:
                return False, f"Maximum daily loss reached ({daily_loss_pct*100:.2f}% >= {self.max_daily_loss*100:.2f}%)"

        return True, "Trade allowed"

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float
    ) -> Tuple[float, float, float]:
        """
        Calculates position quantity, stop loss price, and take profit price.
        
        Formula:
        risk_amount = balance * risk_per_trade
        stop_loss_dist = entry_price * stop_loss_percent
        quantity = risk_amount / stop_loss_dist
        Capped by available balance.
        """
        if account_balance <= 0 or entry_price <= 0:
            return 0.0, 0.0, 0.0

        risk_amount = account_balance * self.risk_per_trade
        stop_loss_dist = entry_price * self.stop_loss_percent
        
        stop_loss_price = entry_price * (1.0 - self.stop_loss_percent)
        take_profit_price = entry_price * (1.0 + self.take_profit_percent)

        if stop_loss_dist <= 0:
            return 0.0, stop_loss_price, take_profit_price

        # Quantity based on risk
        quantity = risk_amount / stop_loss_dist

        # Cap quantity to maximum affordable position size
        max_affordable_quantity = account_balance / entry_price
        if quantity > max_affordable_quantity:
            quantity = max_affordable_quantity

        return round(quantity, 8), round(stop_loss_price, 2), round(take_profit_price, 2)
