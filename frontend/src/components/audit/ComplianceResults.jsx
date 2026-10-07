import React from 'react';
import { ClipboardCheck, CheckCircle2, XCircle, AlertCircle, HelpCircle } from 'lucide-react';

export default function ComplianceResults({ compliance }) {
  if (!compliance) return null;

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'compliant':
        return {
          label: 'Compliant',
          color: 'var(--status-success)',
          bgColor: 'var(--status-success-bg)',
          Icon: CheckCircle2
        };
      case 'non_compliant':
        return {
          label: 'Non-Compliant',
          color: 'var(--status-error)',
          bgColor: 'var(--status-error-bg)',
          Icon: XCircle
        };
      case 'partially_compliant':
        return {
          label: 'Partially Compliant',
          color: 'var(--status-warning)',
          bgColor: 'var(--status-warning-bg)',
          Icon: AlertCircle
        };
      default:
        return {
          label: 'Insufficient Evidence',
          color: 'var(--text-secondary)',
          bgColor: 'var(--border-color)',
          Icon: HelpCircle
        };
    }
  };

  const overallBadge = getStatusBadge(compliance.overall_status);
  const OverallIcon = overallBadge.Icon;
  const findingsList = compliance.findings || [];

  return (
    <div className="card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 className="card-title">
          <ClipboardCheck size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Compliance Analysis & Findings</span>
        </h3>
        <div 
          style={{ 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '8px', 
            padding: '6px 14px', 
            borderRadius: '20px', 
            backgroundColor: overallBadge.bgColor,
            color: overallBadge.color,
            fontSize: '0.85rem',
            fontWeight: 700
          }}
        >
          <OverallIcon size={16} />
          <span>OVERALL: {overallBadge.label}</span>
        </div>
      </div>

      <div className="card-body">
        {/* Executive summary statement */}
        {compliance.summary && (
          <div style={{ marginBottom: '24px', backgroundColor: 'var(--bg-primary)', padding: '16px 20px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
            <h4 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>EXECUTIVE SUMMARY RATIONALE</h4>
            <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{compliance.summary}</p>
          </div>
        )}

        {/* Individual Control Findings */}
        <h4 style={{ margin: '0 0 16px 0', fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
          Detailed Control Findings ({findingsList.length})
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {findingsList.length === 0 ? (
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '24px', textAlign: 'center', border: '1px dashed var(--border-color)', borderRadius: '6px' }}>
              No control findings compiled.
            </div>
          ) : (
            findingsList.map((finding) => {
              const badge = getStatusBadge(finding.status);
              const BadgeIcon = badge.Icon;
              return (
                <div 
                  key={finding.finding_id}
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
                      Control: {finding.control}
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

                  {/* Finding Body */}
                  <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {/* Requirements comparison */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>COMPANY REQUIREMENT</div>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{finding.company_requirement || 'Not declared.'}</p>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>REGULATORY COMPLIANCE TARGET</div>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{finding.regulatory_requirement || 'Not declared.'}</p>
                      </div>
                    </div>

                    {/* Reasoning */}
                    <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '6px' }}>COMPLIANCE REASONING</div>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{finding.reasoning}</p>
                    </div>

                    {/* Citations */}
                    {((finding.evidence_citations && finding.evidence_citations.length > 0) || (finding.evidence && finding.evidence.length > 0)) && (
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>EVIDENCE CITATIONS:</span>
                        {((finding.evidence_citations || []).concat(finding.evidence || [])).map((cite, idx) => {
                          const label = typeof cite === 'string' ? cite : (cite.filename ? `${cite.filename}#Ch${cite.chunk_index}` : (cite.source || 'Evidence'));
                          return (
                            <span 
                              key={idx} 
                              style={{ 
                                fontSize: '0.7rem', 
                                backgroundColor: 'var(--bg-tertiary)', 
                                color: 'var(--text-secondary)', 
                                padding: '2px 8px', 
                                borderRadius: '4px',
                                fontFamily: 'var(--font-mono)'
                              }}
                            >
                              {label}
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
