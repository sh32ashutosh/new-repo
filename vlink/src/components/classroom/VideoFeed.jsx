import React from 'react';
import { FaMicrophone, FaMicrophoneSlash, FaVideo, FaVideoSlash } from 'react-icons/fa';

export default function VideoFeed({ 
  isLowDataMode, 
  userVideoRef, 
  isMicOn = true, 
  isCamOn = true, 
  onToggleMic, 
  onToggleCam 
}) {
  return (
    <div 
      className="video-feed-container" 
      style={{ 
        height: '200px', 
        background: 'black', 
        borderRadius: '8px', 
        overflow: 'hidden', 
        position: 'relative', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        marginBottom: '20px'
      }}
    >
      {isLowDataMode ? (
        <div style={{ textAlign: 'center', color: '#9ca3af' }}>
          <div style={{ fontSize: '3rem', animation: 'pulse 1s infinite' }}>🎤</div>
          <p>Audio Only Mode</p>
        </div>
      ) : (
        <video 
          ref={userVideoRef} 
          autoPlay 
          playsInline 
          muted 
          style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
        />
      )}

      {/* Controls Overlay */}
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '50%',
        transform: 'translateX(-50%)',
        display: 'flex',
        gap: '10px',
        zIndex: 10
      }}>
        <button 
          onClick={onToggleMic}
          style={{
            background: isMicOn ? 'rgba(0,0,0,0.6)' : '#dc2626',
            border: 'none',
            borderRadius: '50%',
            width: '35px',
            height: '35px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            cursor: 'pointer',
            transition: 'background 0.2s'
          }}
          title={isMicOn ? "Mute" : "Unmute"}
        >
          {isMicOn ? <FaMicrophone size={14} /> : <FaMicrophoneSlash size={14} />}
        </button>

        <button 
          onClick={onToggleCam}
          style={{
            background: isCamOn ? 'rgba(0,0,0,0.6)' : '#dc2626',
            border: 'none',
            borderRadius: '50%',
            width: '35px',
            height: '35px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            cursor: 'pointer',
            transition: 'background 0.2s'
          }}
          title={isCamOn ? "Turn Off Camera" : "Turn On Camera"}
        >
          {isCamOn ? <FaVideo size={14} /> : <FaVideoSlash size={14} />}
        </button>
      </div>
    </div>
  );
}