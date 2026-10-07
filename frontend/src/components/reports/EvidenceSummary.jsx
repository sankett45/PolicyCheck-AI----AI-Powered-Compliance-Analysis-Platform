import React from 'react';
import { BookOpen, FileText, Quote } from 'lucide-react';

export default function EvidenceSummary({ evidenceSummary }) {
  if (!evidenceSummary || evidenceSummary.length === 0) {
    return (
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h3 className="card-title">
            <BookOpen size={18} style={{ color: 'var(--accent-gold)' }} />
            <span>Traceable Evidence Sources</span>
          </h3>
        </div>
        <div className="card-body">
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
            No evidence documents referenced in this report.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <div className="card-header">
        <h3 className="card-title">
          <BookOpen size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Traceable Evidence Sources ({evidenceSummary.length})</span>
        </h3>
      </div>
      <div className="card-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {evidenceSummary.map((item, idx) => {
          const similarityPercent = item.similarity_score 
            ? (item.similarity_score * 100).toFixed(0) + '%' 
            : 'N/A';

          return (
            <div 
              key={`${item.document_id}-${idx}`}
              style={{
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                  <FileText size={16} style={{ color: 'var(--accent-gold)', flexShrink: 0 }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                    {item.filename}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.7rem', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-secondary)', padding: '2px 6px', borderRadius: '4px', fontWeight: 500 }}>
                    v{item.document_version || '1.0.0'}
                  </span>
                  {item.page_number !== null && item.page_number !== undefined && (
                    <span style={{ fontSize: '0.7rem', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-secondary)', padding: '2px 6px', borderRadius: '4px', fontWeight: 500 }}>
                      Page {item.page_number}
                    </span>
                  )}
                  <span style={{ fontSize: '0.7rem', backgroundColor: 'var(--accent-gold-alpha)', color: 'var(--accent-gold)', padding: '2px 6px', borderRadius: '4px', fontWeight: 600, border: '1px solid var(--accent-gold-border)' }}>
                    Score: {similarityPercent}
                  </span>
                </div>
              </div>

              {/* Text Snippet */}
              <div 
                style={{ 
                  fontSize: '0.85rem', 
                  color: 'var(--text-secondary)', 
                  backgroundColor: 'var(--bg-tertiary)', 
                  padding: '12px 16px', 
                  borderRadius: '6px', 
                  borderLeft: '3px solid var(--accent-gold)',
                  lineHeight: 1.6,
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'inherit'
                }}
              >
                <Quote size={12} style={{ color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }} />
                {item.text}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
