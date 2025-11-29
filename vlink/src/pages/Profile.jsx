import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile'); // profile, preferences, network, data

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="grid-4" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div><p style={{color:'#888'}}>Full Name</p><p>{user?.name}</p></div>
            <div><p style={{color:'#888'}}>Role</p><p>{user?.role}</p></div>
            <div><p style={{color:'#888'}}>Class</p><p>{user?.class || 'N/A'}</p></div>
            <div><p style={{color:'#888'}}>ID</p><p>{user?.roll || 'N/A'}</p></div>
          </div>
        );
      case 'preferences':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#111', padding: '15px', borderRadius: '8px' }}>
              <div><p>Push Notifications</p><small style={{color:'#888'}}>Receive alerts for classes</small></div>
              <button className="btn btn-success" style={{ padding: '5px 15px' }}>Enabled</button>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#111', padding: '15px', borderRadius: '8px' }}>
              <div><p>Auto Download</p><small style={{color:'#888'}}>Download on Wi-Fi only</small></div>
              <button className="btn" style={{ padding: '5px 15px', background: '#444' }}>Disabled</button>
            </div>
          </div>
        );
      default:
        return <p style={{ color: '#888', textAlign: 'center', padding: '20px' }}>This section is under development.</p>;
    }
  };

  return (
    <div className="card">
      {/* Tabs Navigation */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px', background: '#111', padding: '5px', borderRadius: '8px' }}>
        {['profile', 'preferences', 'network', 'data'].map(tab => (
          <button 
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{ 
              flex: 1, 
              padding: '10px', 
              background: activeTab === tab ? '#2b2b2b' : 'transparent', 
              border: 'none', 
              color: activeTab === tab ? '#fff' : '#888', 
              borderRadius: '6px', 
              cursor: 'pointer',
              fontWeight: activeTab === tab ? 'bold' : 'normal',
              textTransform: 'capitalize'
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
}