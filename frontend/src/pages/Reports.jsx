import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  FileText, 
  Search, 
  AlertTriangle, 
  ArrowLeft,
  Calendar
} from 'lucide-react';

import PageContainer from '../components/layout/PageContainer';
import ReportHeader from '../components/reports/ReportHeader';
import ExecutiveSummary from '../components/reports/ExecutiveSummary';
import ReportSummary from '../components/reports/ReportSummary';
import FindingsTable from '../components/reports/FindingsTable';
import RiskTable from '../components/reports/RiskTable';
import RecommendationList from '../components/reports/RecommendationList';
import EvidenceSummary from '../components/reports/EvidenceSummary';
import HumanReviewDetails from '../components/reports/HumanReviewDetails';
import ReportActions from '../components/reports/ReportActions';
import { reportApi } from '../services/reportApi';

// Mock Fixture context for presentation testing (Groq rate-limit guard)
const MOCK_REPORT_FIXTURE = {
  report_id: 'mock_report_123',
  audit_id: 'mock_audit_987',
  question: 'Is our access control policy compliant with ISO 27001?',
  audit_type: 'regulatory_compliance',
  subject: 'access_control_policy',
  regulation: 'ISO 27001',
  executive_summary: 'The administrative access controls were evaluated. While single sign-on is active, conditional Access Controls and mandatory Multi-Factor Authentication (MFA) are missing on AWS root console accounts. These gaps represent high security vulnerabilities.',
  overall_compliance_status: 'non_compliant',
  overall_risk_level: 'high',
  overall_risk_score: 80,
  findings: [
    {
      finding_id: 'find_mfa_001',
      control: 'Multi-Factor Authentication',
      status: 'non_compliant',
      company_requirement: 'MFA must be enforced for all administrator sessions access platforms.',
      regulatory_requirement: 'ISO 27001 Control A.9.4.2 requires secure log-on procedures.',
      reasoning: 'Although SSO is implemented, AWS administrative root accounts do not require mandatory MFA.',
      evidence_citations: ['access_control_policy.txt:L10']
    }
  ],
  risk_assessments: [
    {
      finding_id: 'find_mfa_001',
      control: 'Multi-Factor Authentication',
      risk_level: 'high',
      risk_score: 80,
      severity: '4',
      likelihood: '4',
      impact: '5',
      rationale: 'Absence of MFA on administrator console logins exposes credentials to phishing and hijacking.'
    }
  ],
  recommendations: [
    {
      finding_id: 'find_mfa_001',
      control: 'Multi-Factor Authentication',
      priority: 'high',
      recommendation: 'Configure active conditional access policies to require MFA for aws-admin privileges.',
      rationale: 'Mandatory MFA reduces hijacked credential risks by 99%.',
      implementation_steps: [
        'Enforce block rule on admin logins without active security keys.',
        'Enroll AWS console users in hardware token policies.'
      ],
      evidence: ['access_control_policy.txt']
    }
  ],
  evidence_summary: [
    {
      document_id: '3351389a-3b73-484f-8db8-38049377558b',
      document_version: '1.0.0',
      filename: 'access_control_policy.txt',
      document_type: 'company_policy',
      page_number: 1,
      chunk_index: 0,
      similarity_score: 0.85,
      text: 'SSO is configured for developer logins. Administrative aws console logins bypass local SSO validation structures.',
      source: 'local/access_control_policy.txt'
    }
  ],
  human_review: {
    review_status: 'approved',
    reviewer_decision: 'approve',
    reviewer_comment: 'Approved audit output. Confirmed AWS root console gap is critical remediation target.',
    timestamp: new Date().toISOString()
  },
  generated_at: new Date().toISOString(),
  report_version: 1,
  status: 'final'
};

