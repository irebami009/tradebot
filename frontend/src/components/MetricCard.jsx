import React from 'react';

export default function MetricCard({ label, value, subtext, change, changeType, badge }) {
  return (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">
        {value}
        {change !== undefined && (
          <span className={`metric-change ${changeType || (change >= 0 ? 'positive' : 'negative')}`}>
            {change >= 0 ? `+${change}%` : `${change}%`}
          </span>
        )}
        {badge && <span className={`signal-badge ${badge}`}>{badge}</span>}
      </div>
      {subtext && <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>{subtext}</div>}
    </div>
  );
}
