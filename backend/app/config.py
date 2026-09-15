import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Execution Mode: BACKTEST, PAPER, LIVE
    MODE: Literal["BACKTEST", "PAPER", "LIVE"] = "PAPER"
    EMERGENCY_STOP: bool = False
    
    # Financial Risk Parameters
    STARTING_BALANCE: float = 10000.0
    RISK_PER_TRADE: float = 0.01          # 1% risk per trade
    MAX_DAILY_LOSS: float = 0.03          # 3% max daily loss
    MAX_PORTFOLIO_EXPOSURE: float = 0.20   # 20% max total portfolio exposure
    MAX_OPEN_POSITIONS: int = 3
    MAX_CONSECUTIVE_LOSSES: int = 5
    MIN_RISK_REWARD_RATIO: float = 2.0    # Minimum 1:2.0 Risk/Reward
    DEFAULT_STOP_LOSS_PCT: float = 0.02
    DEFAULT_TAKE_PROFIT_PCT: float = 0.04
    TRAILING_STOP_ACTIVATION_PCT: float = 0.02
    TRAILING_STOP_STEP_PCT: float = 0.01

    # Strategy Confidence Threshold
    MIN_CONFIDENCE_THRESHOLD: float = 75.0 # 75% minimum confidence score

    # Fee & Slippage Simulation
    TRADING_FEE_PERCENT: float = 0.001     # 0.1% fee
    SLIPPAGE_PERCENT: float = 0.0005       # 0.05% slippage

    # Technical Indicators Parameters
    EMA_FAST: int = 20
    EMA_MEDIUM: int = 50
    EMA_SLOW: int = 200
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: float = 70.0
    RSI_OVERSOLD: float = 30.0
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    ATR_PERIOD: int = 14
    BOLLINGER_PERIOD: int = 20
    BOLLINGER_STD: float = 2.0

    # Exchange / Broker API Credentials (Never hardcoded)
    EXCHANGE_NAME: str = "paper"           # paper, ccxt, mt5
    EXCHANGE_API_KEY: str = ""
    EXCHANGE_SECRET_KEY: str = ""
    EXCHANGE_PASSPHRASE: str = ""
    EXCHANGE_TESTNET: bool = True

    # Database & Data Paths
    DATABASE_URL: str = "sqlite:///./paper_trading.db"
    DATA_FILE: str = os.getenv("DATA_FILE", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_btc_usd.csv")))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
