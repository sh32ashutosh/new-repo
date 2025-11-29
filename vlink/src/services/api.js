import { USE_MOCK, API_BASE_URL } from './config';
import db from '../mock/db.json';

// --- AUTH ---
export const loginUser = async (username, password) => {
  if (USE_MOCK) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const user = db.users.find(u => u.username === username && u.password === password);
        if (user) resolve({ success: true, token: "mock-jwt", user });
        else reject({ success: false, message: "Invalid credentials" });
      }, 500);
    });
  } else {
    // Real Backend Call
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return res.json();
  }
};

// --- DATA FETCHING ---
export const getDashboardData = async () => {
  if (USE_MOCK) return Promise.resolve(db);
  const res = await fetch(`${API_BASE_URL}/dashboard`);
  return res.json();
};

// --- FILE UPLOAD (Tus.io Simulation) ---
export const uploadFileMock = (file, onProgress) => {
  return new Promise((resolve) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 20;
      onProgress(progress); // Update UI Progress Bar
      if (progress >= 100) {
        clearInterval(interval);
        resolve({ success: true, url: URL.createObjectURL(file) });
      }
    }, 500);
  });
};

// --- VECTOR DATA (Live Class) ---
// In a real app, this would use Socket.io. 
// For mock, we just log it or store in a temp variable.
export const sendDrawData = (data) => {
  if (!USE_MOCK) {
    // socket.emit('draw_data', data);
  } else {
    // console.log("Mock Sending Vector:", data);
  }
};