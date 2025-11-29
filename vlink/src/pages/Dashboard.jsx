import { useEffect, useState } from 'react';
import { getDashboardData } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getDashboardData().then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  const liveClass = data.classes.find(c => c.status === 'live');

  return (
    <div>
      {/* Stats Grid */}
      <div className="grid-4">
        <div className="card stat-card">
          <div><p style={{color:'#888'}}>Live Classes</p><p className="stat-value">{data.dashboard.live}</p></div>
          <div style={{color: '#16a34a', fontSize: '1.5rem'}}>●</div>
        </div>
        <div className="card stat-card">
          <div><p style={{color:'#888'}}>Upcoming</p><p className="stat-value">{data.dashboard.upcoming}</p></div>
          <div style={{color: '#2563eb', fontSize: '1.5rem'}}>⏳</div>
        </div>
        <div className="card stat-card">
          <div><p style={{color:'#888'}}>Completed</p><p className="stat-value">{data.dashboard.completed}</p></div>
          <div style={{color: '#9333ea', fontSize: '1.5rem'}}>✓</div>
        </div>
        <div className="card stat-card">
          <div><p style={{color:'#888'}}>Pending</p><p className="stat-value">{data.dashboard.pending}</p></div>
          <div style={{color: '#ea580c', fontSize: '1.5rem'}}>!</div>
        </div>
      </div>

      {/* Live Class Widget */}
      {liveClass && (
        <div className="card" style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3><span className="live-badge"></span> {liveClass.title}</h3>
            <p style={{ color: '#888' }}>{liveClass.teacher} • {liveClass.participants} watching</p>
          </div>
          <button className="btn btn-success" onClick={() => navigate(`/classroom/${liveClass.id}`)}>
            Join Class
          </button>
        </div>
      )}
    </div>
  );
}