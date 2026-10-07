import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

export default function RiskResults({ risk }) {
  if (!risk) return null;

  const getRiskDetails = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical':
        return { label: 'CRITICAL', color: 'var(--status-error)', bgColor: 'var(--status-error-bg)' };
      case 'high':
        return { label: 'HIGH', color: 'var(--status-error)', bgColor: 'var(--status-error-bg)' };
      case 'medium':
        return { label: 'MEDIUM', color: 'var(--status-warning)', bgColor: 'var(--status-warning-bg)' };
      default:
        return { label: 'LOW', color: 'var(--status-success)', bgColor: 'var(--status-success-bg)' };
    }
  };

  const overall = getRiskDetails(risk.overall_risk_level);
  const assessmentsList = risk.assessments || [];

  return (
    <div className="card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 className="card-title">
          <ShieldAlert size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Security Risk Assessment</span>
        </h3>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* Level Pill */}
          <div 
            style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              padding: '6px 14px', 
              borderRadius: '20px', 
              backgroundColor: overall.bgColor,
              color: overall.color,
              fontSize: '0.85rem',
              fontWeight: 700
            }}
          >
            <span>LEVEL: {overall.label}</span>
          </div>
          {/* Score Badge */}
          <div style={{ display: 'inline-flex', alignItems: 'center', padding: '6px 14px', borderRadius: '20px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-color)', fontSize: '0.85rem', fontWeight: 700 }}>
            <span>SCORE: {risk.overall_risk_score}/100</span>
          </div>
        </div>
      </div>

      <div className="card-body">
        <h4 style={{ margin: '0 0 16px 0', fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
          Detailed Finding Vulnerabilities ({assessmentsList.length})
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {assessmentsList.length === 0 ? (
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '24px', textAlign: 'center', border: '1px dashed var(--border-color)', borderRadius: '6px' }}>
              No risk assessments generated.
            </div>
          ) : (
            assessmentsList.map((assess) => {
              const details = getRiskDetails(assess.risk_level);
              return (
                <div 
                  key={assess.finding_id}
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
                      Control: {assess.control}
                    </span>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Vulnerability score:</span>
                      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: details.color, backgroundColor: details.bgColor, padding: '2px 8px', borderRadius: '4px' }}>
                        {assess.risk_score} (Level: {details.label})
                      </span>
                    </div>
                  </div>

                  {/* Impact metrics grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', padding: '12px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '6px', textAlign: 'center' }}>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>SEVERITY</div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{assess.severity}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>LIKELIHOOD</div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{assess.likelihood}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>IMPACT LEVEL</div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{assess.impact}</div>
                    </div>
                  </div>

                  {/* Rationale text */}
                  {assess.rationale && (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      <strong>Risk Rationale:</strong> {assess.rationale}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
