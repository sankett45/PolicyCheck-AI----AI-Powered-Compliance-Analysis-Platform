import React from 'react';
import { UserCheck, ShieldAlert, CheckCircle2, XOctagon } from 'lucide-react';

export default function HumanReviewDetails({ humanReview }) {
  if (!humanReview) return null;

  const getStatusBadge = (decision) => {
    switch (decision?.toLowerCase()) {
      case 'approve':
      case 'approved':
        return { label: 'APPROVED', color: 'var(--status-success)', bgColor: 'var(--status-success-bg)', Icon: CheckCircle2 };
      case 'reject':
      case 'rejected':
        return { label: 'REJECTED', color: 'var(--status-error)', bgColor: 'var(--status-error-bg)', Icon: XOctagon };
      default:
        return { label: 'ADDITIONAL EVIDENCE REQUIRED', color: 'var(--status-warning)', bgColor: 'var(--status-warning-bg)', Icon: ShieldAlert };
    }
  };

  const badge = getStatusBadge(humanReview.reviewer_decision || humanReview.review_status);
  const BadgeIcon = badge.Icon;

  const formatDate = (isoString) => {
    try {
      if (!isoString) return 'N/A';
      return new Date(isoString).toLocaleString('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
    } catch (e) {
      return isoString;
    }
  };

  return (
    <div className="card" style={{ borderTop: `4px solid ${badge.color}`, marginBottom: '24px' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 className="card-title">
          <UserCheck size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Human-in-the-Loop Review Trail</span>
        </h3>
        
        <div 
          style={{ 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '6px', 
            padding: '4px 12px', 
            borderRadius: '12px', 
            backgroundColor: badge.bgColor,
            color: badge.color,
            fontSize: '0.75rem',
            fontWeight: 700
          }}
        >
          <BadgeIcon size={12} />
          <span>DECISION: {badge.label}</span>
        </div>
      </div>

      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Comment */}
        <div style={{ backgroundColor: 'var(--bg-primary)', padding: '16px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
            REVIEWER COMMENT / JUSTIFICATION
          </span>
          <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.5, fontStyle: 'italic' }}>
            "{humanReview.reviewer_comment || 'No explanation comments provided.'}"
          </p>
        </div>

        {/* Timestamp */}
        {humanReview.timestamp && (
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <strong>Action Recorded:</strong> {formatDate(humanReview.timestamp)}
          </div>
        )}
      </div>
    </div>
  );
}
