import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle, AlertCircle, HelpCircle } from 'lucide-react';
import StatCard from '../dashboard/StatCard';

export default function ReportSummary({ complianceStatus, riskLevel, riskScore }) {
  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'compliant':
        return { label: 'COMPLIANT', color: 'var(--status-success)', Icon: CheckCircle2 };
      case 'non_compliant':
        return { label: 'NON-COMPLIANT', color: 'var(--status-error)', Icon: XCircle };
      case 'partially_compliant':
        return { label: 'PARTIALLY COMPLIANT', color: 'var(--status-warning)', Icon: AlertCircle };
      default:
        return { label: 'INSUFFICIENT EVIDENCE', color: 'var(--text-secondary)', Icon: HelpCircle };
    }
  };

  const badge = getStatusBadge(complianceStatus);

  return (
    <div className="stat-grid" style={{ marginBottom: '24px' }}>
      
      {/* Overall Compliance */}
      <StatCard 
        title="Compliance Decision" 
        value={badge.label} 
        description="Synthesized regulatory evaluation state"
        icon={badge.Icon}
        style={{ borderTop: `4px solid ${badge.color}` }}
      />

      {/* Posture Risk Level */}
      <StatCard 
        title="Vulnerability Posture" 
        value={riskLevel?.toUpperCase() || 'LOW'} 
        description="Calculated security posture risk level"
        icon={AlertTriangle}
      />

      {/* Posture Risk Score */}
      <StatCard 
        title="Vulnerability Score" 
        value={`${riskScore || 0}/125`} 
        description="Aggregated risk metrics score (0-125)"
        icon={ShieldCheck}
      />

    </div>
  );
}
