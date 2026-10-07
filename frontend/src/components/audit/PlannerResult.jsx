import React from 'react';
import { Compass, BookOpen, User, HardDrive } from 'lucide-react';

export default function PlannerResult({ planner }) {
  if (!planner) return null;

  const formatLabel = (val) => {
    return val?.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || 'N/A';
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">
          <Compass size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Audit Planner Scope</span>
        </h3>
      </div>
      <div className="card-body">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          {/* Audit Type */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <Compass size={16} style={{ color: 'var(--text-muted)', marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>AUDIT TYPE</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                {formatLabel(planner.audit_type)}
              </div>
            </div>
          </div>

          {/* Subject */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <User size={16} style={{ color: 'var(--text-muted)', marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>SUBJECT AREA</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                {formatLabel(planner.subject)}
              </div>
            </div>
          </div>

          {/* Regulation */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <BookOpen size={16} style={{ color: 'var(--text-muted)', marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>TARGET REGULATION</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 600, color: 'var(--accent-gold)' }}>
                {planner.regulation || 'General Framework'}
              </div>
            </div>
          </div>
        </div>

        {/* Intent */}
        {planner.intent && (
          <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-color)', paddingTop: '16px', display: 'flex', gap: '12px' }}>
            <HardDrive size={16} style={{ color: 'var(--text-muted)', marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>EVALUATION INTENT</div>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                {planner.intent}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
