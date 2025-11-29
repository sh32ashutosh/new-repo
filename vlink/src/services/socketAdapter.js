import { USE_MOCK, SOCKET_URL } from './config';
import { io } from 'socket.io-client';

let socket;

export const connectSocket = () => {
  if (USE_MOCK) {
    console.log("Mock Socket Connected");
    return {
      on: (event, callback) => {
        console.log(`Listening for mock event: ${event}`);
        // If we are listening for drawing, generate fake data for testing
        if (event === 'draw_data') {
          setInterval(() => {
            // Simulate a teacher drawing a random line
            const x = Math.random() * 500;
            const y = Math.random() * 500;
            callback({ tool: 'pen', points: [x, y, x+10, y+10] });
          }, 2000);
        }
      },
      emit: (event, data) => console.log(`Mock Emit [${event}]:`, data),
      disconnect: () => console.log("Mock Socket Disconnected")
    };
  } else {
    // Real Socket connection
    socket = io(SOCKET_URL);
    return socket;
  }
};