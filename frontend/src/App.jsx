import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricCard from './components/MetricCard';
import MarketChart from './components/MarketChart';
import EquityChart from './components/EquityChart';
import PositionCard from './components/PositionCard';
import TradesTable from './components/TradesTable';
import RiskSettingsCard from './components/RiskSettingsCard';
import SignalAuditCard from './components/SignalAuditCard';
import BacktestModal from './components/BacktestModal';
import {
  fetchStatus,
  fetchBalance,
  fetchPositions,
  fetchTrades,
  fetchSignals,
  fetchMarketData,
  fetchPerformance,
  startBot,
  stopBot,
  triggerEmergencyStop,
  resetEmergencyStop
} from './services/api';

export default function App() {
  const [status, setStatus] = useState(null);
  const [balance, setBalance] = useState(null);
  const [positions, setPositions] = useState([]);
  const [trades, setTrades] = useState([]);
  const [signals, setSignals] = useState([]);
  const [candles, setCandles] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [isBacktestOpen, setIsBacktestOpen] = useState(false);

  const loadData = async () => {
    try {
      const [sData, bData, pData, tData, sigData, mData] = await Promise.all([
        fetchStatus(),
        fetchBalance(),
        fetchPositions(),
        fetchTrades(),
        fetchSignals(),
        fetchMarketData("BTC/USD", 100)
      ]);
      setStatus(sData);
      setBalance(bData);
      setPositions(pData);
      setTrades(tData);
      setSignals(sigData);
      setCandles(mData);
    } catch (err) {
      console.error("Error fetching trading bot data:", err);
    }
  };

  const loadPerformance = async () => {
    try {
      const perf = await fetchPerformance();
      setPerformance(perf);
    } catch (err) {
      console.error("Error fetching performance summary:", err);
    }
  };

  useEffect(() => {
    loadData();
    loadPerformance();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleStartBot = async () => {
    try {
      await startBot();
      loadData();
    } catch (err) {
      alert("Failed to start bot: " + err.message);
    }
  };

  const handleStopBot = async () => {
    try {
      await stopBot();
      loadData();
    } catch (err) {
      alert("Failed to stop bot: " + err.message);
    }
  };

  const handleEmergencyTrigger = async () => {
    if (window.confirm("⚠️ ARE YOU SURE YOU WANT TO TRIGGER EMERGENCY KILL SWITCH? This will immediately halt trading.")) {
      try {
        await triggerEmergencyStop();
        loadData();
      } catch (err) {
        alert("Emergency stop failed: " + err.message);
      }
    }
  };

  const handleEmergencyReset = async () => {
    try {
      await resetEmergencyStop();
      loadData();
    } catch (err) {
      alert("Reset failed: " + err.message);
    }
  };

  const isLive = status?.mode === "LIVE";
  const isEmergency = status?.emergency_stop;
  const currentPrice = candles.length > 0 ? candles[candles.length - 1].close : 50000.0;
  const activePosition = positions.length > 0 ? positions[0] : status?.active_position;

  return (
    <div className="app-container">
      {/* High Visibility Status Banner */}
      <div
        className="warning-banner"
        style={{
          backgroundColor: isEmergency ? '#fee2e2' : isLive ? '#fef2f2' : '#fef3c7',
          color: isEmergency ? '#991b1b' : isLive ? '#991b1b' : '#92400e',
          borderColor: isEmergency ? '#fca5a5' : isLive ? '#fca5a5' : '#fde68a'
        }}
      >
        {isEmergency ? (
          <span style={{ fontWeight: 800 }}>
            🚨 EMERGENCY KILL SWITCH ACTIVATED — ALL TRADING SUSPENDED{' '}
            <button
              onClick={handleEmergencyReset}
              style={{ marginLeft: '12px', padding: '2px 8px', borderRadius: '4px', cursor: 'pointer' }}
            >
              Reset Switch
            </button>
          </span>
        ) : isLive ? (
          <span style={{ fontWeight: 800 }}>🔴 REAL MONEY — LIVE TRADING ACTIVE</span>
        ) : (
          <span>🟡 PAPER TRADING MODE ONLY — SIMULATION EXECUTIONS — NO REAL MONEY AT RISK</span>
        )}
      </div>

      {/* Navigation Header */}
      <Header
        status={status}
        onStart={handleStartBot}
        onStop={handleStopBot}
        onEmergencyTrigger={handleEmergencyTrigger}
        onOpenBacktest={() => setIsBacktestOpen(true)}
        onRefresh={loadData}
      />

      {/* Dashboard Workspace */}
      <main className="dashboard-main">
        {/* KPI Metrics */}
        <div className="metrics-grid">
          <MetricCard
            label="Account Balance"
            value={balance ? `$${balance.virtual_balance.toLocaleString()}` : "$10,000.00"}
            change={balance ? balance.daily_pnl_percent : 0.0}
            subtext={isLive ? "Live Broker Equity" : "Starting Paper: $10,000"}
          />

          <MetricCard
            label="Total Realized P&L"
            value={balance ? `${balance.realized_pnl >= 0 ? '+' : ''}$${balance.realized_pnl.toFixed(2)}` : "$0.00"}
            changeType={balance && balance.realized_pnl >= 0 ? "positive" : "negative"}
            subtext="Closed trade net profit"
          />

          <MetricCard
            label="Current BTC/USD Price"
            value={`$${currentPrice.toLocaleString()}`}
            subtext="1-Hour Candlesticks"
          />

          <MetricCard
            label="Confidence Score"
            value={`${status?.latest_confidence || 0.0}%`}
            badge={status?.latest_signal || "HOLD"}
            subtext={`Regime: ${status?.market_regime || 'UNCLEAR'}`}
          />

          <MetricCard
            label="Backtest Sharpe Ratio"
            value={performance ? `${performance.sharpe_ratio}` : "0.00"}
            subtext={performance ? `Win Rate: ${performance.win_rate_percent}%` : "No backtest"}
          />
        </div>

        {/* Row 1: Price Chart vs Signal Audit & Risk Controls */}
        <div className="dashboard-grid">
          <div>
            <MarketChart candles={candles} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <SignalAuditCard status={status} signals={signals} />
            <RiskSettingsCard />
          </div>
        </div>

        {/* Row 2: Positions & Trade Ledger vs Equity Curve */}
        <div className="dashboard-grid">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <PositionCard position={activePosition} />
            <EquityChart equityCurve={performance?.equity_curve || []} />
          </div>
          <div>
            <TradesTable trades={trades} />
          </div>
        </div>
      </main>

      {/* Backtesting Engine Modal */}
      <BacktestModal
        isOpen={isBacktestOpen}
        onClose={() => setIsBacktestOpen(false)}
        onBacktestComplete={(res) => {
          setPerformance(res);
        }}
      />
    </div>
  );
}
