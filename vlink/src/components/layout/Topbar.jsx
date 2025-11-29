import React from 'react';
import { useAuth } from '../../context/AuthContext';

export default function Topbar({ title }) {
  const { user } = useAuth();
  
  // Use a reliable avatar generator based on the user's name
  // If user.name is "Student User", this generates an image with "SU"
  const avatarUrl = user?.name 
    ? `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=2563eb&color=fff`
    : 'https://ui-avatars.com/api/?name=User&background=333&color=fff';

  return (
    <header className="topbar">
      <h1>{title}</h1>
      <div className="topbar-right">
        <div className="status-indicator">
          <span className="dot"></span> Online
        </div>
        <div className="user-profile">
          <img src={avatarUrl} alt="User" className="avatar" />
          <div className="user-info">
            <span className="name">{user?.name}</span>
            <span className="role">{user?.role}</span>
          </div>
        </div>
      </div>
    </header>
  );
}