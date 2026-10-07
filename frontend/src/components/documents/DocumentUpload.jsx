import React, { useState, useRef } from 'react';
import { Upload, X, FileText, AlertCircle } from 'lucide-react';
import { documentApi } from '../../services/documentApi';

export default function DocumentUpload({ onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [documentType, setDocumentType] = useState('company_policy');
  const [documentVersion, setDocumentVersion] = useState('1.0.0');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef(null);

  // Supported doc types from backend enum
  const docTypes = [
    { value: 'company_policy', label: 'Company Policy' },
    { value: 'regulation', label: 'Regulation' },
    { value: 'contract', label: 'Contract' },
    { value: 'sop', label: 'SOP (Standard Operating Procedure)' }
  ];

  // Helper to format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Validate file extension
  const validateFile = (selectedFile) => {
    if (!selectedFile) return false;
    const filename = selectedFile.name.toLowerCase();
    const isSupported = filename.endsWith('.pdf') || filename.endsWith('.docx') || filename.endsWith('.txt');
    if (!isSupported) {
      setError('Unsupported file type. Please select a PDF, DOCX, or TXT file.');
      setFile(null);
      return false;
    }
    setError(null);
    return true;
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const handleRemoveFile = (e) => {
    e.stopPropagation();
    setFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await documentApi.uploadDocument(file, documentType, documentVersion);
      onSuccess();
    } catch (err) {
      setError(err.message || 'Ingestion pipeline execution failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Upload Compliance Document</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div className="error-container">
                <AlertCircle className="error-icon" />
                <div>
                  <h4 className="error-title">Upload failed</h4>
                  <p className="error-desc">{error}</p>
                </div>
              </div>
            )}

            {/* Drag & Drop Area */}
            <div className="form-group">
              <input
                ref={fileInputRef}
                type="file"
                id="file-upload"
                style={{ display: 'none' }}
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                disabled={loading}
              />
              
              {!file ? (
                <div 
                  className={`file-dropzone ${dragActive ? 'drag-active' : ''}`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current.click()}
                >
                  <Upload className="file-dropzone-icon" />
                  <div className="file-dropzone-text">
                    <strong>Click to browse</strong> or drag and drop your file here
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Supported formats: PDF, DOCX, TXT
                  </div>
                </div>
              ) : (
                <div className="selected-file-info">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
                    <FileText style={{ color: 'var(--accent-gold)', flexShrink: 0 }} size={24} />
                    <div style={{ minWidth: 0 }}>
                      <div className="selected-file-name">{file.name}</div>
                      <div className="selected-file-size">{formatFileSize(file.size)}</div>
                    </div>
                  </div>
                  {!loading && (
                    <button 
                      type="button" 
                      onClick={handleRemoveFile}
                      style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
                      title="Remove file"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Document Type Dropdown */}
            <div className="form-group">
              <label className="form-label" htmlFor="doc-type">Document Type</label>
              <select
                id="doc-type"
                className="form-control"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                disabled={loading}
              >
                {docTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Document Version Input */}
            <div className="form-group">
              <label className="form-label" htmlFor="doc-version">Document Version</label>
              <input
                id="doc-version"
                type="text"
                className="form-control"
                placeholder="e.g. 1.0.0"
                value={documentVersion}
                onChange={(e) => setDocumentVersion(e.target.value)}
                disabled={loading}
                required
              />
            </div>
          </div>

          <div className="modal-footer">
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading || !file}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></div>
                  <span>Uploading & Indexing...</span>
                </>
              ) : (
                <span>Ingest Document</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
