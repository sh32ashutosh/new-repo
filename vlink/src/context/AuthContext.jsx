import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Restore session if browser refreshes
    const savedUser = localStorage.getItem('user');
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  // ⚡ UPDATED: Call the Real Backend
  const login = async (username, password) => {
    try {
      // 1. Prepare form data (FastAPI expects x-www-form-urlencoded usually, 
      // but if you configured JSON, use JSON. This example uses Form Data for OAuth2 standard)
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/api/login/access-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // 2. We got a REAL token!
        const userData = data.user; 
        
        // Save the token so other requests (Dashboard) can use it
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        setUser(userData);
        return { success: true };
      } else {
        return { success: false, message: data.detail || 'Login failed' };
      }
    } catch (error) {
      console.error("Login Error:", error);
      return { success: false, message: 'Server error' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};