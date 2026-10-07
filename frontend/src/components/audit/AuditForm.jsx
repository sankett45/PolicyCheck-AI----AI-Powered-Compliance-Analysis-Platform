import React, { useState } from 'react';
import { Shield, Play } from 'lucide-react';

export default function AuditForm({ onSubmit, loading }) {
  const [question, setQuestion] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      setError('Please enter a valid compliance question to audit.');
      return;
    }
    setError(null);
    onSubmit(trimmed);
  };

  return (
    <div className="card" style={{ maxWidth: '640px', margin: '0 auto' }}>
      <div className="card-header">
        <h3 className="card-title">
          <Shield size={18} style={{ color: 'var(--accent-gold)' }} />
          <span>Compliance Audit Query</span>
        </h3>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="card-body">
          <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Enter a question to run an AI-orchestrated compliance audit. The system will analyze your document corpus against target standards to evaluate risk, compliance, and recommendations.
          </p>
          
          <div className="form-group">
            <label className="form-label" htmlFor="audit-question">Audit Question</label>
            <textarea
              id="audit-question"
              className="form-control"
              rows={5}
              placeholder="e.g. Is our access control policy compliant with ISO 27001?"
              value={question}
              onChange={(e) => {
                setQuestion(e.target.value);
                if (error) setError(null);
              }}
              style={{ resize: 'vertical', minHeight: '120px' }}
              disabled={loading}
              required
            />
            {error && (
              <div style={{ color: 'var(--status-error)', fontSize: '0.8rem', marginTop: '6px', fontWeight: 500 }}>
                {error}
              </div>
            )}
          </div>
        </div>

        <div className="card-header" style={{ borderTop: '1px solid var(--border-color)', borderBottom: 'none', justifyContent: 'flex-end', padding: '16px 24px' }}>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading || !question.trim()}
            style={{ width: 'auto' }}
          >
            <Play size={14} />
            <span>Start Compliance Audit</span>
          </button>
        </div>
      </form>
    </div>
  );
}