export default function Reports() {
  const { reportId } = useParams();
  const navigate = useNavigate();

  // Search/Lookup state
  const [inputId, setInputId] = useState('');
  const [searchError, setSearchError] = useState(null);

  // Report details state
  // Report details state
  const [report, setReport] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(false);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [error, setError] = useState(null);
  const [evidenceError, setEvidenceError] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);

  const fetchReport = async (id) => {
    setLoading(true);
    setError(null);
    setReport(null);
    setEvidence([]);
    setEvidenceError(null);
    setDownloadError(null);

    // Sandbox Mock Toggle
    if (import.meta.env.DEV && id === 'mock_report_123') {
      setTimeout(() => {
        setReport(MOCK_REPORT_FIXTURE);
        setLoading(false);
        
        // Simulate evidence loading separately
        setEvidenceLoading(true);
        setTimeout(() => {
          setEvidence(MOCK_REPORT_FIXTURE.evidence_summary);
          setEvidenceLoading(false);
        }, 500);
      }, 600);
      return;
    }

    try {
      // 1. Fetch Report Details
      const data = await reportApi.getReport(id);
      setReport(data);
      setLoading(false);

      // 2. Fetch Evidence Details separately
      setEvidenceLoading(true);
      try {
        const evidenceData = await reportApi.getReportEvidence(id);
        setEvidence(evidenceData || []);
      } catch (evErr) {
        setEvidenceError('Evidence unavailable: The report was loaded, but evidence references could not be retrieved.');
      } finally {
        setEvidenceLoading(false);
      }
    } catch (err) {
      setError('Report not found: The requested audit report could not be located.');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (reportId) {
      fetchReport(reportId);
    }
  }, [reportId]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const id = inputId.trim();
    if (!id) {
      setSearchError('Please enter a valid report ID.');
      return;
    }
    setSearchError(null);
    navigate(`/reports/${id}`);
  };

  const handleDownload = async () => {
    if (!reportId) return;
    setDownloadLoading(true);
    setDownloadError(null);

    // Sandbox Mock Download
    if (import.meta.env.DEV && reportId === 'mock_report_123') {
      setTimeout(() => {
        try {
          const mdText = `# Audit Report: Access Control Policy
**Question:** ${MOCK_REPORT_FIXTURE.question}
- **Report ID:** ${MOCK_REPORT_FIXTURE.report_id}
- **Audit ID:** ${MOCK_REPORT_FIXTURE.audit_id}
- **Status:** FINAL
- **Executive Summary:** ${MOCK_REPORT_FIXTURE.executive_summary}
- **Overall compliance status:** NON_COMPLIANT
- **Risk score:** 80/125`;
          const blob = new Blob([mdText], { type: 'text/markdown' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `audit_report_mock_report_123.md`;
          document.body.appendChild(a);
          a.click();
          a.remove();
        } catch (err) {
          setDownloadError('Download failed: The report could not be downloaded. Please try again.');
        } finally {
          setDownloadLoading(false);
        }
      }, 1000);
      return;
    }

    try {
      await reportApi.downloadReport(reportId);
    } catch (err) {
      setDownloadError('Download failed: The report could not be downloaded. Please try again.');
    } finally {
      setDownloadLoading(false);
    }
  };

  const handleBackToAudits = () => {
    navigate('/audits');
  };

  // Header actions
  const headerAction = reportId ? (
    <button className="btn btn-secondary" onClick={() => navigate('/reports')} style={{ width: 'auto' }}>
      <ArrowLeft size={16} />
      <span>All Reports</span>
    </button>
  ) : null;

  return (
    <PageContainer
      title="Audit Reports"
      subtitle="Inspect finalized reports and evidence-backed compliance scorecards."
      action={headerAction}
    >
      {/* STATE 1: No Report Selected */}
      {!reportId && (
        <div className="card" style={{ maxWidth: '540px', margin: '40px auto' }}>
          <div className="card-header">
            <h3 className="card-title">
              <FileText size={18} style={{ color: 'var(--accent-gold)' }} />
              <span>Inspect Audit Report</span>
            </h3>
          </div>
          <form onSubmit={handleSearchSubmit}>
            <div className="card-body">
              <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Finalized and approved compliance audits generate a persistent Report ID. Enter the ID to load the report workspace.
              </p>
              
              <div className="form-group">
                <label className="form-label" htmlFor="search-report-id">Report Request ID</label>
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
                    id="search-report-id"
                    type="text"
                    className="form-control"
                    placeholder="Enter Report UUID (or type 'mock_report_123' for sandbox)"
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
                <span>Load Report Workspace</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* STATE 2: Loading State */}
      {loading && reportId && (
        <div className="card" style={{ maxWidth: '640px', margin: '40px auto' }}>
          <div className="loader-container">
            <div className="spinner"></div>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Loading report...</div>
          </div>
        </div>
      )}

      {/* STATE 3: Error State */}
      {error && !loading && reportId && (
        <div style={{ maxWidth: '640px', margin: '40px auto' }}>
          <div className="error-container">
            <AlertTriangle className="error-icon" />
            <div>
              <h4 className="error-title">Report Retrieval Error</h4>
              <p className="error-desc">{error}</p>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button className="btn btn-secondary" onClick={() => navigate('/reports')}>
              Return to Search
            </button>
          </div>
        </div>
      )}

      {/* STATE 4: Workspace Loaded */}
      {!loading && !error && report && reportId && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Metadata Header */}
          <ReportHeader 
            reportId={report.report_id}
            auditId={report.audit_id}
            status={report.status}
            version={report.report_version}
            generatedAt={report.generated_at}
            auditType={report.audit_type}
            subject={report.subject}
            regulation={report.regulation}
          />

          {/* Action Row */}
          <ReportActions 
            onDownload={handleDownload}
            onBack={handleBackToAudits}
            downloading={downloadLoading}
          />

          {/* Download Error Alert */}
          {downloadError && (
            <div className="error-container" style={{ margin: 0 }}>
              <AlertTriangle className="error-icon" />
              <div>
                <h4 className="error-title">Download Error</h4>
                <p className="error-desc">{downloadError}</p>
              </div>
            </div>
          )}

          {/* Original Question Card */}
          <div className="card" style={{ borderLeft: '4px solid var(--accent-gold)' }}>
            <div className="card-body" style={{ padding: '20px 24px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                AUDIT COMPLIANCE QUESTION
              </div>
              <p style={{ margin: 0, fontSize: '1.05rem', fontWeight: 500, color: 'var(--text-primary)', wordBreak: 'break-word' }}>
                "{report.question}"
              </p>
            </div>
          </div>

          {/* Executive Summary Section */}
          <ExecutiveSummary summary={report.executive_summary} />

          {/* Overall posturing summary */}
          <ReportSummary 
            complianceStatus={report.overall_compliance_status}
            riskLevel={report.overall_risk_level}
            riskScore={report.overall_risk_score}
          />

          {/* Detailed findings */}
          <FindingsTable findings={report.findings} />

          {/* Detailed risk assessments */}
          <RiskTable riskAssessments={report.risk_assessments} />

          {/* Actions remediation recommendations */}
          <RecommendationList recommendations={report.recommendations} />

          {/* Traceable RAG sources */}
          {evidenceLoading ? (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Traceable Evidence Sources</h3>
              </div>
              <div className="card-body">
                <div className="loader-container" style={{ padding: '24px 0' }}>
                  <div className="spinner"></div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Loading evidence...</div>
                </div>
              </div>
            </div>
          ) : evidenceError ? (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Traceable Evidence Sources</h3>
              </div>
              <div className="card-body">
                <div className="error-container" style={{ margin: 0 }}>
                  <AlertTriangle className="error-icon" />
                  <div>
                    <h4 className="error-title">Evidence Loading Failure</h4>
                    <p className="error-desc">{evidenceError}</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <EvidenceSummary evidenceSummary={evidence} />
          )}

          {/* Human review audit trail logs */}
          <HumanReviewDetails humanReview={report.human_review} />

        </div>
      )}
    </PageContainer>
  );
}
