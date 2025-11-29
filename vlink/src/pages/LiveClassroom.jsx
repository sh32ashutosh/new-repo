import React, { useRef, useState, useEffect } from 'react';
import Peer from 'simple-peer';
import { useAuth } from '../context/AuthContext';
import { sendDrawData } from '../services/api';
import { connectSocket } from '../services/socketAdapter';

// Components
import Whiteboard from '../components/classroom/Whiteboard';
import ToolsPanel from '../components/classroom/ToolsPanel';
import VideoFeed from '../components/classroom/VideoFeed';

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

  // Layout State
  const canvasWrapperRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Refs
  const userVideo = useRef();
  const socket = useRef();
  const peerRef = useRef(); // Keep track of peer to replace tracks

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

  // --- MEDIA & CONNECTION SETUP ---
  useEffect(() => {
    let myStream = null; 
    let isMounted = true; 

    // 1. Initial Media Get
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then((currentStream) => {
        if (!isMounted) {
            currentStream.getTracks().forEach(track => track.stop());
            return;
        }

        myStream = currentStream;
        setStream(currentStream);
        
        if (userVideo.current) {
          userVideo.current.srcObject = currentStream;
        }
        
        // 2. Socket & Peer Setup
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
        if (isMounted) console.error("Media Error:", err);
      });
      
      return () => {
        isMounted = false;
        // Aggressive Cleanup: Stop all tracks
        if (myStream) {
            myStream.getTracks().forEach(track => {
                track.stop();
                track.enabled = false;
            });
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
        audioTrack.enabled = !audioTrack.enabled; // Mute only (keep hardware on for mic is standard)
        setIsMicOn(audioTrack.enabled);
      }
    }
  };

  const toggleCam = () => {
    if (stream) {
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        // Standard Mute: This turns off the stream data, but usually leaves hardware light on.
        // To fix "Background" issue, we ensure 'enabled' is strictly managed.
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
            // For Bandwidth mode, we disable the track.
            videoTrack.enabled = !newState;
            setIsCamOn(!newState);
            
            // NOTE: If you want to strictly turn off the hardware light, 
            // you would use videoTrack.stop() here. 
            // However, re-enabling it requires getUserMedia() again which is complex for this prototype.
            // videoTrack.enabled = false is sufficient for bandwidth savings (0 bits sent).
        }
    }
  };

  // --- WHITEBOARD LOGIC ---
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

      <div style={{ display: 'flex', gap: '20px', flex: 1 }}>
        <div ref={canvasWrapperRef} className="canvas-container" style={{ flex: 3, border: '1px solid #333', borderRadius: '8px', background: '#fff', position: 'relative', overflow: 'hidden' }}>
           <Whiteboard 
             width={dimensions.width} 
             height={dimensions.height}
             tool={tool}
             isTeacher={isTeacher}
             onDrawEnd={handleDrawEnd}
             lines={lines} 
           />
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <VideoFeed 
                isLowDataMode={lowBandwidth} 
                userVideoRef={userVideo} 
                isMicOn={isMicOn}
                isCamOn={isCamOn}
                onToggleMic={toggleMic}
                onToggleCam={toggleCam}
            />
            
            {isTeacher ? (
                <ToolsPanel setTool={setTool} clearCanvas={clearCanvas} />
            ) : (
              <div className="card" style={{padding: '15px', textAlign: 'center'}}>
                <h4>Student View</h4>
                <p style={{color: '#888'}}>You are viewing the teacher's whiteboard.</p>
              </div>
            )}
        </div>
      </div>
    </div>
  );
}