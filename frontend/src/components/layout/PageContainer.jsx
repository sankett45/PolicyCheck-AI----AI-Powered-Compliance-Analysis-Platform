import React from 'react';

/**
 * Reusable container wrapping pages, composing titles, subtitles, action CTAs, and children.
 * 
 * @param {string} title - Page heading.
 * @param {string} subtitle - Description text displayed under title.
 * @param {React.ReactNode} action - Optional CTA action element (e.g. Button) to render on the right.
 * @param {React.ReactNode} children - Core page elements.
 */
export default function PageContainer({ title, subtitle, action, children }) {
  return (
    <div className="page-container">
      {(title || subtitle || action) && (
        <div className="page-header">
          <div>
            {title && <h2 className="page-header-title">{title}</h2>}
            {subtitle && <p className="page-header-subtitle">{subtitle}</p>}
          </div>
          {action && <div className="page-header-action">{action}</div>}
        </div>
      )}
      <main className="page-content">{children}</main>
    </div>
  );
}
