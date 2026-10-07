import React from 'react';
import { FileText, Award, BookOpen, Quote } from 'lucide-react';

export default function RetrievalResults({ retrieval }) {
  if (!retrieval) return null;

  const renderEvidenceCard = (item, idx) => {
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
  };

  const policyList = retrieval.company_policy || [];
  const regulationList = retrieval.regulations || [];

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">
          <BookOpen size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Retrieved RAG Evidence</span>
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Retrieval Confidence:</span>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-gold)' }}>
            {(retrieval.confidence * 100).toFixed(0)}% ({retrieval.confidence_level || 'Medium'})
          </span>
        </div>
      </div>

      <div className="card-body" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Left Column: Company Policies */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={16} style={{ color: 'var(--text-muted)' }} />
            <span>Company Policies ({policyList.length})</span>
          </h4>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {policyList.length === 0 ? (
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '16px', textAlign: 'center', backgroundColor: 'var(--bg-primary)', border: '1px dashed var(--border-color)', borderRadius: '6px' }}>
                No policy matches found.
              </div>
            ) : (
              policyList.map((item, idx) => renderEvidenceCard(item, idx))
            )}
          </div>
        </div>

        {/* Right Column: Regulations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={16} style={{ color: 'var(--text-muted)' }} />
            <span>Regulations ({regulationList.length})</span>
          </h4>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {regulationList.length === 0 ? (
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '16px', textAlign: 'center', backgroundColor: 'var(--bg-primary)', border: '1px dashed var(--border-color)', borderRadius: '6px' }}>
                No regulation matches found.
              </div>
            ) : (
              regulationList.map((item, idx) => renderEvidenceCard(item, idx))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
