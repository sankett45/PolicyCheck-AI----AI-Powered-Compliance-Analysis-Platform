import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  AlertTriangle, 
  UserCheck, 
  FileSpreadsheet, 
  Plus 
} from 'lucide-react';

import PageContainer from '../components/layout/PageContainer';
import StatCard from '../components/dashboard/StatCard';
import RecentAudits from '../components/dashboard/RecentAudits';
import RiskOverview from '../components/dashboard/RiskOverview';

export default function Dashboard() {
  const navigate = useNavigate();

  // CTA button navigating to Audits page
  const headerAction = (
    <button className="btn btn-primary" onClick={() => navigate('/audits')}>
      <Plus size={16} />
      <span>Start New Audit</span>
    </button>
  );

  return (
    <PageContainer 
      title="Dashboard" 
      subtitle="Monitor compliance audits, risks, reviews, and reports."
      action={headerAction}
    >
      {/* Metric Cards Grid */}
      <div className="stat-grid">
        <StatCard 
          title="Total Audits" 
          value="—" 
          description="Compliance execution history count"
          icon={ShieldCheck}
        />
        <StatCard 
          title="High Risk Gaps" 
          value="—" 
          description="Controls requiring immediate patching"
          icon={AlertTriangle}
        />
        <StatCard 
          title="Pending HITL Reviews" 
          value="—" 
          description="Audit operator decisions required"
          icon={UserCheck}
        />
        <StatCard 
          title="Synthesized Reports" 
          value="—" 
          description="Final compliance artifacts generated"
          icon={FileSpreadsheet}
        />
      </div>

      {/* Main Dashboard Layout Grid */}
      <div className="dashboard-grid">
        <RecentAudits />
        <RiskOverview />
      </div>
    </PageContainer>
  );
}
