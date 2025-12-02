import socketio

# Define the allowed origins explicitly for the WebSocket connection
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    # ⚡ CRITICAL FIX: Explicitly allow the Vite URL
    cors_allowed_origins=origins,
    logger=True,
    engineio_logger=True
)