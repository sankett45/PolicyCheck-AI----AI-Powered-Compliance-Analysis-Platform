import React from 'react';
import { BarChart3, AlertTriangle } from 'lucide-react';

/**
 * Renders the risk distribution overview empty state.
 */
export default function RiskOverview() {
  return (
    <section className="card">
      <div className="card-header">
        <h3 className="card-title">
          <BarChart3 size={18} />
          <span>Risk Overview</span>
        </h3>
      </div>
      <div className="card-body">
        <div className="empty-state">
          <AlertTriangle className="empty-state-icon" />
          <h4 className="empty-state-title">No risk data available</h4>
          <p className="empty-state-desc">
            Submit compliance audits to generate risk assessments and mapping views.
          </p>
        </div>
      </div>
    </section>
  );
}
