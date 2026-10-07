import React from 'react';
import { ShieldCheck, AlertTriangle } from 'lucide-react';
import StatCard from '../dashboard/StatCard';
import ConfidenceIndicator from '../audit/ConfidenceIndicator';

export default function ReviewSummary({ retrievalConfidence, complianceConfidence, riskLevel, riskScore }) {
  return (
    <div className="stat-grid" style={{ marginBottom: '24px' }}>
      {/* Posture Risk */}
      <StatCard 
        title="Vulnerability Posture" 
        value={`${riskLevel?.toUpperCase() || 'LOW'} (${riskScore || 0}/100)`} 
        description="Assessed risk of identified control gaps"
        icon={AlertTriangle}
      />

      {/* Retrieval Confidence */}
      <ConfidenceIndicator 
        confidence={retrievalConfidence} 
        title="Retrieval Confidence" 
      />

      {/* Compliance Confidence */}
      <ConfidenceIndicator 
        confidence={complianceConfidence} 
        title="Compliance Confidence" 
      />
    </div>
  );
}
