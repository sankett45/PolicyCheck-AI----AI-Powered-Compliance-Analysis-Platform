import React from 'react';

/**
 * Reusable stat scorecard component.
 * 
 * @param {string} title - The title of the metric.
 * @param {string|number} value - The current value to display (e.g. "—").
 * @param {string} description - Brief description or contextual metadata.
 * @param {React.ComponentType} icon - Lucide Icon to render.
 */
export default function StatCard({ title, value, description, icon: Icon }) {
  return (
    <section className="stat-card">
      <div className="stat-card-header">
        <span>{title}</span>
        {Icon && (
          <div className="stat-card-icon-wrapper">
            <Icon size={16} />
          </div>
        )}
      </div>
      <div className="stat-card-value">{value}</div>
      {description && <div className="stat-card-desc">{description}</div>}
    </section>
  );
}
