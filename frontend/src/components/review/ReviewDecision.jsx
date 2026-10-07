import React, { useState } from 'react';
import { Check, X, AlertCircle, RefreshCw } from 'lucide-react';

export default function ReviewDecision({ reviewId, currentStatus, onSubmit, submitting, error }) {
  const [comment, setComment] = useState('');
  const [validationError, setValidationError] = useState(null);

  const isResolved = currentStatus !== 'pending';

  const handleAction = (decision) => {
    const trimmedComment = comment.trim();
    
    // Validate comment on Reject or Request More Evidence
    if ((decision === 'reject' || decision === 'request_more_evidence') && !trimmedComment) {
      setValidationError(`A comment explaining your reasoning is required to ${decision === 'reject' ? 'reject' : 'request more evidence'} this audit.`);
      return;
    }

    setValidationError(null);
    onSubmit(decision, trimmedComment);
  };

  if (isResolved) {
    const getOutcomeClass = () => {
      switch (currentStatus?.toLowerCase()) {
        case 'approved':
          return { label: 'Approved', color: 'var(--status-success)', text: 'This compliance audit has been human-approved and the final report is compiled.' };
        case 'rejected':
          return { label: 'Rejected', color: 'var(--status-error)', text: 'This compliance audit was explicitly rejected by the human reviewer.' };
        default:
          return { label: 'More Evidence Requested', color: 'var(--status-warning)', text: 'Additional evidence has been requested. The audit thread is terminated.' };
      }
    };
    const outcome = getOutcomeClass();
    return (
      <div className="card" style={{ borderTop: `4px solid ${outcome.color}`, backgroundColor: 'var(--bg-secondary)' }}>
        <div className="card-header">
          <h3 className="card-title">Review Decision Log</h3>
        </div>
        <div className="card-body">
          <p style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-primary)', fontWeight: 600 }}>
            Status: <span style={{ color: outcome.color }}>{outcome.label}</span>
          </p>
          <p style={{ margin: '8px 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            {outcome.text}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Reviewer Decision Center</h3>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {error && (
          <div className="error-container" style={{ margin: 0 }}>
            <AlertCircle className="error-icon" />
            <div>
              <h4 className="error-title">Decision Submission Failed</h4>
              <p className="error-desc">{error}</p>
            </div>
          </div>
        )}

        {validationError && (
          <div className="error-container" style={{ margin: 0, backgroundColor: 'var(--status-warning-bg)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
            <AlertCircle className="error-icon" style={{ color: 'var(--status-warning)' }} />
            <div>
              <h4 className="error-title" style={{ color: 'var(--status-warning)' }}>Validation Required</h4>
              <p className="error-desc" style={{ color: 'var(--text-secondary)' }}>{validationError}</p>
            </div>
          </div>
        )}

        {/* Comment Textarea */}
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label" htmlFor="reviewer-comment">Reviewer Comment / Rationale</label>
          <textarea
            id="reviewer-comment"
            className="form-control"
            rows={4}
            placeholder="Add comments explaining your decision (required for rejections or more evidence requests)..."
            value={comment}
            onChange={(e) => {
              setComment(e.target.value);
              if (validationError) setValidationError(null);
            }}
            disabled={submitting}
            style={{ resize: 'vertical' }}
          />
        </div>
      </div>

      <div 
        className="card-header" 
        style={{ 
          borderTop: '1px solid var(--border-color)', 
          borderBottom: 'none', 
          display: 'flex', 
          justifyContent: 'flex-end', 
          gap: '12px',
          padding: '16px 24px',
          flexWrap: 'wrap'
        }}
      >
        {/* Request More Evidence */}
        <button
          type="button"
          className="btn"
          style={{ 
            backgroundColor: 'var(--bg-tertiary)', 
            color: 'var(--status-warning)', 
            border: '1px solid rgba(245, 158, 11, 0.2)' 
          }}
          onClick={() => handleAction('request_more_evidence')}
          disabled={submitting}
        >
          <RefreshCw size={14} className={submitting ? 'spinner' : ''} />
          <span>Request Evidence</span>
        </button>

        {/* Reject */}
        <button
          type="button"
          className="btn"
          style={{ 
            backgroundColor: 'var(--status-error-bg)', 
            color: 'var(--status-error)', 
            border: '1px solid rgba(239, 68, 68, 0.2)' 
          }}
          onClick={() => handleAction('reject')}
          disabled={submitting}
        >
          <X size={14} />
          <span>Reject Audit</span>
        </button>

        {/* Approve */}
        <button
          type="button"
          className="btn btn-primary"
          style={{ backgroundColor: 'var(--status-success)', color: '#000' }}
          onClick={() => handleAction('approve')}
          disabled={submitting}
        >
          <Check size={14} />
          <span>Approve & Continue</span>
        </button>
      </div>
    </div>
  );
}
