import React from 'react';
import { Gauge, CheckCircle2 } from 'lucide-react';

export default function ConfidenceIndicator({ confidence, level, title }) {
  if (confidence === undefined || confidence === null) return null;

  const scorePercent = (confidence * 100).toFixed(0) + '%';

  const getGaugeColor = (val) => {
    if (val >= 0.75) return 'var(--status-success)';
    if (val >= 0.5) return 'var(--status-warning)';
    return 'var(--status-error)';
  };

  const getGaugeBg = (val) => {
    if (val >= 0.75) return 'var(--status-success-bg)';
    if (val >= 0.5) return 'var(--status-warning-bg)';
    return 'var(--status-error-bg)';
  };

  const color = getGaugeColor(confidence);
  const bgColor = getGaugeBg(confidence);

  return (
    <section 
      className="stat-card"
      style={{
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px'
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <span className="stat-card-desc" style={{ textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
          {title || 'Confidence Score'}
        </span>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span className="stat-card-value">{scorePercent}</span>
          {level && (
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color }}>
              ({level})
            </span>
          )}
        </div>
      </div>

      <div 
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '42px',
          height: '42px',
          borderRadius: '50%',
          backgroundColor: bgColor,
          color: color
        }}
      >
        <Gauge size={20} />
      </div>
    </section>
  );
}
