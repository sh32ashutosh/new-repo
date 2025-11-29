import { createContext, useState, useContext } from 'react';
import { loginUser } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('vidmesh_user')) || null);

  const login = async (username, password) => {
    try {
      const data = await loginUser(username, password);
      setUser(data.user);
      localStorage.setItem('vidmesh_user', JSON.stringify(data.user));
      return { success: true };
    } catch (err) {
      return err;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('vidmesh_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);