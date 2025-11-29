import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { FaHome, FaChalkboardTeacher, FaTasks, FaFolder, FaUser, FaSignOutAlt, FaComments } from 'react-icons/fa';

// NOTE: The 'export default' below is critical for the import to work in Layout.jsx
export default function Sidebar({ isOpen }) {
  const location = useLocation();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <FaHome /> },
    { name: 'Classes', path: '/classes', icon: <FaChalkboardTeacher /> },
    { name: 'Assignments', path: '/assignments', icon: <FaTasks /> },
    { name: 'Discussions', path: '/discussions', icon: <FaComments /> }, 
    { name: 'Files', path: '/files', icon: <FaFolder /> },
    { name: 'Profile', path: '/profile', icon: <FaUser /> },
  ];

  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h2 style={{color: 'white', margin: 0}}>Vlink Enhanced</h2>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <Link 
            key={item.path} 
            to={item.path} 
            className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            {item.icon}
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div onClick={handleLogout} className="sidebar-link logout-btn">
          <FaSignOutAlt />
          <span>Logout</span>
        </div>
      </div>
    </div>
  );
}