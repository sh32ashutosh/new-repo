Vlink - Low Bandwidth Virtual Classroom (SIH 25101)

Vlink is a live, real-time educational platform engineered for optimal performance on low-bandwidth and unstable networks. It achieves maximum data efficiency by replacing traditional video streaming with a vector synchronization model and utilizing Peer-to-Peer (P2P) technology for high-volume content transfer.

🚀 Implemented Features

I. Frontend Features (React.js)

Feature

Description

Bandwidth Optimization

Vector Whiteboard

Real-time drawing using React-Konva. The teacher can draw, erase, and change colors.

Saves ~98% data by sending minimal coordinate packets instead of video frames of the whiteboard.

WebRTC P2P Video/Audio

Direct Peer-to-Peer video and audio streaming between Teacher and Student.

Zero server bandwidth cost for video transmission.

Low Data Mode

A toggle button that disables the video track of the WebRTC stream instantly.

Saves ~95% bandwidth by prioritizing audio and whiteboard vectors during poor connectivity.

LAN Video Relay (Teacher)

Allows the Teacher to paste an internet video link (MP4) and stream it only through their local Wi-Fi.

Saves N-1 data connections. Only the teacher uses internet data; students consume local Wi-Fi data.

P2P File Sharer

Allows any student to select a video file and send it directly to all other connected peers using WebRTC Data Channels.

Serverless file transfer used for sharing resources entirely over the local network (LAN).

Role-Based UI

Dedicated interfaces for Teacher (Tools Panel, Create Class) and Student (View Only, Join Class, P2P Host option).

N/A

II. Backend Features (Python Flask, Socket.io, SQLite)

Component

Technology

Purpose

Persistence Layer

Flask-SQLAlchemy (SQLite)

Uses a persistent vlink.db file to store all user accounts, classes, assignments, and uploaded files, ensuring data survives server restarts.

Real-Time Signaling

Flask-SocketIO

Handles the initial WebRTC handshake (callUser, answerCall) and relays tiny Vector Drawing packets (draw_data) between peers.

LAN Proxy Endpoint

/api/stream-proxy

Fetches content from a public URL and re-serves it over the local network, enabling the LAN Video Relay feature.

Authentication/Data

/api/login, /api/dashboard

REST endpoints for user authentication and fetching class data from the persistent database.

🚧 Roadmap: Features Not Yet Achieved

The following features were specified in the original request but require further development and integration time:

Feature Category

Detail

Status/Reason

Whiteboard Control

Pen Color Change & Eraser Logic: While the UI is present, the actual functionality to change pen color or dynamically resize the eraser is mocked and not yet fully implemented in the Konva drawing logic.

Partially Implemented.

Slide Synchronization

Ability for the Teacher to upload an image/PDF that serves as the background layer for the whiteboard canvas.

Not Implemented. Requires file conversion/processing on the client-side to render the static background image underneath the Konva drawing layer.

Tus.io Resumable Uploads

Full implementation of the Tus.io protocol for resilient, resumable file uploads.

Mocked. The file upload UI is present, but the actual client-side Tus library logic is simulated using timers (uploadFileMock) instead of a full client-server implementation.

Discussions & Assignments

Functionality to submit a new discussion post or a quiz answer and have it saved to the database.

Basic Data Layer Only. The backend endpoints (/api/discussions) exist to receive data, but the full React form handling (submitting the post and updating the database) is still simulated in the frontend.

🔑 Critical Configuration for Live Use

The entire system must run on HTTPS to enable the Camera/Mic (WebRTC) and connect mobile devices.

1. Network Setup

Update Config: Ensure src/services/config.js is set to:

export const USE_MOCK = false; 
const SERVER_IP = "192.168.x.x"; // Your Laptop's IPv4
export const API_BASE_URL = `https://${SERVER_IP}:5000/api`; 
export const SOCKET_URL = `https://${SERVER_IP}:5000`;



Start Backend: Run python app.py. (It runs on HTTPS via port 5000).

Start Frontend: Run npm run dev -- --host. (It runs on HTTPS via port 5173).

2. Mandatory Mobile Setup (Fixes Login and Camera)

You MUST manually accept the self-signed certificates on your phone.

Accept Backend: On your phone, go to https://192.168.x.x:5000/api/dashboard. Click Advanced -> Proceed (unsafe). (This unblocks the Login/API calls).

Accept Frontend: On your phone, go to https://192.168.x.x:5173. Click Advanced -> Proceed (unsafe). (This unblocks the React application and the Camera API).

⚠️ Troubleshooting Guide (Addressing Errors)

Error Encountered

Cause

Solution

ERR_SSL_PROTOCOL_ERROR

Frontend (HTTPS) was trying to communicate with an unsecured Backend (HTTP).

Fixed by: Adding ssl_context='adhoc' to socketio.run() in backend/app.py, forcing the backend to serve securely.

Cannot read properties of undefined (reading 'getUserMedia')

The browser blocks Camera/Mic access on network IPs (192.168.x.x) unless it is secure.

Fixed by: Using https:// URLs for both frontend (via basicSsl plugin) and backend, and forcing the user to manually accept the certificate (Step 2 above).

TypeError: server() got an unexpected keyword argument 'ssl_context'

Flask-SocketIO's default Eventlet mode doesn't support adhoc SSL.

Fixed by: Changing async_mode in flask_socketio to 'threading'.

No matching export in config.js

Missing export keyword in src/services/config.js.

Fixed by: Ensuring all variables (USE_MOCK, API_BASE_URL, SOCKET_URL) were explicitly exported.

Login Credentials: student/123 or teacher/123
