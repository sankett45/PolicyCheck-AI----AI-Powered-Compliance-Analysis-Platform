import React from 'react';
import { UserCheck, ShieldAlert, CheckCircle2, XCircle, HelpCircle } from 'lucide-react';

export default function ReviewHeader({ reviewId, question, status, riskLevel, riskScore }) {
  const getStatusDetails = (currentStatus) => {
    switch (currentStatus?.toLowerCase()) {
      case 'approved':
        return { label: 'Approved', color: 'var(--status-success)', bgColor: 'var(--status-success-bg)', Icon: CheckCircle2 };
      case 'rejected':
        return { label: 'Rejected', color: 'var(--status-error)', bgColor: 'var(--status-error-bg)', Icon: XCircle };
      case 'needs_more_evidence':
        return { label: 'Additional Evidence Required', color: 'var(--status-warning)', bgColor: 'var(--status-warning-bg)', Icon: ShieldAlert };
      default:
        return { label: 'Pending Human Review', color: 'var(--accent-gold)', bgColor: 'var(--accent-gold-alpha)', Icon: UserCheck };
    }
  };

  const statusDetails = getStatusDetails(status);
  const StatusIcon = statusDetails.Icon;

  return (
    <div className="card" style={{ borderLeft: `4px solid ${statusDetails.color}`, marginBottom: '24px' }}>
      <div className="card-body" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
              HUMAN REVIEW REQUEST ID
            </div>
            <div style={{ fontSize: '0.9rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {reviewId}
            </div>
          </div>
          
          {/* Status Badge */}
          <div 
            style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '8px', 
              padding: '6px 14px', 
              borderRadius: '20px', 
              backgroundColor: statusDetails.bgColor,
              color: statusDetails.color,
              fontSize: '0.85rem',
              fontWeight: 700
            }}
          >
            <StatusIcon size={16} />
            <span>{statusDetails.label}</span>
          </div>
        </div>

        {/* Question */}
        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
            AUDITED COMPLIANCE QUERY
          </div>
          <p style={{ margin: 0, fontSize: '1.1rem', fontWeight: 500, color: 'var(--text-primary)', wordBreak: 'break-word', lineHeight: 1.5 }}>
            "{question}"
          </p>
        </div>
      </div>
    </div>
  );
}
