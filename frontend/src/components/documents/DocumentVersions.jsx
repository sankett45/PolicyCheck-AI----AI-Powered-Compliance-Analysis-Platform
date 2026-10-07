import React from 'react';
import { Calendar, Tag } from 'lucide-react';

export default function DocumentVersions({ versions, currentId }) {
  if (!versions || versions.length === 0) return null;

  // Format date safely
  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <div style={{ marginTop: '24px', borderTop: '1px solid var(--border-color)', paddingTop: '24px' }}>
      <h5 style={{ margin: '0 0 16px 0', fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 600 }}>
        Version History ({versions.length})
      </h5>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {versions.map((ver, index) => {
          const isSelected = ver.id === currentId;
          const isLatest = index === 0;

          return (
            <div 
              key={ver.id} 
              style={{
                backgroundColor: isSelected ? 'var(--accent-gold-alpha)' : 'var(--bg-primary)',
                border: `1px solid ${isSelected ? 'var(--accent-gold-border)' : 'var(--border-color)'}`,
                borderRadius: '6px',
                padding: '12px 16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '12px'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <Tag size={12} style={{ color: 'var(--accent-gold)' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    v{ver.document_version}
                  </span>
                  {isLatest && (
                    <span style={{ fontSize: '0.65rem', backgroundColor: 'var(--status-success-bg)', color: 'var(--status-success)', padding: '1px 5px', borderRadius: '3px', fontWeight: 600 }}>
                      Latest
                    </span>
                  )}
                  {isSelected && (
                    <span style={{ fontSize: '0.65rem', backgroundColor: 'rgba(255,215,0,0.1)', color: 'var(--accent-gold)', padding: '1px 5px', borderRadius: '3px', fontWeight: 600 }}>
                      Viewing
                    </span>
                  )}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <Calendar size={12} />
                  <span>Uploaded {formatDate(ver.uploaded_at)}</span>
                </div>
              </div>
              
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                {ver.chunk_count} Chunks
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
