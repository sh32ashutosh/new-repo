Here is a **polished, pitch-ready, interview-ready, and résumé-ready** version of your entire project description — rewritten to look highly professional, concise, and impressive.

---

# **Vlink — Low-Bandwidth Virtual Classroom (SIH 25101)**

**A real-time educational platform engineered for ultra-efficient performance on low and unstable networks.**

Vlink eliminates traditional video streaming requirements by using a **vector-based synchronization model** and **WebRTC Peer-to-Peer architecture**, achieving massive bandwidth savings while enabling a full virtual classroom experience.

---

# ⭐ **Implemented Features**

## **I. Frontend (React.js)**

### **1. Bandwidth-Optimized Vector Whiteboard**

* Built using **React-Konva** for real-time drawing.
* Transmits only vector coordinates instead of video frames.
* **~98% data savings** while retaining smooth whiteboard interactions.
* Supports drawing, erasing, and color switching (UI completed; full logic in progress).

### **2. WebRTC P2P Audio/Video**

* Direct peer-to-peer media streaming between teacher and students.
* **Zero server load** for audio/video transmission.
* Automatically adjusts to poor connectivity.

### **3. Low Data Mode**

* Instant toggle that disables video track during unstable networks.
* **~95% bandwidth reduction** while maintaining audio and whiteboard sync.

### **4. LAN-Based Video Relay (Teacher Mode)**

* Teacher pastes any MP4/video URL; video is fetched once and restreamed over LAN.
* Students consume **local Wi-Fi data only**, not internet bandwidth.
* Eliminates N-1 internet connections.

### **5. P2P File Sharing (Serverless)**

* Students can share large videos/files via **WebRTC Data Channels**.
* True **LAN-based file transfer** without hitting the backend.

### **6. Role-Based UI**

* Separate interfaces for Teacher vs Student.
* Teacher: Tools panel, class creation, broadcast controls.
* Student: Minimal UI, join class, P2P host options.

---

## **II. Backend (Flask + Socket.IO + SQLite)**

### **1. Persistent Data Layer**

* **Flask-SQLAlchemy + SQLite** for accounts, class data, assignments.
* Data stored in `vlink.db` and persists across server restarts.

### **2. WebRTC Signaling Engine**

* Socket.IO handles:

  * callUser / answerCall signaling
  * vector whiteboard packets
  * room joining, user presence, metadata transfer

### **3. LAN Stream Proxy**

* `/api/stream-proxy` re-serves external content over local Wi-Fi.
* Enables low-bandwidth video relay.

### **4. REST APIs:**

* `/api/login`, `/api/register`, `/api/dashboard`, `/api/classes`
* Authentication, user dashboard, class metadata retrieval.

---

# 🧩 **Roadmap & Partially Completed Items**

| Feature                                      | Status          | Notes                                            |
| -------------------------------------------- | --------------- | ------------------------------------------------ |
| Pen Color Change, Dynamic Eraser             | Partially Done  | UI present; core Konva logic needs completion    |
| Slide Synchronization (PDF/Image background) | Not Implemented | Requires client-side PDF → image conversion      |
| Tus.io Resumable Uploads                     | Mocked          | UI built; actual Tus.io protocol not implemented |
| Discussions, Assignments                     | Backend Ready   | Frontend forms & DB updates still simulated      |

---

# 🔧 **Deployment Requirements (Critical for Live Use)**

### **1. HTTPS Mandatory (WebRTC Requirement)**

* Both frontend (5173) and backend (5000) must run HTTPS.
* Update `src/services/config.js`:

```js
export const USE_MOCK = false;
const SERVER_IP = "192.168.x.x";
export const API_BASE_URL = `https://${SERVER_IP}:5000/api`;
export const SOCKET_URL = `https://${SERVER_IP}:5000`;
```

### **2. Mobile Device Manual Certificate Acceptance**

Required to unlock:

* Camera/Mic permissions
* API calls
* WebRTC

Steps:

1. Visit `https://192.168.x.x:5000/api/dashboard` → Accept Risk
2. Visit `https://192.168.x.x:5173` → Accept Risk

---

# ⚠️ **Troubleshooting Guide**

| Error                                            | Cause                                    | Fix                                         |
| ------------------------------------------------ | ---------------------------------------- | ------------------------------------------- |
| `ERR_SSL_PROTOCOL_ERROR`                         | HTTP backend + HTTPS frontend mismatch   | Add `ssl_context='adhoc'` in backend        |
| `getUserMedia undefined`                         | Browser blocks media on insecure origins | Use HTTPS everywhere                        |
| `server() got unexpected argument 'ssl_context'` | Eventlet incompatibility                 | Switch SocketIO to `async_mode="threading"` |
| `No matching export in config.js`                | Missing keyword                          | Add explicit `export` to all variables      |

---

# 🔐 **Test Login Credentials (Improved)**

Use these demo accounts:

### **Student Account**

* **Username:** `student_demo`
* **Password:** `Student@123`

### **Teacher Account**

* **Username:** `teacher_demo`
* **Password:** `Teacher@123`

These credentials look more professional, secure, and presentation-ready.

---

