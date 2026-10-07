import React from 'react';
import { AlertOctagon } from 'lucide-react';

export default function ReviewReason({ reasons }) {
  if (!reasons || reasons.length === 0) return null;

  const mapReasonLabel = (reason) => {
    const labels = {
      low_retrieval_confidence: 'Low Retrieval Confidence',
      low_compliance_confidence: 'Low Compliance Confidence',
      insufficient_evidence: 'Insufficient Evidence Citations',
      high_risk: 'High Posture Risk Scored',
      policy_or_regulation_conflict: 'Policy / Regulation Conflict Detected',
      manual_review_required: 'Manual Policy Review Enforced'
    };
    return labels[reason] || reason?.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div className="card" style={{ border: '1px solid rgba(245, 158, 11, 0.2)', backgroundColor: 'var(--status-warning-bg)', marginBottom: '24px' }}>
      <div className="card-body" style={{ padding: '20px' }}>
        <h4 style={{ margin: '0 0 12px 0', fontSize: '0.9rem', fontWeight: 700, color: 'var(--status-warning)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertOctagon size={16} />
          <span>Confidence Gate Warning Signals</span>
        </h4>
        <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
          The deterministic compliance gate has flagged the automated analysis due to the following criteria matching:
        </p>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {reasons.map((reason) => (
            <span 
              key={reason} 
              style={{ 
                fontSize: '0.75rem', 
                backgroundColor: 'rgba(245, 158, 11, 0.15)', 
                color: 'var(--status-warning)', 
                padding: '4px 12px', 
                borderRadius: '4px',
                fontWeight: 600,
                border: '1px solid rgba(245, 158, 11, 0.2)'
              }}
            >
              {mapReasonLabel(reason)}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
