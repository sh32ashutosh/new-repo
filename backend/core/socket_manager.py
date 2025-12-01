import socketio

# Initialize the Async Socket.IO Server
# We use cors_allowed_origins='*' to accept connections from your React PWA
# The frontend uses 'transports': ['websocket'], which this server accepts by default.
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*', 
    logger=True,  # Keep logs on to see "Handshake" events in terminal
    engineio_logger=True,
    # This ensures we don't block the frontend's immediate websocket upgrade attempt
    allow_upgrades=True 
)