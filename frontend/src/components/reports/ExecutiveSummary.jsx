import React from 'react';
import { BookOpen } from 'lucide-react';

export default function ExecutiveSummary({ summary }) {
  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <div className="card-header">
        <h3 className="card-title">
          <BookOpen size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Executive Summary</span>
        </h3>
      </div>
      <div className="card-body">
        {summary ? (
          <p 
            style={{ 
              margin: 0, 
              fontSize: '0.925rem', 
              color: 'var(--text-primary)', 
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap'
            }}
          >
            {summary}
          </p>
        ) : (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
            Executive summary unavailable.
          </div>
        )}
      </div>
    </div>
  );
}
