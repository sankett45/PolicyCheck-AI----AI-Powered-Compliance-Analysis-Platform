import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  UserCheck, 
  Search, 
  AlertTriangle, 
  ArrowLeft,
  Layers,
  CheckCircle,
  HelpCircle,
  FileText
} from 'lucide-react';

import PageContainer from '../components/layout/PageContainer';
import ReviewHeader from '../components/review/ReviewHeader';
import ReviewReason from '../components/review/ReviewReason';
import ReviewSummary from '../components/review/ReviewSummary';
import ReviewDecision from '../components/review/ReviewDecision';
import ComplianceResults from '../components/audit/ComplianceResults';
import RiskResults from '../components/audit/RiskResults';
import RecommendationResults from '../components/audit/RecommendationResults';
import { reviewApi } from '../services/reviewApi';

// Mock Fixture context for presentation testing (Groq rate-limit guard)
const MOCK_REVIEW_FIXTURE = {
  review_id: 'mock_review_123',
  question: 'Do we enforce multi-factor authentication for administrative access?',
  review_status: 'pending',
  reasons: ['low_compliance_confidence', 'high_risk'],
  retrieval_confidence: 0.45,
  compliance_confidence: 0.38,
  risk_level: 'high',
  risk_score: 75,
  compliance_summary: 'The administrative access control check failed verification due to missing active MFA records for cloud databases.',
  findings: [
    {
      finding_id: 'find_mfa_001',
      control: 'Multi-Factor Authentication',
      status: 'non_compliant',
      company_requirement: 'MFA must be enforced for all administrator sessions access platforms.',
      regulatory_requirement: 'ISO 27001 Control A.9.4.2 requires secure log-on procedures.',
      reasoning: 'Although SSO is implemented, administrative accounts accessing AWS console do not have mandatory MFA enforced.',
      evidence_citations: ['access_control_policy.txt:L10']
    }
  ],
  recommendations: [
    {
      finding_id: 'find_mfa_001',
      control: 'Multi-Factor Authentication',
      priority: 'high',
      recommendation: 'Enable conditional access policies requiring MFA for administrative roles.',
      rationale: 'Mitigates the risk of hijacked administrator credentials accessing cloud setups.',
      implementation_steps: [
        'Identify all IAM accounts with administrative roles.',
        'Configure AWS Identity Center to enforce MFA.',
        'Enforce block policy for logins without active MFA devices.'
      ],
      evidence: ['access_control_policy.txt']
    }
  ],
  created_at: new Date().toISOString()
};

