import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await login(username, password);
    if (res.success) {
      navigate('/');
    } else {
      alert("Invalid Credentials (Try 'student' / '123')");
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#000' }}>
      <div className="card" style={{ width: '350px' }}>
        <h2 style={{ textAlign: 'center' }}>Vlink Login</h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '20px' }}>
          <input className="input-field" placeholder="Username (student)" value={username} onChange={e => setUsername(e.target.value)} />
          <input className="input-field" type="password" placeholder="Password (123)" value={password} onChange={e => setPassword(e.target.value)} />
          <button className="btn btn-primary" type="submit">Login</button>
        </form>
      </div>
    </div>
  );
}