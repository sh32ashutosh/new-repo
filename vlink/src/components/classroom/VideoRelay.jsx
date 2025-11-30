import React, { useState } from 'react';
import { API_BASE_URL } from '../../services/config';

export default function VideoRelay({ isTeacher }) {
  const [inputUrl, setInputUrl] = useState('');
  const [streamUrl, setStreamUrl] = useState('');

  const handleStream = () => {
    if (!inputUrl) return;
    
    // Construct the Local Proxy URL
    // API_BASE_URL is like 'http://192.168.1.5:5000/api'
    // We want: 'http://192.168.1.5:5000/api/stream-proxy?url=...'
    const proxyUrl = `${API_BASE_URL}/stream-proxy?url=${encodeURIComponent(inputUrl)}`;
    
    setStreamUrl(proxyUrl);
  };

  return (
    <div className="card" style={{ marginTop: '15px', padding: '15px', border: '1px solid #333' }}>
      <h3 style={{fontSize: '1rem', marginBottom: '10px'}}>🌐 LAN Video Relay (Teacher Only)</h3>
      
      {isTeacher && (
        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px', flexDirection: 'column' }}>
          <input 
            className="input-field" 
            placeholder="Paste Internet MP4 Link..." 
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            style={{ fontSize: '0.8rem' }}
          />
          <button className="btn btn-primary" onClick={handleStream} style={{ fontSize: '0.8rem', padding: '5px' }}>
            Stream to Class
          </button>
        </div>
      )}

      {streamUrl && (
        <div>
          <p style={{ color: '#16a34a', fontSize: '0.8rem', marginBottom: '5px' }}>
            ⚡ Streaming via Local Network
          </p>
          <video 
            src={streamUrl} 
            controls 
            autoPlay 
            style={{ width: '100%', borderRadius: '8px', border: '1px solid #444' }} 
          />
        </div>
      )}
      
      {!isTeacher && !streamUrl && (
        <p style={{color: '#666', fontSize: '0.9rem'}}>Waiting for teacher to stream content...</p>
      )}
    </div>
  );
}