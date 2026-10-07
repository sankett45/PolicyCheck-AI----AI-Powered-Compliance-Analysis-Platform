import React from 'react';
import { ClipboardList, ShieldAlert } from 'lucide-react';

/**
 * Renders the recent compliance audit list empty state.
 */
export default function RecentAudits() {
  return (
    <section className="card">
      <div className="card-header">
        <h3 className="card-title">
          <ClipboardList size={18} />
          <span>Recent Audits</span>
        </h3>
      </div>
      <div className="card-body">
        <div className="empty-state">
          <ShieldAlert className="empty-state-icon" />
          <h4 className="empty-state-title">No audits yet</h4>
          <p className="empty-state-desc">
            Start your first compliance audit to see results here.
          </p>
        </div>
      </div>
    </section>
  );
}
