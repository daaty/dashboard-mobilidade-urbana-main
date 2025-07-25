import React from 'react';

const TestFloatingButton = () => {
  return (
    <div 
      style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        width: '60px',
        height: '60px',
        backgroundColor: '#2563eb',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '24px',
        cursor: 'pointer',
        zIndex: 9999,
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
      }}
      onClick={() => alert('Chat funcionando!')}
    >
      💬
    </div>
  );
};

export default TestFloatingButton;
