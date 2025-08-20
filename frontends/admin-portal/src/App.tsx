import React, { useState, createContext, useContext } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { Routes, Route, Link, Navigate } from 'react-router-dom';
import api, { setAuthToken } from './api';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import Settings from './pages/Settings';

interface AuthContextValue {
  token: string | null;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextValue>({ token: null, signOut: () => {} });

export const useAuth = () => useContext(AuthContext);

const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);

  const login = useGoogleLogin({
    onSuccess: (resp) => {
      setToken(resp.access_token);
      setAuthToken(resp.access_token);
    },
  });

  const signOut = () => {
    setToken(null);
    setAuthToken(null);
  };

  if (!token) {
    return (
      <div style={{ padding: '16px' }}>
        <button onClick={() => login()}>Sign in with Google</button>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ token, signOut }}>
      <nav
        style={{
          padding: '8px',
          borderBottom: '1px solid #ccc',
          display: 'flex',
          gap: '16px',
          alignItems: 'center'
        }}
      >
        <Link to="/">Dashboard</Link>
        <Link to="/clients">Clients</Link>
        <Link to="/settings">Settings</Link>
        <button onClick={signOut} style={{ marginLeft: 'auto' }}>
          Sign out
        </button>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/clients" element={<Clients />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </AuthContext.Provider>
  );
};

export default App;
