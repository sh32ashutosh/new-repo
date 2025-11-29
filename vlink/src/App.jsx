import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import 'react-toastify/dist/ReactToastify.css'; // Keep this if using Toastify, or remove if using custom ToastContext
import './App.css';

// --- IMPORTS ---
// Updated path: pointing to the 'layout' subfolder
import Layout from './components/layout/Layout';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LiveClassroom from './pages/LiveClassroom';
import Files from './pages/Files';
import Assignments from './pages/Assignments';
import Discussions from './pages/Discussions';
import Profile from './pages/Profile';
import Classes from './pages/Classes'; // <--- Import the new page here

// --- PROTECTED ROUTE WRAPPER ---
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Layout>{children}</Layout>;
};

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider> {/* Wraps app with your custom Toast logic */}
        <BrowserRouter>
          <Routes>
            {/* Public Route */}
            <Route path="/login" element={<Login />} />

            {/* Protected Routes */}
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/classes" 
              element={
                <ProtectedRoute>
                  <Classes /> {/* <--- Use the component here instead of the div placeholder */}
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/classroom/:id" 
              element={
                <ProtectedRoute>
                  <LiveClassroom /> {/* This component contains the Whiteboard */}
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/assignments" 
              element={
                <ProtectedRoute>
                  <Assignments />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/discussions" 
              element={
                <ProtectedRoute>
                  <Discussions />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/files" 
              element={
                <ProtectedRoute>
                  <Files />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } 
            />

            {/* Fallback Route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}