import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { api } from '../../services/api';

export default function Navbar({ onToggleSidebar }) {
  const location = useLocation();
  const [apiStatus, setApiStatus] = useState('connecting'); // 'connected' | 'connecting' | 'unavailable'

  // Map pathnames to human-readable titles
  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/':
        return 'Dashboard';
      case '/audits':
        return 'Compliance Audits';
      case '/documents':
        return 'Documents & Evidence';
      case '/reviews':
        return 'Reviews & HITL';
      case '/reports':
        return 'Synthesized Reports';
      default:
        return 'AuditFlow AI';
    }
  };

  useEffect(() => {
    let active = true;

    const checkHealth = async () => {
      try {
        const response = await fetch(`${api.getBaseUrl()}/health`);
        if (!response.ok) {
          throw new Error('Health check non-2xx response');
        }
        const data = await response.json();
        
        if (active) {
          if (data.status === 'healthy') {
            setApiStatus('connected');
          } else {
            // Unhealthy but reachable
            setApiStatus('connected'); // Still connected to the server
          }
        }
      } catch (error) {
        if (active) {
          setApiStatus('unavailable');
        }
      }
    };

    // Initial check
    checkHealth();

    // Poll status every 5 seconds
    const intervalId = setInterval(checkHealth, 5000);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  return (
    <header className="navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button 
          className="navbar-mobile-toggle" 
          onClick={onToggleSidebar}
          aria-label="Toggle navigation menu"
        >
          <Menu size={20} />
        </button>
        <h1 className="navbar-title" style={{ margin: 0, fontSize: '1.2rem' }}>
          {getPageTitle(location.pathname)}
        </h1>
      </div>

      <div className="navbar-actions">
        <div className="api-status">
          <span className={`api-status-dot ${apiStatus}`}></span>
          <span>
            API: {apiStatus === 'connected' ? 'Connected' : apiStatus === 'connecting' ? 'Connecting' : 'Unavailable'}
          </span>
        </div>

        <div className="user-profile-mock" title="User Profile Placeholder">
          AD
        </div>
      </div>
    </header>
  );
}
