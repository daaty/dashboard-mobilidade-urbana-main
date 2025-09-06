import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, X, Minimize2, Maximize2, Brain } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

// URL da API do agente - usando o endpoint do playground
const AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL || 
  (import.meta.env.PROD 
    ? 'https://dashboard-mobility-agent.herokuapp.com' 
    : 'http://localhost:8001');

// ID do agente para o playground (pode ser qualquer UUID)
const AGENT_ID = 'mobility-agent-frontend-chat';

const FloatingChat = () => {
  const { user } = useAuth(); // Capturar dados do usuário autenticado
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  
  // Mensagem personalizada com nome do usuário
  const getWelcomeMessage = () => {
    const userName = user?.username || 'Usuário';
    return `Olá${user?.username ? ` ${userName}` : ''}! Sou seu assistente inteligente de mobilidade urbana. Como posso ajudá-lo hoje?`;
  };
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesRef = useRef(null);

  // Inicializar mensagem de boas-vindas após o usuário ser carregado
  useEffect(() => {
    const welcomeMessage = {
      type: 'agent',
      message: getWelcomeMessage(),
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, [user?.username]); // Reagir especificamente ao username
  
  // Função para enviar mensagem
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: 'user',
      message: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      // Capturar dados do usuário para enviar ao agente
      const userName = user?.username && user.username !== 'Usuário' ? user.username : null;
      const userId = user?.id || user?.username || 'frontend_user';
      
      // Debug: verificar o que está sendo enviado
      console.log('🔍 FloatingChat enviando:', {
        user_object: user,
        userName: userName,
        userId: userId,
        user_username: user?.username
      });
      
      const payload = {
        message: currentInput,
        user_id: userId,
        session_id: `chat_${userId}_${Date.now()}`
      };
      
      // Só adicionar user_name se realmente tiver um nome válido
      if (userName) {
        payload.user_name = userName;
      }
      
      // Usando o endpoint do playground que acabamos de corrigir
      const response = await fetch(`${AGENT_API_URL}/v1/playground/agents/${AGENT_ID}/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok && data.status === 'completed') {
        const agentMessage = {
          type: 'agent',
          message: data.content || data.result || data.message,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, agentMessage]);
      } else {
        const errorMessage = {
          type: 'error',
          message: 'Erro ao processar sua pergunta. Tente novamente.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (err) {
      const errorMessage = {
        type: 'error',
        message: 'Erro de conexão. Verifique sua conexão e tente novamente.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Scroll automático
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  // Se não está aberto, mostra apenas o botão flutuante
  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-5 rounded-full shadow-2xl hover:from-purple-700 hover:to-blue-700 transition-all duration-300 transform hover:scale-110 focus:outline-none focus:ring-4 focus:ring-purple-300"
          title="Chat Inteligente"
        >
          <MessageCircle className="h-8 w-8" />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className={`bg-white rounded-lg shadow-2xl border border-gray-200 w-[500px] transition-all duration-300 ${
        isMinimized ? 'h-16' : 'h-[600px]'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-t-lg">
          <div className="flex items-center space-x-2">
            <Brain className="h-6 w-6" />
            <span className="font-semibold text-base">Chat</span>
          </div>
          <div className="flex space-x-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
              title={isMinimized ? "Expandir" : "Minimizar"}
            >
              {isMinimized ? <Maximize2 className="h-5 w-5" /> : <Minimize2 className="h-5 w-5" />}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
              title="Fechar"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Chat Content */}
        {!isMinimized && (
          <>
            {/* Messages */}
            <div 
              ref={messagesRef}
              className="flex-1 overflow-y-auto p-4 space-y-4 h-[460px]"
            >
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-sm px-4 py-3 rounded-lg text-sm ${
                      msg.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : msg.type === 'error'
                        ? 'bg-red-100 text-red-800 border border-red-200'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.message}</div>
                    <div className="text-xs opacity-70 mt-1">
                      {msg.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 max-w-sm px-4 py-3 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                      <span className="text-sm">Pensando...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="Digite sua pergunta..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                  disabled={loading}
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !input.trim()}
                  className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default FloatingChat;
