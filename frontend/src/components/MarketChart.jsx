import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

export default function MarketChart({ candles }) {
  if (!candles || candles.length === 0) {
    return <div className="card">Loading market chart data...</div>;
  }

  // Format timestamp for display
  const chartData = candles.map(c => ({
    ...c,
    timeLabel: c.timestamp ? c.timestamp.split(' ')[1] || c.timestamp : ''
  }));

  return (
    <div className="card">
      <div className="card-title">
        <span>BTC/USD Price & Technical Indicators</span>
        <span style={{ fontSize: '12px', fontWeight: 400, color: 'var(--text-secondary)' }}>
          EMA 9 (Blue) | EMA 21 (Orange) | RSI 14
        </span>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="timeLabel" stroke="#94a3b8" fontSize={11} />
            <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `$${v}`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
              formatter={(value, name) => [`$${Number(value).toFixed(2)}`, name]}
            />
            <Legend verticalAlign="top" height={36} />
            <Line type="monotone" dataKey="close" stroke="#0f172a" strokeWidth={2} dot={false} name="Close Price" />
            <Line type="monotone" dataKey="ema_fast" stroke="#2563eb" strokeWidth={1.5} dot={false} name="EMA 9" />
            <Line type="monotone" dataKey="ema_slow" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="EMA 21" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="indicator-chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="timeLabel" hide />
            <YAxis domain={[0, 100]} ticks={[30, 50, 70]} stroke="#94a3b8" fontSize={10} />
            <Tooltip formatter={(val) => [val, "RSI (14)"]} />
            <Line type="monotone" dataKey="rsi" stroke="#8b5cf6" strokeWidth={1.5} dot={false} name="RSI 14" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
