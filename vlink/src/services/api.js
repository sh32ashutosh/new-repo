import { API_BASE_URL } from './config';
import { getSocket } from './socketAdapter'; 

// Helper to retrieve the JWT token
const getToken = () => localStorage.getItem('token');

// Generic Fetch Wrapper
// Handles Headers, Auth Injection, and Error Parsing
const apiCall = async (endpoint, options = {}) => {
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Auto-Inject Token
  if (token) {
    headers['Authorization'] = token; 
  }

  // Handle File Uploads (Browser must set boundary for FormData)
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // GLOBAL ERROR INTERCEPTOR (Zero Tolerance Auth)
    if (response.status === 401) {
      console.warn("Session expired or invalid token. Logging out...");
      localStorage.removeItem('token');
      localStorage.removeItem('user_data');
      window.location.href = '/login'; // Force redirect to login
      throw new Error("Unauthorized");
    }

    const data = await response.json();

    if (!response.ok) {
      // Extract specific error message from FastAPI response
      throw new Error(data.detail || data.message || 'API Request Failed');
    }

    return data;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
};

// --- AUTH ---
export const loginUser = async (username, password) => {
  // Uses the simplified /login route (ensure backend router is updated)
  const data = await apiCall('/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  
  // Safety Check: Ensure token actually exists
  if (data.token) {
      localStorage.setItem('token', data.token);
      return data;
  } else {
      throw new Error("Login succeeded but no token received");
  }
};

// --- DASHBOARD ---
export const getDashboardData = () => apiCall('/dashboard');

// --- CLASSROOMS ---
export const createClass = (title) => apiCall('/classes/create', {
  method: 'POST',
  body: JSON.stringify({ title }),
});

export const joinClass = (code) => apiCall('/classes/join', {
  method: 'POST',
  body: JSON.stringify({ code }),
});

export const getClassDetails = (classId) => apiCall(`/classes/${classId}`);

// --- LIVE CLASS CONTROL ---
export const startLiveClass = (classId) => apiCall(`/live/${classId}/start`, { method: 'POST' });
export const endLiveClass = (classId) => apiCall(`/live/${classId}/end`, { method: 'POST' });

// --- ASSIGNMENTS ---
export const createAssignment = (data) => apiCall('/assignments/create', {
  method: 'POST',
  body: JSON.stringify(data),
});

export const submitQuiz = (assignmentId, answers) => apiCall(`/assignments/${assignmentId}/submit`, {
  method: 'POST',
  body: JSON.stringify({ answers }),
});

// --- FILES ---
export const uploadFile = (file, classroomId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('classroom_id', classroomId);

  return apiCall('/files/upload', {
    method: 'POST',
    body: formData,
  });
};

// --- DISCUSSIONS ---
export const getDiscussions = (classId) => apiCall(`/discussions/class/${classId}`);

export const createDiscussion = (classId, title, content) => apiCall('/discussions/create', {
  method: 'POST',
  body: JSON.stringify({ classroom_id: classId, title, content }),
});

export const replyToDiscussion = (discussionId, content) => apiCall(`/discussions/${discussionId}/reply`, {
  method: 'POST',
  body: JSON.stringify({ content }),
});

// --- PROFILE ---
export const getProfile = () => apiCall('/profile');
export const updatePreferences = (prefs) => apiCall('/profile/preferences', {
  method: 'POST',
  body: JSON.stringify(prefs)
});

// --- WHITEBOARD (Socket Proxy) ---
// This ensures LiveClassroom.jsx doesn't break when calling this function
export const sendDrawData = (data) => {
  const socket = getSocket();
  if (socket && socket.connected) {
    socket.emit('draw_data', data);
  } else {
    // console.warn("Socket not connected, draw data dropped");
  }
};