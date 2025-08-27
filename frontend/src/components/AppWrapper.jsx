import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '../contexts/AuthContext'
import ProtectedRoute from './ProtectedRoute'
import LoginPage from '../pages/LoginPage'
import SignupPage from '../pages/SignupPage'
import App from './App'

function AppWrapper() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Rotas públicas */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          
          {/* Rota protegida - Dashboard */}
          <Route 
            path="/dashboard/*" 
            element={
              <ProtectedRoute>
                <App />
              </ProtectedRoute>
            } 
          />
          
          {/* Redirecionamento da raiz para o dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Fallback para rotas não encontradas */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default AppWrapper
