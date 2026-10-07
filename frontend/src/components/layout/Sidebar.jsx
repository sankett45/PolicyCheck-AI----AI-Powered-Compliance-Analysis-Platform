import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ShieldCheck, 
  FileText, 
  UserCheck, 
  ClipboardList, 
  X 
} from 'lucide-react';

export default function Sidebar({ isOpen, onClose }) {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/audits', label: 'Audits', icon: ShieldCheck },
    { path: '/documents', label: 'Documents', icon: FileText },
    { path: '/reviews', label: 'Reviews', icon: UserCheck },
    { path: '/reports', label: 'Reports', icon: ClipboardList }
  ];

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-brand">
        <div className="sidebar-title">
          AuditFlow <span className="logo-highlight">AI</span>
        </div>
        <div className="sidebar-subtitle">AI Compliance & Audit</div>
        {isOpen && (
          <button 
            className="navbar-mobile-toggle" 
            onClick={onClose} 
            style={{ position: 'absolute', right: '16px', top: '24px' }}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        )}
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
              onClick={onClose}
            >
              <Icon className="sidebar-link-icon" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div>v1.0.0</div>
        <div style={{ marginTop: '2px', fontSize: '0.65rem' }}>Enterprise Audit System</div>
      </div>
    </aside>
  );
}
