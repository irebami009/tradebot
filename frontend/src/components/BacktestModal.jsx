import React, { useState } from 'react';
import { X, Play, BarChart2 } from 'lucide-react';
import { runBacktest } from '../services/api';

export default function BacktestModal({ isOpen, onClose, onBacktestComplete }) {
  const [params, setParams] = useState({
    symbol: "BTC/USD",
    starting_balance: 1000.0,
    risk_per_trade: 0.01,
    stop_loss_percent: 0.02,
    take_profit_percent: 0.04,
    ema_fast: 9,
    ema_slow: 21,
    rsi_period: 14
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: parseFloat(value) || value
    }));
  };

  const handleRun = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await runBacktest(params);
      setResults(res);
      if (onBacktestComplete) {
        onBacktestComplete(res);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart2 size={20} color="var(--accent-blue)" /> Historical Backtesting Engine
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleRun}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Starting Balance ($)</label>
              <input type="number" name="starting_balance" className="form-input" value={params.starting_balance} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label className="form-label">Risk Per Trade (%)</label>
              <input type="number" step="0.005" name="risk_per_trade" className="form-input" value={params.risk_per_trade} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label className="form-label">Stop Loss (%)</label>
              <input type="number" step="0.005" name="stop_loss_percent" className="form-input" value={params.stop_loss_percent} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label className="form-label">Take Profit (%)</label>
              <input type="number" step="0.005" name="take_profit_percent" className="form-input" value={params.take_profit_percent} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label className="form-label">Fast EMA Period</label>
              <input type="number" name="ema_fast" className="form-input" value={params.ema_fast} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label className="form-label">Slow EMA Period</label>
              <input type="number" name="ema_slow" className="form-input" value={params.ema_slow} onChange={handleChange} />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '12px', justifyContent: 'center' }} disabled={loading}>
            {loading ? "Simulating Backtest..." : <><Play size={16} /> Run Backtest Simulation</>}
          </button>
        </form>

        {error && <div style={{ color: 'var(--status-red)', marginTop: '12px', fontSize: '13px' }}>Error: {error}</div>}

        {results && (
          <div style={{ marginTop: '20px', backgroundColor: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>Backtest Performance Results</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '13px' }}>
              <div>Total Return: <strong style={{ color: results.total_return_percent >= 0 ? 'var(--status-green)' : 'var(--status-red)' }}>{results.total_return_percent}%</strong></div>
              <div>Ending Balance: <strong>${results.ending_balance}</strong></div>
              <div>Win Rate: <strong>{results.win_rate_percent}%</strong></div>
              <div>Total Trades: <strong>{results.total_trades} ({results.winning_trades}W / {results.losing_trades}L)</strong></div>
              <div>Profit Factor: <strong>{results.profit_factor}</strong></div>
              <div>Max Drawdown: <strong style={{ color: 'var(--status-red)' }}>{results.max_drawdown_percent}%</strong></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
