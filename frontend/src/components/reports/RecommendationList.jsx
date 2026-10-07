import React from 'react';
import { Lightbulb, CheckSquare } from 'lucide-react';

export default function RecommendationList({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h3 className="card-title">
            <Lightbulb size={18} style={{ color: 'var(--accent-gold)' }} />
            <span>Remediation Recommendations</span>
          </h3>
        </div>
        <div className="card-body">
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
            No recommendations recorded.
          </div>
        </div>
      </div>
    );
  }

  const getPriorityBadge = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
      case 'high':
        return { label: priority.toUpperCase(), color: 'var(--status-error)', bgColor: 'var(--status-error-bg)' };
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
          <Lightbulb size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Remediation Recommendations ({recommendations.length})</span>
        </h3>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {recommendations.map((rec, idx) => {
          const badge = getPriorityBadge(rec.priority);
          const fid = rec.finding_id || `finding_${idx}`;

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
                gap: '14px'
              }}
            >
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  Control Area: {rec.control}
                </span>
                
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <a 
                    href={`#finding-${fid}`} 
                    style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-gold)', textDecoration: 'underline' }}
                  >
                    {fid}
                  </a>
                  <div 
                    style={{ 
                      fontSize: '0.75rem', 
                      fontWeight: 700, 
                      color: badge.color, 
                      backgroundColor: badge.bgColor, 
                      padding: '4px 10px', 
                      borderRadius: '12px' 
                    }}
                  >
                    PRIORITY: {badge.label}
                  </div>
                </div>
              </div>

              {/* Action */}
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>RECOMMENDED ACTION</div>
                <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-primary)', lineHeight: 1.5, fontWeight: 500 }}>
                  {rec.recommendation}
                </p>
              </div>

              {/* Rationale */}
              {rec.rationale && (
                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>RECOMMENDATION RATIONALE</div>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    {rec.rationale}
                  </p>
                </div>
              )}

              {/* Implementation steps checklist */}
              {rec.implementation_steps && rec.implementation_steps.length > 0 && (
                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px' }}>IMPLEMENTATION CHECKLIST</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {rec.implementation_steps.map((step, sIdx) => (
                      <div key={sIdx} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                        <CheckSquare size={14} style={{ color: 'var(--accent-gold)', marginTop: '3px', flexShrink: 0 }} />
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          {step}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Source docs */}
              {rec.evidence && rec.evidence.length > 0 && (
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>SOURCE REFERENCES:</span>
                  {rec.evidence.map((ev, evIdx) => (
                    <span 
                      key={evIdx} 
                      style={{ 
                        fontSize: '0.7rem', 
                        backgroundColor: 'var(--bg-tertiary)', 
                        color: 'var(--text-secondary)', 
                        padding: '2px 8px', 
                        borderRadius: '4px',
                        fontFamily: 'var(--font-mono)'
                      }}
                    >
                      {ev}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
