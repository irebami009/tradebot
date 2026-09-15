import React from 'react';
import { ShieldCheck } from 'lucide-react';

export default function RiskSettingsCard() {
  return (
    <div className="card">
      <div className="card-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={18} color="var(--accent-blue)" /> Capital Preservation Gatekeepers
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Risk Per Trade</span>
          <span style={{ fontWeight: 600, color: 'var(--accent-blue)' }}>1.0% ($100 per $10k)</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Max Daily Loss Limit</span>
          <span style={{ fontWeight: 600, color: 'var(--status-red)' }}>3.0% ($300 max loss)</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Max Portfolio Exposure</span>
          <span style={{ fontWeight: 600 }}>20.0% Max Cap</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Min Risk/Reward Ratio</span>
          <span style={{ fontWeight: 600, color: 'var(--status-green)' }}>1 : 2.0 Minimum</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Max Open Positions</span>
          <span style={{ fontWeight: 600 }}>3 Positions</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Consecutive Loss Cooldown</span>
          <span style={{ fontWeight: 600, color: 'var(--status-red)' }}>5 Losses Max</span>
        </div>
      </div>
    </div>
  );
}
