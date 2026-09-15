import React from 'react';

export default function PositionCard({ position }) {
  if (!position) {
    return (
      <div className="card">
        <div className="card-title">Active Simulated Position</div>
        <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No active open positions. Watching market for BUY signals...
        </div>
      </div>
    );
  }

  const isProfit = position.unrealized_pnl >= 0;

  return (
    <div className="card">
      <div className="card-title">
        <span>Active Position: {position.symbol}</span>
        <span className="signal-badge BUY">LONG</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '12px' }}>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Entry Price</div>
          <div style={{ fontSize: '18px', fontWeight: 700 }}>${position.entry_price.toLocaleString()}</div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Current Price</div>
          <div style={{ fontSize: '18px', fontWeight: 700 }}>${position.current_price.toLocaleString()}</div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Quantity</div>
          <div style={{ fontSize: '15px', fontWeight: 600 }}>{position.quantity} units</div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Unrealized PnL</div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: isProfit ? 'var(--status-green)' : 'var(--status-red)' }}>
            {isProfit ? '+' : ''}${position.unrealized_pnl.toFixed(2)} ({position.unrealized_pnl_percent}%)
          </div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Stop Loss (2%)</div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--status-red)' }}>${position.stop_loss.toLocaleString()}</div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Take Profit (4%)</div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--status-green)' }}>${position.take_profit.toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
}
