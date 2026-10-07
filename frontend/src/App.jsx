import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Dashboard from './pages/Dashboard';
import Audits from './pages/Audits';
import Documents from './pages/Documents';
import Reviews from './pages/Reviews';
import Reports from './pages/Reports';

/**
 * Reusable layout composition framework containing Sidebar, Navbar, and children containers.
 */
function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="app-layout">
      {/* Click-away backdrop overlay for collapsible mobile sidebar view */}
      {sidebarOpen && (
        <div 
          onClick={closeSidebar}
          style={{
            position: 'fixed',
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            zIndex: 95,
          }}
          role="presentation"
        />
      )}

      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      
      <div className="main-wrapper">
        <Navbar onToggleSidebar={toggleSidebar} />
        {children}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/audits" element={<Audits />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/reviews" element={<Reviews />} />
          <Route path="/reviews/:reviewId" element={<Reviews />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/reports/:reportId" element={<Reports />} />
          {/* Default fallback route matching redirects to Dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}
