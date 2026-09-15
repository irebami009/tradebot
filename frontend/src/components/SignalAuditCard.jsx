import React from 'react';
import { Cpu, CheckCircle, AlertTriangle } from 'lucide-react';

export default function SignalAuditCard({ status, signals }) {
  const latestSig = signals && signals.length > 0 ? signals[0] : null;
  const confidence = status?.latest_confidence || (latestSig ? latestSig.confidence_score : 0.0);
  const regime = status?.market_regime || (latestSig ? latestSig.market_regime : "UNCLEAR");
  const reasons = latestSig?.reasoning_summary ? latestSig.reasoning_summary.split(' | ') : [];

  return (
    <div className="card">
      <div className="card-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Cpu size={18} color="var(--accent-blue)" /> Multi-Factor Decision Audit ("WHY")
        </span>
        <span className={`signal-badge ${status?.latest_signal || "HOLD"}`}>
          {status?.latest_signal || "HOLD"} ({confidence}%)
        </span>
      </div>

      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Market Regime</div>
          <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>{regime}</div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Confidence Score</div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: confidence >= 75 ? 'var(--status-green)' : 'var(--status-amber)' }}>
            {confidence}% / 100%
          </div>
        </div>
      </div>

      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
        Reasoning & Indicator Breakdown:
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
        {reasons.length > 0 ? (
          reasons.map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '13px', color: 'var(--text-primary)' }}>
              <CheckCircle size={14} color="var(--accent-blue)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <span>{r}</span>
            </div>
          ))
        ) : (
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Analyzing market structure, momentum, volatility, and volume...
          </div>
        )}
      </div>
    </div>
  );
}
