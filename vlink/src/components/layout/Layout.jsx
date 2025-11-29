import React, { useState } from 'react';
// This import requires Sidebar.jsx to have 'export default'
import Sidebar from './Sidebar'; 
import Topbar from './Topbar';
import { useLocation } from 'react-router-dom';

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true); 
  const location = useLocation();

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    // Capitalize first letter of route
    return path.substring(1).charAt(0).toUpperCase() + path.slice(2);
  };

  return (
    <div className="app-container">
      <Sidebar isOpen={sidebarOpen} />
      <div className="main-content">
        <Topbar title={getPageTitle()} />
        {children}
      </div>
    </div>
  );
}