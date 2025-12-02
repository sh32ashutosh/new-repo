from backend.core.socket_manager import sio

# --- CONNECTION LIFECYCLE ---

@sio.event
async def connect(sid, environ):
    """
    Triggered when a client connects via WebSocket.
    'environ' contains headers if you need to parse JWTs manually here.
    """
    print(f"✅ Socket Connected: {sid}")

@sio.event
async def disconnect(sid):
    """
    Triggered when a client drops connection.
    """
    print(f"❌ Socket Disconnected: {sid}")

# --- WEB RTC SIGNALING (P2P Handshake) ---

@sio.event
async def callUser(sid, data):
    """
    Relays the 'Offer' signal from the Initiator (Teacher) to the Receiver.
    Frontend sends: { signalData: ..., from: user.id }
    """
    # In a real production app, we would use 'to=room_id' to isolate classes.
    # For now, we broadcast to everyone except the sender.
    await sio.emit('callUser', data, skip_sid=sid)

@sio.event
async def answerCall(sid, data):
    """
    Relays the 'Answer' signal from the Receiver back to the Initiator.
    Frontend sends: { signal: ... }
    """
    # Frontend expects 'callAccepted' event with the signal payload
    await sio.emit('callAccepted', data['signal'], skip_sid=sid)

# --- WHITEBOARD SYNC ---

@sio.event
async def draw_data(sid, data):
    """
    Relays vector drawing coordinates.
    Frontend sends: { line: { tool, points: [...] } }
    """
    await sio.emit('draw_data', data, skip_sid=sid)