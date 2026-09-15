# Apex Paper Trading Bot & Backtesting Platform

A modular, production-grade **Python Paper Trading Bot & Backtesting Engine** paired with a fintech **React + Vite Dashboard**.

> [!IMPORTANT]
> **PAPER TRADING ONLY — NO REAL CAPITAL AT RISK**  
> This application is strictly designed for simulation, strategy backtesting, and paper trading. It does **not** connect to real exchange APIs or place live financial orders.

---

## 🏗️ Architecture & Project Structure

```
trading-bot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Pydantic environment configuration
│   │   ├── database.py          # SQLAlchemy SQLite connection manager
│   │   ├── api/                 # REST API Routers
│   │   │   ├── routes.py        # Bot control, balance, backtest endpoints
│   │   │   ├── trades.py        # Trade ledger and open position endpoints
│   │   │   └── market.py        # OHLCV candlestick & indicator endpoints
│   │   ├── strategy/            # Algorithmic Trading Strategies
│   │   │   ├── indicators.py    # Pure Pandas/NumPy EMA & RSI calculators
│   │   │   └── strategy.py      # EMA Crossover + RSI strategy logic
│   │   ├── trading/             # Simulation & Execution Engines
│   │   │   ├── paper_trader.py  # Simulated order execution & fee manager
│   │   │   ├── risk_manager.py  # 1% risk position sizing & daily loss guard
│   │   │   └── backtester.py    # Sequential historical candle playback
│   │   ├── models/              # Schemas & DB Models
│   │   │   ├── schemas.py       # Pydantic request/response validation
│   │   │   └── db_models.py     # SQLAlchemy ORM database tables
│   │   └── services/            # Background Tasks & Data Providers
│   │       ├── market_data.py   # Abstract Base Provider & CSV Data Streamer
│   │       └── bot_runner.py    # Background thread trading loop
│   ├── tests/                   # Pytest automated test suite
│   │   ├── test_indicators.py
│   │   ├── test_strategy.py
│   │   ├── test_risk_manager.py
│   │   ├── test_paper_trader.py
│   │   ├── test_backtester.py
│   │   └── test_api.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # React + Vite Dashboard
│   ├── src/
│   │   ├── components/          # Reusable UI Cards & Recharts
│   │   ├── services/            # API Client functions
│   │   ├── App.jsx              # Main dashboard view
│   │   └── index.css            # Light fintech design system
│   ├── index.html
│   └── package.json
├── data/
│   └── sample_btc_usd.csv       # Sample historical OHLCV data
├── README.md
└── .gitignore
```

---

## 📊 Strategy & Risk Management Rules

### 1. Strategy: EMA Crossover + RSI 14
- **Fast EMA**: 9 periods
- **Slow EMA**: 21 periods
- **RSI**: 14 periods (Wilder's Smoothing)

- **BUY Signal**:
  - EMA 9 crosses **above** EMA 21 (`prev_EMA9 <= prev_EMA21` and `curr_EMA9 > curr_EMA21`)
  - RSI 14 is **above 50**
  - No active open position
- **SELL Signal**:
  - EMA 9 crosses **below** EMA 21 (`prev_EMA9 >= prev_EMA21` and `curr_EMA9 < curr_EMA21`)
  - RSI 14 is **below 50**
  - Position currently open
- **HOLD Signal**: All other market conditions.

### 2. Risk Management Protocol
- **Starting Capital**: $1,000.00
- **Risk Per Trade**: 1% ($10 risk on $1,000 initial balance)
- **Stop Loss**: 2% below entry price
- **Take Profit**: 4% above entry price
- **Position Sizing Formula**:
  $$\text{Risk Amount} = \text{Account Balance} \times 0.01$$
  $$\text{Stop Loss Distance} = \text{Entry Price} \times 0.02$$
  $$\text{Position Quantity} = \frac{\text{Risk Amount}}{\text{Stop Loss Distance}}$$
- **Max Daily Loss Guard**: Halts new trade entries if daily loss exceeds 5%.

---

## 💻 Exact Windows PowerShell Commands

### Step 1: Clone / Navigate to Project Directory
```powershell
cd C:\Users\HP\.gemini\antigravity-ide\scratch\trading-bot
```

### Step 2: Set Up Backend (FastAPI + SQLite)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

### Step 3: Run Backend Server
```powershell
.\venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```
*API Swagger Documentation will be live at:* `http://localhost:8000/docs`

### Step 4: Set Up & Launch React Dashboard (New Terminal Window)
```powershell
cd C:\Users\HP\.gemini\antigravity-ide\scratch\trading-bot\frontend
npm install
npm run dev
```
*React Dashboard will be live at:* `http://localhost:5173`

---

## 🧪 Running Automated Tests

To execute the test suite (15 unit & integration tests):

```powershell
cd C:\Users\HP\.gemini\antigravity-ide\scratch\trading-bot\backend
.\venv\Scripts\pytest -v
```

---

## 🔌 How to Add Live Exchange Integration Later (e.g. Binance / Alpaca / CCXT)

The bot is architected using the **Dependency Inversion Pattern**:

1. In `backend/app/services/market_data.py`, implement a new provider inheriting from `BaseMarketDataProvider`:
   ```python
   class BinanceMarketDataProvider(BaseMarketDataProvider):
       def fetch_ohlcv(self, symbol: str, limit: int = 1000) -> pd.DataFrame:
           # Call Binance REST API / CCXT here
           ...
   ```
2. In `backend/app/trading/paper_trader.py`, replace `PaperTrader` with a `LiveBrokerTrader` that translates `open_position()` and `close_position()` into real API order requests.
