import { USE_MOCK, SOCKET_URL } from './config';
import { io } from 'socket.io-client';

let socketInstance = null;

export const connectSocket = () => {
  if (USE_MOCK) {
    console.log("Mock Socket Connected");
    return { 
        on: (event, callback) => {
            if (event === 'connect') setTimeout(callback, 10); // Mock connect event
        }, 
        emit: () => {}, 
        disconnect: () => {} 
    };
  } else {
    // Real Socket connection to your Local IP
    if (!socketInstance) {
        // CRITICAL: Configuration to handle self-signed HTTPS certificate locally
        socketInstance = io(SOCKET_URL, {
            transports: ['websocket'], // Use pure websocket
            secure: true,
            rejectUnauthorized: false, // Allows self-signed certificates in dev
            reconnectionAttempts: 5,
        });
    }
    return socketInstance;
  }
};