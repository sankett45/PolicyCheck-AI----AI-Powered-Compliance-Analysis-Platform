import React from 'react';
import { X, Calendar, Database, Folder, Tag, Layers, CheckCircle } from 'lucide-react';
import DocumentVersions from './DocumentVersions';

export default function DocumentDetails({ document, allDocuments, onClose, onDelete }) {
  if (!document) return null;

  // Format date safely
  const formatUploadDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
    } catch (e) {
      return dateStr;
    }
  };

  // Find all other versions of the same filename to display history
  const otherVersions = allDocuments
    .filter((doc) => doc.filename === document.filename)
    .sort((a, b) => new Date(b.created_at || b.uploaded_at) - new Date(a.created_at || a.uploaded_at));

  // Determine pill status class
  const getStatusClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'indexed':
      case 'ready':
        return 'api-status-dot connected';
      case 'processing':
        return 'api-status-dot connecting';
      default:
        return 'api-status-dot unavailable';
    }
  };

  const getStatusText = (status) => {
    if (!status) return 'Unknown';
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  const formatDocType = (type) => {
    return type?.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || 'Unknown';
  };

  return (
    <div className="side-panel-overlay" onClick={onClose}>
      <div className="side-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={18} style={{ color: 'var(--accent-gold)' }} />
            <span>Document Details</span>
          </h3>
          <button className="modal-close" onClick={onClose} aria-label="Close panel">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body" style={{ flex: 1, padding: '24px' }}>
          <div style={{ marginBottom: '24px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '1.2rem', color: 'var(--text-primary)', wordBreak: 'break-all' }}>
              {document.filename}
            </h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <span className={getStatusClass(document.status)}></span>
              <span>{getStatusText(document.status)}</span>
              <span>•</span>
              <span>{formatDocType(document.document_type)}</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '32px' }}>
            {/* Type */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <Folder size={16} style={{ color: 'var(--text-muted)', marginTop: '3px' }} />
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CLASSIFICATION</div>
                <div style={{ fontSize: '0.9rem' }}>{formatDocType(document.document_type)}</div>
              </div>
            </div>

            {/* Version */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <Tag size={16} style={{ color: 'var(--text-muted)', marginTop: '3px' }} />
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>SEMANTIC VERSION</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--accent-gold)' }}>
                    v{document.document_version}
                  </span>
                  {otherVersions[0]?.id === document.id && (
                    <span style={{ fontSize: '0.7rem', backgroundColor: 'var(--status-success-bg)', color: 'var(--status-success)', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
                      Latest Version
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Chunk Count */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <Layers size={16} style={{ color: 'var(--text-muted)', marginTop: '3px' }} />
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>VECTOR INDEX CHUNKS</div>
                <div style={{ fontSize: '0.9rem' }}>{document.chunk_count} text chunks generated</div>
              </div>
            </div>

            {/* Uploaded At */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <Calendar size={16} style={{ color: 'var(--text-muted)', marginTop: '3px' }} />
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>INGESTED TIMESTAMP</div>
                <div style={{ fontSize: '0.9rem' }}>{formatUploadDate(document.uploaded_at)}</div>
              </div>
            </div>

            {/* Path */}
            <div style={{ display: 'flex', gap: '12px', minWidth: 0 }}>
              <Database size={16} style={{ color: 'var(--text-muted)', marginTop: '3px', flexShrink: 0 }} />
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>LOCAL DISK LOCATION</div>
                <div style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
                  {document.file_path}
                </div>
              </div>
            </div>

            {/* Document ID */}
            <div style={{ display: 'flex', gap: '12px', minWidth: 0 }}>
              <Database size={16} style={{ color: 'var(--text-muted)', marginTop: '3px', flexShrink: 0 }} />
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>DATABASE UUID</div>
                <div style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
                  {document.id}
                </div>
              </div>
            </div>
          </div>

          {/* Versions list */}
          <DocumentVersions versions={otherVersions} currentId={document.id} />
        </div>

        <div className="modal-footer" style={{ borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)' }}>
          <button 
            className="btn btn-secondary" 
            style={{ marginRight: 'auto', backgroundColor: 'var(--status-error-bg)', color: 'var(--status-error)', borderColor: 'rgba(239, 68, 68, 0.2)' }}
            onClick={() => onDelete(document)}
          >
            Delete Corpus Document
          </button>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
