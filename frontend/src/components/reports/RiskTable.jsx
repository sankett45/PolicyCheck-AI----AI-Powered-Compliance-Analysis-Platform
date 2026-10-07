import React from 'react';
import { ShieldAlert, AlertTriangle } from 'lucide-react';

export default function RiskTable({ riskAssessments }) {
  if (!riskAssessments || riskAssessments.length === 0) {
    return (
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h3 className="card-title">
            <ShieldAlert size={18} style={{ color: 'var(--accent-gold)' }} />
            <span>Detailed Vulnerability Assessments</span>
          </h3>
        </div>
        <div className="card-body">
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
            No vulnerability assessments recorded.
          </div>
        </div>
      </div>
    );
  }

  const getRiskDetails = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical':
      case 'high':
        return { label: level.toUpperCase(), color: 'var(--status-error)', bgColor: 'var(--status-error-bg)' };
      case 'medium':
        return { label: 'MEDIUM', color: 'var(--status-warning)', bgColor: 'var(--status-warning-bg)' };
      default:
        return { label: 'LOW', color: 'var(--status-success)', bgColor: 'var(--status-success-bg)' };
    }
  };

  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <div className="card-header">
        <h3 className="card-title">
          <ShieldAlert size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Detailed Vulnerability Assessments ({riskAssessments.length})</span>
        </h3>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {riskAssessments.map((r, idx) => {
          const details = getRiskDetails(r.risk_level);
          const fid = r.finding_id || `finding_${idx}`;

          return (
            <div 
              key={`${fid}-${idx}`}
              style={{
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                  Control Area: {r.control}
                </span>
                
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <a 
                    href={`#finding-${fid}`} 
                    style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-gold)', textDecoration: 'underline' }}
                  >
                    {fid}
                  </a>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: details.color, backgroundColor: details.bgColor, padding: '2px 8px', borderRadius: '4px' }}>
                    Score: {r.risk_score} ({details.label})
                  </span>
                </div>
              </div>

              {/* Scorecard grid */}
              <div 
                style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(3, 1fr)', 
                  gap: '12px', 
                  padding: '12px', 
                  backgroundColor: 'var(--bg-tertiary)', 
                  borderRadius: '6px', 
                  textAlign: 'center',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>SEVERITY</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{r.severity}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>LIKELIHOOD</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{r.likelihood}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>IMPACT LEVEL</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{r.impact}</div>
                </div>
              </div>

              {/* Rationale */}
              {r.rationale && (
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, borderTop: '1px solid var(--border-color)', paddingTop: '10px' }}>
                  <strong>Risk Rationale:</strong> {r.rationale}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
