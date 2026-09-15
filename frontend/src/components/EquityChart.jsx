import React, { memo } from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const EquityChart = memo(function EquityChart({ equityCurve }) {
  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="card">
        <div className="card-title">Portfolio Equity Curve</div>
        <div style={{ padding: '30px 0', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '13px' }}>
          No performance curve generated yet. Click "Run Backtest".
        </div>
      </div>
    );
  }

  const data = equityCurve.map(pt => ({
    ...pt,
    timeLabel: pt.timestamp ? pt.timestamp.split(' ')[1] || pt.timestamp : ''
  }));

  return (
    <div className="card">
      <div className="card-title">Portfolio Equity Curve</div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="timeLabel" stroke="#94a3b8" fontSize={10} />
            <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={10} tickFormatter={(v) => `$${v}`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
              formatter={(val) => [`$${Number(val).toFixed(2)}`, "Equity"]}
            />
            <Area type="monotone" dataKey="balance" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#equityGrad)" isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
});

export default EquityChart;
