import React from 'react';
import { ClipboardCheck, CheckCircle2, XCircle, AlertCircle, HelpCircle } from 'lucide-react';

export default function FindingsTable({ findings }) {
  if (!findings || findings.length === 0) {
    return (
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h3 className="card-title">
            <ClipboardCheck size={18} style={{ color: 'var(--accent-gold)' }} />
            <span>Compliance Gaps & Findings</span>
          </h3>
        </div>
        <div className="card-body">
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
            No findings recorded.
          </div>
        </div>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'compliant':
        return { label: 'Compliant', color: 'var(--status-success)', bgColor: 'var(--status-success-bg)', Icon: CheckCircle2 };
      case 'non_compliant':
        return { label: 'Non-Compliant', color: 'var(--status-error)', bgColor: 'var(--status-error-bg)', Icon: XCircle };
      case 'partially_compliant':
        return { label: 'Partially Compliant', color: 'var(--status-warning)', bgColor: 'var(--status-warning-bg)', Icon: AlertCircle };
      default:
        return { label: 'Insufficient Evidence', color: 'var(--text-secondary)', bgColor: 'var(--border-color)', Icon: HelpCircle };
    }
  };

  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <div className="card-header">
        <h3 className="card-title">
          <ClipboardCheck size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Compliance Gaps & Findings ({findings.length})</span>
        </h3>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {findings.map((finding, idx) => {
          const badge = getStatusBadge(finding.status);
          const BadgeIcon = badge.Icon;
          const fid = finding.finding_id || `finding_${idx}`;

          return (
            <div 
              key={fid}
              id={`finding-${fid}`}
              style={{
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                overflow: 'hidden'
              }}
            >
              {/* Finding Header */}
              <div 
                style={{ 
                  padding: '14px 20px', 
                  backgroundColor: 'var(--bg-tertiary)', 
                  borderBottom: '1px solid var(--border-color)', 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center' 
                }}
              >
                <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  Finding {idx + 1}: {finding.control}
                </span>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    {fid}
                  </span>
                  <div 
                    style={{ 
                      display: 'inline-flex', 
                      alignItems: 'center', 
                      gap: '6px', 
                      padding: '4px 10px', 
                      borderRadius: '12px', 
                      backgroundColor: badge.bgColor,
                      color: badge.color,
                      fontSize: '0.75rem',
                      fontWeight: 700
                    }}
                  >
                    <BadgeIcon size={12} />
                    <span>{badge.label}</span>
                  </div>
                </div>
              </div>

              {/* Finding Body */}
              <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>COMPANY REQUIREMENT</div>
                    <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {finding.company_requirement}
                    </p>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>REGULATORY COMPLIANCE TARGET</div>
                    <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {finding.regulatory_requirement}
                    </p>
                  </div>
                </div>

                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '6px' }}>COMPLIANCE REASONING</div>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    {finding.reasoning}
                  </p>
                </div>

                {finding.evidence_citations && finding.evidence_citations.length > 0 && (
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>EVIDENCE CITATIONS:</span>
                    {finding.evidence_citations.map((cite, cIdx) => (
                      <span 
                        key={cIdx} 
                        style={{ 
                          fontSize: '0.7rem', 
                          backgroundColor: 'var(--bg-tertiary)', 
                          color: 'var(--text-secondary)', 
                          padding: '2px 8px', 
                          borderRadius: '4px',
                          fontFamily: 'var(--font-mono)'
                        }}
                      >
                        {cite}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