export default function Reviews() {
  const { reviewId } = useParams();
  const navigate = useNavigate();

  // Search input state
  const [inputId, setInputId] = useState('');
  const [searchError, setSearchError] = useState(null);

  // Review execution states
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Decision transaction states
  const [submitting, setSubmitting] = useState(false);
  const [decisionError, setDecisionError] = useState(null);

  const fetchReview = async (id) => {
    setLoading(true);
    setError(null);
    setReview(null);

    // Sandbox Mock Toggle
    if (import.meta.env.DEV && id === 'mock_review_123') {
      setTimeout(() => {
        setReview(MOCK_REVIEW_FIXTURE);
        setLoading(false);
      }, 600);
      return;
    }

    try {
      const data = await reviewApi.getReview(id);
      setReview(data);
    } catch (err) {
      setError(err.message || 'The requested review could not be found or connection failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (reviewId) {
      fetchReview(reviewId);
    }
  }, [reviewId]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const id = inputId.trim();
    if (!id) {
      setSearchError('Please enter a valid review ID.');
      return;
    }
    setSearchError(null);
    navigate(`/reviews/${id}`);
  };

  const handleDecisionSubmit = async (decision, comment) => {
    setSubmitting(true);
    setDecisionError(null);

    // Sandbox Mock Success
    if (import.meta.env.DEV && reviewId === 'mock_review_123') {
      setTimeout(() => {
        const statusMap = {
          approve: 'approved',
          reject: 'rejected',
          request_more_evidence: 'needs_more_evidence'
        };
        setReview(prev => ({
          ...prev,
          review_status: statusMap[decision]
        }));
        setSubmitting(false);
      }, 800);
      return;
    }

    try {
      const res = await reviewApi.submitReviewDecision(reviewId, decision, comment);
      // Refresh review details upon success
      setReview(prev => ({
        ...prev,
        review_status: res.status
      }));
    } catch (err) {
      setDecisionError(err.message || 'Failed to submit review decision. Try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // Reusable compliance models layout grouping
  const getComplianceData = (rev) => {
    return {
      overall_status: rev.risk_level === 'critical' || rev.reasons.includes('high_risk') ? 'non_compliant' : 'partially_compliant',
      summary: rev.compliance_summary,
      findings: rev.findings || []
    };
  };

  const getRiskData = (rev) => {
    return {
      overall_risk_level: rev.risk_level,
      overall_risk_score: rev.risk_score,
      assessments: (rev.findings || []).map((f) => ({
        finding_id: f.finding_id,
        control: f.control,
        risk_level: rev.risk_level,
        risk_score: rev.risk_score,
        severity: 'N/A',
        likelihood: 'N/A',
        impact: 'N/A',
        rationale: 'Triggered compliance gate verification'
      }))
    };
  };

  const getRecommendationsData = (rev) => {
    return {
      recommendations: rev.recommendations || []
    };
  };

  // Header actions
  const headerAction = reviewId ? (
    <button className="btn btn-secondary" onClick={() => navigate('/reviews')}>
      <ArrowLeft size={16} />
      <span>All Reviews</span>
    </button>
  ) : null;

  return (
    <PageContainer
      title="Reviews & HITL"
      subtitle="Manual verification dashboard for compliance audits."
      action={headerAction}
    >
      {/* STATE 1: No Review Selected */}
      {!reviewId && (
        <div className="card" style={{ maxWidth: '540px', margin: '40px auto' }}>
          <div className="card-header">
            <h3 className="card-title">
              <UserCheck size={18} style={{ color: 'var(--accent-gold)' }} />
              <span>Inspect Human Review</span>
            </h3>
          </div>
          <form onSubmit={handleSearchSubmit}>
            <div className="card-body">
              <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Compliance audits requiring manual verification generate a unique Review ID. Enter the ID to load the findings, risk details, and record a decision.
              </p>
              
              <div className="form-group">
                <label className="form-label" htmlFor="search-review-id">Review Request ID</label>
                <div style={{ position: 'relative' }}>
                  <Search 
                    size={16} 
                    style={{ 
                      position: 'absolute', 
                      left: '12px', 
                      top: '50%', 
                      transform: 'translateY(-50%)', 
                      color: 'var(--text-muted)' 
                    }} 
                  />
                  <input
                    id="search-review-id"
                    type="text"
                    className="form-control"
                    placeholder="Enter Review UUID (or type 'mock_review_123' for sandbox)"
                    style={{ paddingLeft: '38px' }}
                    value={inputId}
                    onChange={(e) => {
                      setInputId(e.target.value);
                      if (searchError) setSearchError(null);
                    }}
                  />
                </div>
                {searchError && (
                  <div style={{ color: 'var(--status-error)', fontSize: '0.8rem', marginTop: '6px', fontWeight: 500 }}>
                    {searchError}
                  </div>
                )}
              </div>
            </div>

            <div className="card-header" style={{ borderTop: '1px solid var(--border-color)', borderBottom: 'none', justifyContent: 'flex-end', padding: '16px 24px' }}>
              <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>
                <span>Load Review Workspace</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* STATE 2: Loading State */}
      {loading && reviewId && (
        <div className="card" style={{ maxWidth: '640px', margin: '40px auto' }}>
          <div className="loader-container">
            <div className="spinner"></div>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Retrieving human review context...</div>
          </div>
        </div>
      )}

      {/* STATE 3: Error State */}
      {error && !loading && reviewId && (
        <div style={{ maxWidth: '640px', margin: '40px auto' }}>
          <div className="error-container">
            <AlertTriangle className="error-icon" />
            <div>
              <h4 className="error-title">Unable to load review</h4>
              <p className="error-desc">{error}</p>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button className="btn btn-secondary" onClick={() => navigate('/reviews')}>
              Return to Review Search
            </button>
          </div>
        </div>
      )}

      {/* STATE 4: Workspace Loaded */}
      {!loading && !error && review && reviewId && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Header warning */}
          <ReviewHeader 
            reviewId={review.review_id}
            question={review.question}
            status={review.review_status}
            riskLevel={review.risk_level}
            riskScore={review.risk_score}
          />

          {/* Reasons banner */}
          <ReviewReason reasons={review.reasons} />

          {/* Metrics scorecard summary */}
          <ReviewSummary 
            retrievalConfidence={review.retrieval_confidence}
            complianceConfidence={review.compliance_confidence}
            riskLevel={review.risk_level}
            riskScore={review.risk_score}
          />

          {/* Findings */}
          <ComplianceResults compliance={getComplianceData(review)} />

          {/* Risk details */}
          <RiskResults risk={getRiskData(review)} />

          {/* Recommendations */}
          <RecommendationResults recommendations={getRecommendationsData(review)} />

          {/* Decision Center */}
          <ReviewDecision 
            reviewId={review.review_id}
            currentStatus={review.review_status}
            onSubmit={handleDecisionSubmit}
            submitting={submitting}
            error={decisionError}
          />
        </div>
      )}
    </PageContainer>
  );
}
