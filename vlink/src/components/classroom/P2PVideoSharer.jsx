import React, { useState, useEffect, useRef } from 'react';

export default function P2PVideoSharer({ isHost, peerRef, socket }) {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [receivedVideoUrl, setReceivedVideoUrl] = useState(null);
  const [status, setStatus] = useState('');
  
  // Buffer for receiving data
  const receiveBuffer = useRef([]);
  const receivedSize = useRef(0);
  const fileMeta = useRef(null);

  useEffect(() => {
    if (!peerRef.current) return;

    const peer = peerRef.current;

    // --- RECEIVER LOGIC (For those watching) ---
    peer.on('data', (data) => {
      try {
        // Check if data is metadata (JSON string)
        const text = new TextDecoder().decode(data);
        const meta = JSON.parse(text);
        
        if (meta.type === 'video-meta') {
          fileMeta.current = meta;
          receiveBuffer.current = [];
          receivedSize.current = 0;
          setStatus(`Receiving video: ${meta.name} (${(meta.size / 1024 / 1024).toFixed(2)} MB)`);
        }
      } catch (e) {
        // If error, it's likely BINARY data (video chunk)
        if (fileMeta.current) {
          receiveBuffer.current.push(data);
          receivedSize.current += data.byteLength;
          
          const percent = Math.round((receivedSize.current / fileMeta.current.size) * 100);
          setProgress(percent);

          // Video fully received?
          if (receivedSize.current === fileMeta.current.size) {
            setStatus('Video Received! Processing...');
            const blob = new Blob(receiveBuffer.current, { type: fileMeta.current.mime });
            setReceivedVideoUrl(URL.createObjectURL(blob));
            fileMeta.current = null; // Reset
          }
        }
      }
    });
  }, [peerRef]);

  // --- SENDER LOGIC (For the Host) ---
  const streamFile = async () => {
    if (!file || !peerRef.current) return;
    
    setStatus('Starting Stream...');
    const peer = peerRef.current;
    const CHUNK_SIZE = 16 * 1024; // 16KB chunks (Safe for WebRTC)

    // 1. Send Metadata First
    const meta = JSON.stringify({
      type: 'video-meta',
      name: file.name,
      size: file.size,
      mime: file.type
    });
    peer.send(meta);

    // 2. Read and Send Chunks
    const reader = new FileReader();
    let offset = 0;

    reader.onload = (e) => {
      peer.send(e.target.result); // Send binary chunk
      offset += e.target.result.byteLength;
      
      const percent = Math.round((offset / file.size) * 100);
      setProgress(percent);

      if (offset < file.size) {
        readNextChunk();
      } else {
        setStatus('Streaming Complete');
      }
    };

    const readNextChunk = () => {
      const slice = file.slice(offset, offset + CHUNK_SIZE);
      reader.readAsArrayBuffer(slice);
    };

    readNextChunk();
  };

  return (
    <div className="card" style={{ marginTop: '15px', padding: '15px', border: '1px solid #333' }}>
      <h3 style={{fontSize: '1rem', marginBottom: '10px'}}>⚡ P2P Video Share (No Internet)</h3>
      
      {/* HOST INTERFACE */}
      {isHost ? (
        <div style={{display: 'flex', gap: '10px', flexDirection: 'column'}}>
          <input 
            type="file" 
            accept="video/*" 
            onChange={(e) => setFile(e.target.files[0])} 
            className="input-field" 
          />
          <button 
            className="btn btn-success" 
            onClick={streamFile}
            disabled={!file}
          >
            Stream to Class
          </button>
          {progress > 0 && <p>Sending: {progress}%</p>}
        </div>
      ) : (
        /* RECEIVER INTERFACE */
        <div>
          {status && <p style={{color: '#ca8a04'}}>{status}</p>}
          {progress > 0 && progress < 100 && (
             <div style={{width:'100%', background:'#333', height:'5px', marginTop:'5px'}}>
               <div style={{width: `${progress}%`, background:'#16a34a', height:'100%'}}></div>
             </div>
          )}
          {receivedVideoUrl && (
            <video 
              src={receivedVideoUrl} 
              controls 
              autoPlay 
              style={{ width: '100%', marginTop: '10px', borderRadius: '8px' }} 
            />
          )}
          {!receivedVideoUrl && !status && <p style={{color:'#666'}}>Waiting for host to stream...</p>}
        </div>
      )}
    </div>
  );
}