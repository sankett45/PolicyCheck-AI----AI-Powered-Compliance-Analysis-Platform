import React from 'react';
import { Download, ArrowLeft } from 'lucide-react';

export default function ReportActions({ onDownload, onBack, downloading }) {
  return (
    <div 
      className="card report-actions" 
      style={{ 
        marginBottom: '24px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px dashed var(--border-color)'
      }}
    >
      <div 
        className="card-body" 
        style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          gap: '16px',
          flexWrap: 'wrap',
          padding: '16px 24px'
        }}
      >
        <button 
          className="btn btn-secondary" 
          onClick={onBack}
          style={{ width: 'auto' }}
        >
          <ArrowLeft size={16} />
          <span>Audits Workspace</span>
        </button>

        <button 
          className="btn btn-primary" 
          onClick={onDownload}
          disabled={downloading}
          style={{ width: 'auto' }}
        >
          <Download size={16} />
          <span>{downloading ? 'Compiling Markdown...' : 'Download Report (.md)'}</span>
        </button>
      </div>
    </div>
  );
}
