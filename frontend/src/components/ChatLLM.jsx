import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Bot, User, Loader, X } from 'lucide-react';

const ChatLLM = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: '👋 Olá! Sou seu assistente de IA especializado em mobilidade urbana. Como posso ajudar você a analisar os dados do dashboard?',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    console.log('🚀 Enviando mensagem:', inputValue);
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      console.log('📡 Fazendo requisição para /api/llm/chat');
      const response = await fetch('/api/llm/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue
        })
      });

      console.log('📨 Resposta recebida:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('📊 Dados da resposta:', data);
      
      if (data.success && data.response) {
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: data.response.response || data.response,
          timestamp: new Date(),
          fromCache: data.from_cache
        };
        console.log('✅ Mensagem do bot criada:', botMessage);
        setMessages(prev => [...prev, botMessage]);
      } else {
        console.error('❌ Resposta da API inválida:', data);
        throw new Error('Erro na resposta da API');
      }
    } catch (error) {
      console.error('💥 Erro no chat:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `❌ Erro: ${error.message}. Tente novamente.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatMessage = (content) => {
    // Converte quebras de linha em parágrafos
    return content.split('\n').map((line, index) => (
      <p key={index} className={index > 0 ? 'mt-2' : ''}>
        {line}
      </p>
    ));
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 hover:scale-110 z-50"
        aria-label="Abrir chat com IA"
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bot size={20} />
          <div>
            <h3 className="font-semibold">Assistente IA</h3>
            <p className="text-xs text-blue-100">Mobilidade Urbana</p>
          </div>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white hover:text-blue-200 transition-colors"
          aria-label="Fechar chat"
        >
          <X size={20} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white rounded-br-sm'
                  : message.isError
                  ? 'bg-red-100 text-red-800 rounded-bl-sm'
                  : 'bg-white text-gray-800 rounded-bl-sm border border-gray-200'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'bot' && !message.isError && (
                  <Bot size={16} className="text-blue-600 mt-1 flex-shrink-0" />
                )}
                {message.type === 'user' && (
                  <User size={16} className="text-white mt-1 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <div className="text-sm">
                    {formatMessage(message.content)}
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <span className={`text-xs ${
                      message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
                    }`}>
                      {formatTime(message.timestamp)}
                    </span>
                    {message.fromCache && (
                      <span className="text-xs text-gray-400 ml-2">📱 Cache</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 rounded-lg rounded-bl-sm border border-gray-200 p-3 max-w-[80%]">
              <div className="flex items-center space-x-2">
                <Bot size={16} className="text-blue-600" />
                <Loader size={16} className="animate-spin text-blue-600" />
                <span className="text-sm">Processando...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-white rounded-b-lg">
        <div className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua pergunta sobre mobilidade urbana..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            aria-label="Enviar mensagem"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Pressione Enter para enviar • Shift+Enter para nova linha
        </p>
      </div>
    </div>
  );
};

export default ChatLLM;
