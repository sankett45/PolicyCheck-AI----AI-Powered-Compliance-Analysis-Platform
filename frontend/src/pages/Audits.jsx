import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, 
  RefreshCw, 
  ArrowLeft, 
  Layers, 
  ShieldCheck, 
  AlertTriangle,
  FileText,
  UserCheck
} from 'lucide-react';

import PageContainer from '../components/layout/PageContainer';
import AuditForm from '../components/audit/AuditForm';
import PlannerResult from '../components/audit/PlannerResult';
import RetrievalResults from '../components/audit/RetrievalResults';
import ComplianceResults from '../components/audit/ComplianceResults';
import RiskResults from '../components/audit/RiskResults';
import RecommendationResults from '../components/audit/RecommendationResults';
import ConfidenceIndicator from '../components/audit/ConfidenceIndicator';
import AuditStatus from '../components/audit/AuditStatus';
import StatCard from '../components/dashboard/StatCard';
import { auditApi } from '../services/auditApi';

export default function Audits() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [question, setQuestion] = useState('');
  const [status, setStatus] = useState(null); // 'completed' | 'review_required' | 'rejected'
  const [auditResult, setAuditResult] = useState(null);

  // Trigger Audit Query
  const handleStartAudit = async (trimmedQuestion) => {
    setQuestion(trimmedQuestion);
    setLoading(true);
    setError(null);
    setStatus(null);
    setAuditResult(null);

    try {
      const result = await auditApi.runAudit(trimmedQuestion);
      setAuditResult(result);
      setStatus(result.status);
    } catch (err) {
      setError(err.message || 'Audit execution encountered a connection timeout or backend processing failure.');
    } finally {
      setLoading(false);
    }
  };

  // Reset State
  const handleReset = () => {
    setQuestion('');
    setStatus(null);
    setAuditResult(null);
    setError(null);
    setLoading(false);
  };

  // Dynamic Header actions
  const headerAction = (status || error || loading) ? (
    <div style={{ display: 'flex', gap: '12px' }}>
      {status === 'completed' && auditResult?.report_id && (
        <button 
          className="btn btn-primary" 
          onClick={() => navigate(`/reports/${auditResult.report_id}`)}
          style={{ width: 'auto' }}
        >
          <FileText size={16} />
          <span>View Final Report</span>
        </button>
      )}
      <button className="btn btn-secondary" onClick={handleReset} disabled={loading} style={{ width: 'auto' }}>
        <ArrowLeft size={16} />
        <span>New Audit</span>
      </button>
    </div>
  ) : null;

  return (
    <PageContainer
      title="Compliance Audits"
      subtitle="Analyze company policies and regulations using LangGraph compliance agents."
      action={headerAction}
    >
      {/* 1. Loading State */}
      {loading && (
        <div className="card" style={{ maxWidth: '640px', margin: '40px auto' }}>
          <div className="loader-container" style={{ padding: '64px 32px' }}>
            <div className="spinner"></div>
            <h3 style={{ margin: '16px 0 8px 0', fontSize: '1.1rem', color: 'var(--text-primary)' }}>
              Executing Audit Workflow
            </h3>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center', maxWidth: '380px' }}>
              LangGraph compliance agents are processing the query, retrieving RAG evidence, assessing security risks, and synthesizing remediation checklists...
            </p>
          </div>
        </div>
      )}

      {/* 2. Error State */}
      {error && !loading && (
        <div style={{ maxWidth: '640px', margin: '40px auto' }}>
          <div className="error-container">
            <AlertTriangle className="error-icon" />
            <div style={{ flex: 1 }}>
              <h4 className="error-title">Audit execution failed</h4>
              <p className="error-desc">{error}</p>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
            <button className="btn btn-primary" onClick={() => handleStartAudit(question)}>
              <RefreshCw size={14} />
              <span>Retry Audit</span>
            </button>
            <button className="btn btn-secondary" onClick={handleReset}>
              Return to Form
            </button>
          </div>
        </div>
      )}

      {/* 3. Empty/Form State */}
      {!loading && !error && !auditResult && (
        <div style={{ padding: '24px 0' }}>
          <AuditForm onSubmit={handleStartAudit} loading={loading} />
        </div>
      )}

      {/* 4. Results Workspace State */}
      {!loading && !error && auditResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '16px' }}>
          {/* Header context card */}
          <div className="card" style={{ borderLeft: '4px solid var(--accent-gold)' }}>
            <div className="card-body" style={{ padding: '20px 24px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                CURRENT AUDIT QUESTION
              </div>
              <p style={{ margin: 0, fontSize: '1.05rem', fontWeight: 500, color: 'var(--text-primary)', wordBreak: 'break-word' }}>
                "{question}"
              </p>
            </div>
          </div>

          {/* Audit Status Banner */}
          <AuditStatus status={status} reasons={auditResult.reasons} />

          {/* Status Metrics Cards Grid */}
          <div className="stat-grid">
            {/* Overall Compliance */}
            {auditResult.compliance?.overall_status && (
              <StatCard 
                title="Overall Compliance" 
                value={auditResult.compliance.overall_status.replace('_', ' ').toUpperCase()} 
                description="Synthesized compliance analysis decision"
                icon={ShieldCheck}
              />
            )}
            
            {/* Overall Risk */}
            {auditResult.risk?.overall_risk_level && (
              <StatCard 
                title="Vulnerability Risk" 
                value={`${auditResult.risk.overall_risk_level.toUpperCase()} (${auditResult.risk.overall_risk_score}/100)`} 
                description="Calculated finding security risk level"
                icon={AlertTriangle}
              />
            )}

            {/* Confidence Indicators */}
            {status === 'review_required' ? (
              <>
                <ConfidenceIndicator 
                  confidence={auditResult.retrieval_confidence} 
                  title="Retrieval Confidence" 
                />
                <ConfidenceIndicator 
                  confidence={auditResult.compliance_confidence} 
                  title="Compliance Confidence" 
                />
              </>
            ) : (
              auditResult.retrieval?.confidence !== undefined && (
                <ConfidenceIndicator 
                  confidence={auditResult.retrieval.confidence} 
                  level={auditResult.retrieval.confidence_level}
                  title="Overall RAG Confidence" 
                />
              )
            )}
          </div>

          {/* Sub-node details layout */}
          {status === 'completed' && (
            <>
              {/* Planner Scope */}
              <PlannerResult planner={auditResult.planner} />

              {/* Findings */}
              <ComplianceResults compliance={auditResult.compliance} />

              {/* Risk details */}
              <RiskResults risk={auditResult.risk} />

              {/* Recommendations */}
              <RecommendationResults recommendations={auditResult.recommendations} />

              {/* Evidence Chunks */}
              <RetrievalResults retrieval={auditResult.retrieval} />
            </>
          )}

          {/* Terminal review/rejected placeholder panels */}
          {status !== 'completed' && (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">
                  <Layers size={18} style={{ color: 'var(--accent-gold)' }} />
                  <span>Workflow Execution Context</span>
                </h3>
              </div>
              <div className="card-body">
                <p style={{ margin: '0 0 16px 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  This audit query cannot display findings, risks, or recommendations in the workspace as it is not finalized.
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', backgroundColor: 'var(--bg-primary)', padding: '16px', borderRadius: '6px', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>THREAD SESSION ID</div>
                    <div style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', wordBreak: 'break-all' }}>{auditResult.thread_id || auditResult.audit_id}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>HUMAN REVIEW ID</div>
                    <div style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', wordBreak: 'break-all' }}>{auditResult.review_id || 'Review ID unavailable'}</div>
                  </div>
                </div>
                {status === 'review_required' && (
                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    {auditResult.review_id ? (
                      <button 
                        className="btn btn-primary" 
                        onClick={() => navigate(`/reviews/${auditResult.review_id}`)}
                        style={{ width: 'auto' }}
                      >
                        <UserCheck size={14} />
                        <span>Open Review Workspace</span>
                      </button>
                    ) : (
                      <div style={{ color: 'var(--status-error)', fontSize: '0.85rem', fontWeight: 600 }}>
                        Review information unavailable.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </PageContainer>
  );
}
