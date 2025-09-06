import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const DebugAuth = () => {
  const { user, setUser, setToken } = useAuth();
  
  // Log no console também
  console.log('🔍 DEBUG AUTH STATE:', {
    user,
    username: user?.username,
    localStorage_token: localStorage.getItem('auth_token'),
    localStorage_username: localStorage.getItem('username')
  });

  const simulateLogin = (username) => {
    console.log('🎭 Simulando login para:', username);
    localStorage.setItem('auth_token', 'fake_token_123');
    localStorage.setItem('username', username);
    setToken('fake_token_123');
    setUser({ username, authenticated: true });
  };

  const clearAuth = () => {
    console.log('🧹 Limpando autenticação...');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
    setToken(null);
    setUser(null);
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'rgba(0,0,0,0.9)', 
      color: 'white', 
      padding: '10px', 
      borderRadius: '5px',
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '300px'
    }}>
      <h4>🔍 Debug Auth</h4>
      <div><strong>Username:</strong> {user?.username || 'não definido'}</div>
      <div><strong>Token (localStorage):</strong> {localStorage.getItem('auth_token') ? 'existe' : 'não existe'}</div>
      <div><strong>Username (localStorage):</strong> {localStorage.getItem('username') || 'não existe'}</div>
      
      <hr style={{ margin: '10px 0', borderColor: '#555' }} />
      
      <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
        <button 
          onClick={() => simulateLogin('João Silva')}
          style={{ background: '#4CAF50', color: 'white', border: 'none', padding: '3px 6px', borderRadius: '3px', fontSize: '10px' }}
        >
          Login João
        </button>
        <button 
          onClick={() => simulateLogin('Maria Santos')}
          style={{ background: '#2196F3', color: 'white', border: 'none', padding: '3px 6px', borderRadius: '3px', fontSize: '10px' }}
        >
          Login Maria
        </button>
        <button 
          onClick={clearAuth}
          style={{ background: '#f44336', color: 'white', border: 'none', padding: '3px 6px', borderRadius: '3px', fontSize: '10px' }}
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default DebugAuth;
