import { Buffer } from 'buffer';
window.Buffer = Buffer; // Make Buffer available globally
import process from 'process';
window.process = process;
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './styles/Variables.css'; // Import variables first
import './App.css';              // Then global styles

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);