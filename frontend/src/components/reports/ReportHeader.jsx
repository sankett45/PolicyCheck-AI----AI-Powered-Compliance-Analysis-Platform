import React from 'react';
import { FileText, ShieldAlert, CheckCircle2, UserCheck, Calendar } from 'lucide-react';

export default function ReportHeader({ reportId, auditId, status, version, generatedAt, auditType, subject, regulation }) {
  const getStatusBadge = (reportStatus) => {
    switch (reportStatus?.toLowerCase()) {
      case 'final':
        return { label: 'FINAL REPORT', color: 'var(--status-success)', bgColor: 'var(--status-success-bg)', Icon: CheckCircle2 };
      case 'rejected':
        return { label: 'AUDIT REJECTED', color: 'var(--status-error)', bgColor: 'var(--status-error-bg)', Icon: ShieldAlert };
      case 'pending_review':
        return { label: 'PENDING HUMAN REVIEW', color: 'var(--accent-gold)', bgColor: 'var(--accent-gold-alpha)', Icon: UserCheck };
      default:
        return { label: 'REPORT DRAFT', color: 'var(--text-secondary)', bgColor: 'var(--bg-tertiary)', Icon: FileText };
    }
  };

  const badge = getStatusBadge(status);
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
    <div className="card" style={{ borderLeft: `4px solid ${badge.color}`, marginBottom: '24px' }}>
      <div className="card-body" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        
        {/* Row 1: Header Titles & Status */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px', flexWrap: 'wrap' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              COMPLIANCE AUDIT REPORT
            </h2>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Calendar size={12} />
              <span>Generated: {formatDate(generatedAt)}</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-secondary)', padding: '4px 10px', borderRadius: '12px', fontWeight: 600 }}>
              Version {version || 1}
            </span>
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
              <span>{badge.label}</span>
            </div>
          </div>
        </div>

        {/* Row 2: UUID Details */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block' }}>REPORT ID</span>
            <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>{reportId}</span>
          </div>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block' }}>THREAD AUDIT ID</span>
            <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>{auditId}</span>
          </div>
        </div>

        {/* Row 3: Categorizations */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block' }}>AUDIT CLASSIFICATION</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{auditType?.replace(/_/g, ' ').toUpperCase() || 'GENERAL'}</span>
          </div>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block' }}>SUBJECT CONTROL AREA</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{subject?.replace(/_/g, ' ').toUpperCase() || 'GENERAL'}</span>
          </div>
          <div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block' }}>TARGET COMPLIANCE REGULATION</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--accent-gold)', fontWeight: 600 }}>{regulation || 'GENERAL'}</span>
          </div>
        </div>

      </div>
    </div>
  );
}
