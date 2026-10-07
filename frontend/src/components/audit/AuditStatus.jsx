import React from 'react';
import { ShieldCheck, AlertTriangle, XOctagon } from 'lucide-react';

export default function AuditStatus({ status, reasons }) {
  if (status === 'completed') {
    return (
      <div 
        style={{
          backgroundColor: 'var(--status-success-bg)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          borderRadius: '8px',
          padding: '16px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: 'var(--status-success)',
          marginBottom: '24px'
        }}
      >
        <ShieldCheck size={20} />
        <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>
          Audit Completed. Results synthesized successfully.
        </span>
      </div>
    );
  }

  if (status === 'review_required') {
    return (
      <div 
        style={{
          backgroundColor: 'var(--status-warning-bg)',
          border: '1px solid rgba(245, 158, 11, 0.2)',
          borderRadius: '8px',
          padding: '20px',
          color: 'var(--status-warning)',
          marginBottom: '24px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <AlertTriangle size={20} />
          <span style={{ fontSize: '0.95rem', fontWeight: 700 }}>
            Human Review Required
          </span>
        </div>
        <p style={{ margin: '0 0 12px 0', fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
          This audit query triggered confidence gate warnings and must be verified by a compliance officer before the final audit report is compiled.
        </p>
        {reasons && reasons.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>TRIGGER WARNINGS:</span>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {reasons.map((r, idx) => (
                <span 
                  key={idx} 
                  style={{ 
                    fontSize: '0.7rem', 
                    backgroundColor: 'rgba(245, 158, 11, 0.15)', 
                    color: 'var(--status-warning)', 
                    padding: '2px 8px', 
                    borderRadius: '4px',
                    fontWeight: 600
                  }}
                >
                  {r.replace(/_/g, ' ').toUpperCase()}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  if (status === 'rejected') {
    return (
      <div 
        style={{
          backgroundColor: 'var(--status-error-bg)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          borderRadius: '8px',
          padding: '20px',
          color: 'var(--status-error)',
          marginBottom: '24px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <XOctagon size={20} />
          <span style={{ fontSize: '0.95rem', fontWeight: 700 }}>
            Audit Execution Rejected
          </span>
        </div>
        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
          This compliance audit thread has been explicitly rejected by a compliance operator. No final report has been synthesized.
        </p>
      </div>
    );
  }

  return null;
}
