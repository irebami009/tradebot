import React from 'react';
import { Play, Square, AlertOctagon, RefreshCw } from 'lucide-react';

export default function Header({ status, onStart, onStop, onEmergencyTrigger, onOpenBacktest, onRefresh }) {
  const isRunning = status?.is_running;
  const isLive = status?.mode === "LIVE";
  const isEmergency = status?.emergency_stop;

  return (
    <header className="header">
      <div className="header-brand">
        <div className="brand-icon">⚡</div>
        <div className="header-title">
          <h1>Apex Automated Trading System</h1>
          <p>Institutional Multi-Factor Scored Engine</p>
        </div>
      </div>

      <div className="header-actions">
        <div className={`status-badge ${isLive ? 'stopped' : 'running'}`} style={{ fontWeight: 700 }}>
          {isLive ? '🔴 LIVE TRADING' : '🟡 PAPER SIMULATION'}
        </div>

        <div className={`status-badge ${isEmergency ? 'stopped' : isRunning ? 'running' : 'stopped'}`}>
          <span className="status-dot"></span>
          {isEmergency ? 'EMERGENCY KILLED' : isRunning ? 'BOT RUNNING' : 'BOT STOPPED'}
        </div>

        {isRunning ? (
          <button className="btn btn-danger" onClick={onStop}>
            <Square size={16} /> Stop Bot
          </button>
        ) : (
          <button className="btn btn-primary" onClick={onStart} disabled={isEmergency}>
            <Play size={16} /> Start Bot
          </button>
        )}

        <button
          className="btn"
          style={{ backgroundColor: '#dc2626', color: 'white' }}
          onClick={onEmergencyTrigger}
          title="Emergency Stop Switch"
        >
          <AlertOctagon size={16} /> KILL SWITCH
        </button>

        <button className="btn btn-outline" onClick={onOpenBacktest}>
          Run Backtest
        </button>

        <button className="btn btn-outline" onClick={onRefresh} title="Refresh data">
          <RefreshCw size={16} />
        </button>
      </div>
    </header>
  );
}
