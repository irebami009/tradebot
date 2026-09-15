import React from 'react';

export default function TradesTable({ trades }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="card">
        <div className="card-title">Recent Trade History</div>
        <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No recorded trades yet.
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-title">Recent Trade History</div>
      <div className="trades-table-container">
        <table className="trades-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Entry Price</th>
              <th>Exit Price</th>
              <th>Quantity</th>
              <th>PnL ($)</th>
              <th>PnL (%)</th>
              <th>Fees</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t) => {
              const isProfit = (t.profit_loss || 0) >= 0;
              return (
                <tr key={t.id}>
                  <td>#{t.id}</td>
                  <td><strong>{t.symbol}</strong></td>
                  <td><span className="signal-badge BUY">{t.side}</span></td>
                  <td>${t.entry_price ? t.entry_price.toFixed(2) : '-'}</td>
                  <td>${t.exit_price ? t.exit_price.toFixed(2) : '-'}</td>
                  <td>{t.quantity}</td>
                  <td style={{ fontWeight: 700, color: isProfit ? 'var(--status-green)' : 'var(--status-red)' }}>
                    {t.profit_loss !== null ? `${isProfit ? '+' : ''}$${t.profit_loss.toFixed(2)}` : '-'}
                  </td>
                  <td style={{ fontWeight: 600, color: isProfit ? 'var(--status-green)' : 'var(--status-red)' }}>
                    {t.profit_loss_percentage !== null ? `${isProfit ? '+' : ''}${t.profit_loss_percentage.toFixed(2)}%` : '-'}
                  </td>
                  <td>${t.fees.toFixed(4)}</td>
                  <td>
                    <span className={`status-badge ${t.status === 'OPEN' ? 'running' : 'stopped'}`}>
                      {t.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
