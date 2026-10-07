import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Upload, 
  Search, 
  RefreshCw, 
  AlertTriangle, 
  Calendar, 
  Layers, 
  Trash2, 
  Eye,
  CheckCircle,
  HelpCircle
} from 'lucide-react';

import PageContainer from '../components/layout/PageContainer';
import DocumentUpload from '../components/documents/DocumentUpload';
import DocumentDetails from '../components/documents/DocumentDetails';
import { documentApi } from '../services/documentApi';

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Search & Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');

  // Modal & Slide Panel States
  const [uploadOpen, setUploadOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [deleteConfirmDoc, setDeleteConfirmDoc] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Fetch Documents
  const fetchDocuments = async (showLoader = true) => {
    if (showLoader) setLoading(true);
    setError(null);
    try {
      const data = await documentApi.getDocuments();
      // Sort newest first
      const sorted = [...data].sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at));
      setDocuments(sorted);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend document storage.');
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // Handle Document Delete
  const handleDelete = async () => {
    if (!deleteConfirmDoc) return;
    setDeleteLoading(true);
    setError(null);

    try {
      await documentApi.deleteDocument(deleteConfirmDoc.id);
      // If deleted document is currently open in details side panel, close it
      if (selectedDocument && selectedDocument.id === deleteConfirmDoc.id) {
        setSelectedDocument(null);
      }
      setDeleteConfirmDoc(null);
      await fetchDocuments(false); // Refresh list
    } catch (err) {
      setError(err.message || 'Deletion failed. Document could not be removed.');
    } finally {
      setDeleteLoading(false);
    }
  };

  // Safe Date Formatting
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

  const formatDocType = (type) => {
    return type?.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || 'Unknown';
  };

  // Client-side filtering
  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedType === 'all' || doc.document_type === selectedType;
    return matchesSearch && matchesType;
  });

  // Action header CTA
  const headerAction = (
    <button className="btn btn-primary" onClick={() => setUploadOpen(true)}>
      <Upload size={16} />
      <span>Upload Document</span>
    </button>
  );

  return (
    <PageContainer 
      title="Documents & Evidence" 
      subtitle="Manage company policies and regulatory guidelines used for compliance checks."
      action={headerAction}
    >
      {/* Search and Filters */}
      <div 
        style={{ 
          display: 'flex', 
          gap: '16px', 
          marginBottom: '24px', 
          alignItems: 'center',
          flexWrap: 'wrap'
        }}
      >
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <Search 
            size={18} 
            style={{ 
              position: 'absolute', 
              left: '14px', 
              top: '50%', 
              transform: 'translateY(-50%)', 
              color: 'var(--text-muted)' 
            }} 
          />
          <input
            type="text"
            className="form-control"
            placeholder="Search documents by filename..."
            style={{ paddingLeft: '42px' }}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <select
          className="form-control"
          style={{ width: '200px' }}
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
        >
          <option value="all">All Classification Types</option>
          <option value="company_policy">Company Policy</option>
          <option value="regulation">Regulation</option>
          <option value="contract">Contract</option>
          <option value="sop">SOP</option>
        </select>

        <button 
          className="btn btn-secondary" 
          onClick={() => fetchDocuments(true)}
          title="Refresh List"
          aria-label="Refresh list"
        >
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="error-container">
          <AlertTriangle className="error-icon" />
          <div style={{ flex: 1 }}>
            <h4 className="error-title">Corpus Synchronize Error</h4>
            <p className="error-desc">{error}</p>
          </div>
          <button className="btn btn-secondary" onClick={() => fetchDocuments(true)} style={{ padding: '6px 12px', fontSize: '0.75rem' }}>
            Retry Sync
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="card">
          <div className="loader-container">
            <div className="spinner"></div>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Synchronizing document corpus...</div>
          </div>
        </div>
      ) : filteredDocuments.length === 0 ? (
        /* Empty State */
        <div className="card">
          <div className="empty-state">
            <FileText className="empty-state-icon" style={{ strokeWidth: 1.25 }} />
            <h3 className="empty-state-title">
              {searchQuery || selectedType !== 'all' ? 'No matching documents found' : 'No documents in compliance base'}
            </h3>
            <p className="empty-state-desc" style={{ marginBottom: '24px' }}>
              {searchQuery || selectedType !== 'all' 
                ? 'Try modifying your search queries or category filters.'
                : 'Upload company policy documents, regulatory standard manuals, or custom SOPs to prepare for AI compliance checks.'
              }
            </p>
            {!(searchQuery || selectedType !== 'all') && (
              <button className="btn btn-primary" onClick={() => setUploadOpen(true)}>
                <Upload size={16} />
                <span>Upload Document</span>
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Document Table Grid */
        <div className="card" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)' }}>
                <th style={{ padding: '16px 24px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>FILENAME</th>
                <th style={{ padding: '16px 24px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>CLASSIFICATION</th>
                <th style={{ padding: '16px 24px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>VERSION</th>
                <th style={{ padding: '16px 24px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>CHUNKS</th>
                <th style={{ padding: '16px 24px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>DATE INGESTED</th>
                <th style={{ padding: '16px 24px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'right' }}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocuments.map((doc) => (
                <tr 
                  key={doc.id} 
                  style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.2s ease' }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-primary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <FileText size={16} style={{ color: 'var(--accent-gold)' }} />
                      <span style={{ wordBreak: 'break-all' }}>{doc.filename}</span>
                    </div>
                  </td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>
                    {formatDocType(doc.document_type)}
                  </td>
                  <td style={{ padding: '16px 24px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--accent-gold)' }}>v{doc.document_version}</span>
                  </td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>
                    {doc.chunk_count}
                  </td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>
                    {formatDate(doc.uploaded_at)}
                  </td>
                  <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '8px' }}>
                      <button 
                        className="btn btn-secondary" 
                        style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                        onClick={() => setSelectedDocument(doc)}
                        title="View details"
                      >
                        <Eye size={14} />
                        <span className="desktop-only">Details</span>
                      </button>
                      <button 
                        className="btn" 
                        style={{ padding: '6px 12px', fontSize: '0.8rem', backgroundColor: 'transparent', border: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--status-error)' }}
                        onClick={() => setDeleteConfirmDoc(doc)}
                        title="Delete Document"
                      >
                        <Trash2 size={14} />
                        <span className="desktop-only">Delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Upload Modal Overlay */}
      {uploadOpen && (
        <DocumentUpload 
          onClose={() => setUploadOpen(false)} 
          onSuccess={() => {
            setUploadOpen(false);
            fetchDocuments(false); // Silent refresh
          }} 
        />
      )}

      {/* Slide-out details panel */}
      {selectedDocument && (
        <DocumentDetails 
          document={selectedDocument}
          allDocuments={documents}
          onClose={() => setSelectedDocument(null)}
          onDelete={(doc) => {
            setDeleteConfirmDoc(doc);
          }}
        />
      )}

      {/* Delete Confirmation Overlay */}
      {deleteConfirmDoc && (
        <div className="modal-overlay" onClick={() => setDeleteConfirmDoc(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '440px' }}>
            <div className="modal-header">
              <h3 className="modal-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--status-error)' }}>
                <AlertTriangle size={18} />
                <span>Delete Corpus Document?</span>
              </h3>
              <button className="modal-close" onClick={() => setDeleteConfirmDoc(null)} aria-label="Close modal">
                <X size={18} />
              </button>
            </div>
            
            <div className="modal-body" style={{ padding: '24px' }}>
              <p style={{ margin: '0 0 12px 0', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                Are you sure you want to delete <strong>{deleteConfirmDoc.filename} (v{deleteConfirmDoc.document_version})</strong>?
              </p>
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                This operation is permanent. The document metadata and text chunk vectors will be removed from Neon PostgreSQL and Qdrant index.
              </p>
            </div>

            <div className="modal-footer">
              <button 
                className="btn btn-secondary" 
                onClick={() => setDeleteConfirmDoc(null)}
                disabled={deleteLoading}
              >
                Cancel
              </button>
              <button 
                className="btn" 
                style={{ backgroundColor: 'var(--status-error)', color: '#fff' }}
                onClick={handleDelete}
                disabled={deleteLoading}
              >
                {deleteLoading ? (
                  <>
                    <div className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px', borderTopColor: '#fff' }}></div>
                    <span>Deleting...</span>
                  </>
                ) : (
                  <span>Delete</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
