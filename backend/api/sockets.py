from backend.core.socket_manager import sio

# --- CONNECTION LIFECYCLE ---

@sio.event
async def connect(sid, environ):
    print(f"✅ Socket Connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"❌ Socket Disconnected: {sid}")

# --- WEB RTC SIGNALING (Legacy/Fallback) ---

@sio.event
async def callUser(sid, data):
    """
    Enhanced Signaling: Now supports 'signal_type' to prevent conflicts
    between Camera streams and P2P File Sharing.
    """
    room = data.get('class_id')
    # Default to 'camera' if not specified to support legacy code
    signal_type = data.get('signal_type', 'camera') 
    
    if room:
        await sio.emit('callUser', data, room=room, skip_sid=sid)

@sio.event
async def answerCall(sid, data):
    room = data.get('class_id')
    signal_type = data.get('signal_type', 'camera')
    
    if room:
        await sio.emit('callAccepted', data['signal'], room=room, skip_sid=sid)
# --- THE HYBRID RELAY (Audio + Stylus) ---

@sio.event
async def stream_packet(sid, data):
    """
    Handles the 'Zero Tolerance' Hybrid Payload.
    
    The 'vectors' field now strictly follows the format: ((x,y), color, set/reset)
    
    Expected 'data' structure:
    {
       "seq": 105,              # Sequence Number (For Jitter Buffer)
       "ts": 16999999,          # Timestamp
       "audio": <BinaryBlob>,   # 40ms Opus Chunk
       "vectors": [             
          # Format: [[x, y], color_hex, mode]
          # mode: "set" (draw/add pixel) | "reset" (erase/remove pixel)
          [[100, 200], "#FF0000", "set"],
          [[101, 202], "#FF0000", "set"]
       ],
       "fec": <BinaryBlob>      # XOR Parity data
    }
    """
    # 1. Broadcast immediately to the room (LAN Anchor behavior)
    # The server acts as a dumb pipe here to ensure < 10ms processing time.
    await sio.emit('stream_packet', data, skip_sid=sid)

# --- LEGACY WHITEBOARD (Fallback) ---
@sio.event
async def draw_data(sid, data):
    await sio.emit('draw_data', data, skip_sid=sid)