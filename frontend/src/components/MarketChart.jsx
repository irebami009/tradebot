import React, { memo } from 'react';
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

const MarketChart = memo(function MarketChart({ candles }) {
  if (!candles || candles.length === 0) {
    return <div className="card">Loading market chart data...</div>;
  }

  const chartData = candles.map(c => ({
    ...c,
    timeLabel: c.timestamp ? c.timestamp.split(' ')[1] || c.timestamp : ''
  }));

  return (
    <div className="card">
      <div className="card-title">
        <span>BTC/USD Price & Technical Indicators</span>
        <span style={{ fontSize: '11px', fontWeight: 400, color: 'var(--text-secondary)' }}>
          EMA 20 (Blue) | EMA 50 (Orange) | EMA 200 (Slate) | RSI 14
        </span>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="timeLabel" stroke="#94a3b8" fontSize={10} />
            <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={10} tickFormatter={(v) => `$${v}`} />
            <Tooltip
              contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
              formatter={(value, name) => [`$${Number(value).toFixed(2)}`, name]}
            />
            <Legend verticalAlign="top" height={30} wrapperStyle={{ fontSize: '11px' }} />
            <Line type="monotone" dataKey="close" stroke="#0f172a" strokeWidth={2} dot={false} name="Close Price" isAnimationActive={false} />
            <Line type="monotone" dataKey="ema_20" stroke="#2563eb" strokeWidth={1.5} dot={false} name="EMA 20" isAnimationActive={false} />
            <Line type="monotone" dataKey="ema_50" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="EMA 50" isAnimationActive={false} />
            <Line type="monotone" dataKey="ema_200" stroke="#64748b" strokeWidth={1.5} dot={false} name="EMA 200" isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="indicator-chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="timeLabel" hide />
            <YAxis domain={[0, 100]} ticks={[30, 50, 70]} stroke="#94a3b8" fontSize={9} />
            <Tooltip formatter={(val) => [val, "RSI (14)"]} />
            <Line type="monotone" dataKey="rsi" stroke="#8b5cf6" strokeWidth={1.5} dot={false} name="RSI 14" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
});

export default MarketChart;
