import React, { useRef, useState, useEffect } from 'react';
import Peer from 'simple-peer';
import { useAuth } from '../context/AuthContext';
import { sendDrawData } from '../services/api';
import { connectSocket } from '../services/socketAdapter';

// Components
import Whiteboard from '../components/classroom/Whiteboard';
import ToolsPanel from '../components/classroom/ToolsPanel';
import VideoFeed from '../components/classroom/VideoFeed';
import P2PVideoSharer from '../components/classroom/P2PVideoSharer';
import VideoRelay from '../components/classroom/VideoRelay'; 

export default function LiveClassroom() {
  const { user } = useAuth();
  const isTeacher = user?.role === 'teacher';

  // --- STATE ---
  const [lines, setLines] = useState([]);
  const linesRef = useRef([]); // Ref to track lines synchronously
  
  const [tool, setTool] = useState('pen'); 
  
  // Media State
  const [stream, setStream] = useState(null);
  const [lowBandwidth, setLowBandwidth] = useState(false);
  const [isMicOn, setIsMicOn] = useState(true);
  const [isCamOn, setIsCamOn] = useState(true);

  // P2P Host State
  const [iAmHost, setIAmHost] = useState(false);
  
  // Content Mode: 'p2p' (File Share) or 'relay' (Internet Stream)
  const [shareMode, setShareMode] = useState('relay'); 

  // Layout State
  const canvasWrapperRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Refs
  const userVideo = useRef();
  const socket = useRef(); // Socket instance reference
  const peerRef = useRef(); 
  const [mediaError, setMediaError] = useState(null); // Store camera errors

  // --- RESPONSIVE CANVAS SIZING ---
  useEffect(() => {
    if (!canvasWrapperRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 10 && height > 10) setDimensions({ width, height });
      }
    });
    resizeObserver.observe(canvasWrapperRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // --- WEB RTC & SOCKET SETUP ---
  useEffect(() => {
    let myStream = null; 
    let isMounted = true; 

    // SAFETY CHECK: Ensure browser supports mediaDevices
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setMediaError("HTTPS Required: Browser blocked camera. Please use 'https://' in URL.");
        return;
    }

    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then((currentStream) => {
        if (!isMounted) {
            currentStream.getTracks().forEach(track => track.stop());
            return;
        }

        setMediaError(null); // Clear errors on success
        myStream = currentStream;
        setStream(currentStream);
        
        if (userVideo.current) {
          userVideo.current.srcObject = currentStream;
        }
        
        socket.current = connectSocket();

        if (isTeacher) {
            const peer = new Peer({ initiator: true, trickle: false, stream: currentStream });
            peerRef.current = peer; 
            
            peer.on('signal', (data) => {
                if (isMounted && socket.current) {
                    socket.current.emit('callUser', { signalData: data, from: user.id });
                }
            });

            if (socket.current) {
                socket.current.on('callAccepted', (signal) => {
                    peer.signal(signal);
                });
            }
        } else {
            if (socket.current) {
                socket.current.on('callUser', (data) => {
                     const peer = new Peer({ initiator: false, trickle: false, stream: currentStream });
                     peerRef.current = peer; 

                     peer.on('signal', (data) => {
                        if (isMounted && socket.current) {
                            socket.current.emit('answerCall', { signal: data });
                        }
                     });
                     peer.signal(data.signalData);
                     peer.on('stream', (teacherStream) => {
                        if (isMounted && userVideo.current) {
                          userVideo.current.srcObject = teacherStream;
                        }
                     });
                });
            }
        }
      })
      .catch(err => {
        if (isMounted) {
            console.error("Media Error:", err);
            setMediaError("Camera Access Denied: Check browser permissions.");
        }
      });
      
      return () => {
        isMounted = false;
        if (myStream) {
            myStream.getTracks().forEach(track => track.stop());
        }
        if (socket.current && socket.current.disconnect) {
            socket.current.disconnect();
        }
        if (peerRef.current) {
            peerRef.current.destroy();
        }
      };
  }, [isTeacher, user.id]);

  // --- MEDIA CONTROLS ---
  const toggleMic = () => {
    if (stream) {
      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMicOn(audioTrack.enabled);
      }
    }
  };

  const toggleCam = () => {
    if (stream) {
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsCamOn(videoTrack.enabled);
      }
    }
  };

  const toggleLowBandwidth = () => {
    const newState = !lowBandwidth;
    setLowBandwidth(newState);
    if (stream) {
        const videoTrack = stream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !newState;
            setIsCamOn(!newState);
        }
    }
  };

  const handleDrawEnd = (action, data) => {
    if (action === 'start') {
      const newLine = { tool: data.tool, points: [data.x, data.y] };
      linesRef.current = [...linesRef.current, newLine];
      setLines(linesRef.current);
    } else if (action === 'move') {
      const currentLines = linesRef.current;
      const lastLine = currentLines[currentLines.length - 1];
      if (!lastLine) return; 
      
      const newPoints = lastLine.points.concat([data.x, data.y]);
      const updatedLine = { ...lastLine, points: newPoints };
      const newLines = [...currentLines.slice(0, -1), updatedLine];
      
      linesRef.current = newLines;
      setLines(newLines);
      
      sendDrawData({ line: updatedLine });
    }
  };

  const clearCanvas = () => {
    setLines([]);
    linesRef.current = [];
  };

  return (
    <div className="card" style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
        <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
          <h2>Live Classroom</h2>
          <span style={{ fontSize: '0.8rem', background: isTeacher ? '#16a34a' : '#2563eb', padding: '2px 8px', borderRadius: '4px', color: 'white' }}>
            {isTeacher ? 'TEACHER MODE' : 'STUDENT MODE'}
          </span>
        </div>
        
        <div style={{ display: 'flex', gap: '10px' }}>
           <button className="btn" style={{backgroundColor: lowBandwidth ? '#ea580c' : '#333'}} onClick={toggleLowBandwidth}>
             {lowBandwidth ? '⚡ Low Data Mode Active' : 'Wifi Mode'}
           </button>
           <button className="btn btn-danger" onClick={() => window.location.href = '/'}>Leave Class</button>
        </div>
      </div>

      {/* Error Banner for HTTPS/Permissions */}
      {mediaError && (
        <div style={{
            background: '#7f1d1d', 
            color: '#fca5a5', 
            padding: '10px', 
            marginBottom: '15px', 
            borderRadius: '6px', 
            border: '1px solid #ef4444',
            textAlign: 'center',
            fontSize: '0.9rem'
        }}>
            <strong>📷 Issue: {mediaError}</strong>
            <br/>
            <span>If using IP (192.168...), ensure you use <b>https://</b></span>
        </div>
      )}

      {/* Main Layout */}
      <div style={{ display: 'flex', gap: '20px', flex: 1, overflow: 'hidden' }}>
        
        {/* Whiteboard Area */}
        <div ref={canvasWrapperRef} className="canvas-container" style={{ flex: 3, border: '1px solid #333', background: '#fff', position: 'relative', overflow: 'hidden' }}>
           <Whiteboard width={dimensions.width} height={dimensions.height} tool={tool} isTeacher={isTeacher} onDrawEnd={handleDrawEnd} lines={lines} />
        </div>

        {/* Sidebar (Video + Tools + Streaming) */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto' }}>
            <VideoFeed 
                isLowDataMode={lowBandwidth} 
                userVideoRef={userVideo} 
                isMicOn={isMicOn} 
                isCamOn={isCamOn} 
                onToggleMic={toggleMic} 
                onToggleCam={toggleCam} 
            />
            
            {/* Toggle Content Mode */}
            <div style={{display: 'flex', gap: '5px'}}>
                <button 
                    style={{flex: 1, padding: '5px', background: shareMode === 'relay' ? '#2563eb' : '#333', border: 'none', color: 'white', borderRadius: '4px', cursor: 'pointer'}}
                    onClick={() => setShareMode('relay')}
                >
                    LAN Stream
                </button>
                <button 
                    style={{flex: 1, padding: '5px', background: shareMode === 'p2p' ? '#2563eb' : '#333', border: 'none', color: 'white', borderRadius: '4px', cursor: 'pointer'}}
                    onClick={() => setShareMode('p2p')}
                >
                    P2P Share
                </button>
            </div>

            {/* SWITCH BETWEEN MODES */}
            {shareMode === 'relay' ? (
                <VideoRelay 
                    isTeacher={isTeacher} 
                    socket={socket.current} // <--- PASSING SOCKET TO VIDEO RELAY
                />
            ) : (
                <P2PVideoSharer 
                    isHost={isTeacher || iAmHost} 
                    peerRef={peerRef} 
                    // NOTE: P2P Sharer uses peerRef, not socket, for direct connection
                />
            )}

            {isTeacher ? (
                <ToolsPanel setTool={setTool} clearCanvas={clearCanvas} />
            ) : (
              // Allow students to host P2P in P2P mode
              shareMode === 'p2p' && !iAmHost && (
                 <button 
                    className="btn" 
                    style={{fontSize: '0.8rem', padding: '5px', background: '#444', marginTop: '10px'}}
                    onClick={() => setIAmHost(true)}
                 >
                    Become Stream Host
                 </button>
              )
            )}
        </div>
      </div>
    </div>
  );
}