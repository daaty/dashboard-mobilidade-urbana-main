import React, { useState, useEffect, useRef } from 'react';
import { Brain, TrendingUp, AlertCircle, Lightbulb, BarChart3, RefreshCw, MessageCircle, Target, Users, DollarSign, MapPin, Calendar, Send, X, Minimize2 } from 'lucide-react';

// URL da API do agente (local para desenvolvimento, Heroku para produção)
const AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL || 
  (import.meta.env.PROD 
    ? 'https://dashboard-mobility-agent.herokuapp.com' 
    : 'http://localhost:8001');

const SistemaIA = () => {
  const [insights, setInsights] = useState(null);
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState({
    insights: false,
    reports: false
  });
  const [error, setError] = useState(null);
  const [analysisType, setAnalysisType] = useState('performance');
  
  // Estados do Chat
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMinimized, setChatMinimized] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      type: 'agent',
      message: 'Olá! Sou o agente AGNO inteligente. Como posso ajudá-lo hoje?',
      timestamp: new Date()
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatMessagesRef = useRef(null);

  // Tipos de análise disponíveis
  const analysisTypes = [
    { id: 'performance', name: 'Análise de Performance', icon: TrendingUp, color: 'blue' },
    { id: 'financial', name: 'Saúde Financeira', icon: DollarSign, color: 'green' },
    { id: 'drivers', name: 'Performance de Motoristas', icon: Users, color: 'purple' },
    { id: 'expansion', name: 'Expansão Geográfica', icon: MapPin, color: 'orange' },
    { id: 'trends', name: 'Tendências de Mercado', icon: Calendar, color: 'pink' },
    { id: 'executive', name: 'Relatório Executivo', icon: Target, color: 'indigo' }
  ];

  const fetchAnalysis = async (type) => {
    setLoading(prev => ({ ...prev, insights: true }));
    setError(null);
    
    try {
      const response = await fetch(`${AGENT_API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_type: type,
          parameters: {}
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setInsights({
          type: type,
          result: data.result,
          timestamp: data.timestamp,
          metadata: data.metadata
        });
      } else {
        setError('Erro ao gerar análise: ' + (data.detail || 'Erro desconhecido'));
      }
    } catch (err) {
      setError('Erro de conexão com o agente: ' + err.message);
      console.error('Erro na análise:', err);
    } finally {
      setLoading(prev => ({ ...prev, insights: false }));
    }
  };

  const fetchExecutiveReport = async () => {
    setLoading(prev => ({ ...prev, reports: true }));
    setError(null);
    
    try {
      const response = await fetch(`${AGENT_API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_type: 'executive',
          parameters: {}
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setReports({
          result: data.result,
          timestamp: data.timestamp
        });
      } else {
        setError('Erro ao gerar relatório: ' + (data.detail || 'Erro desconhecido'));
      }
    } catch (err) {
      setError('Erro de conexão com o agente: ' + err.message);
      console.error('Erro no relatório:', err);
    } finally {
      setLoading(prev => ({ ...prev, reports: false }));
    }
  };

  // Função para enviar mensagem no chat
  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      type: 'user',
      message: chatInput,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const currentInput = chatInput;
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await fetch(`${AGENT_API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentInput,
          context: {}
        })
      });

      const data = await response.json();

      if (data.success) {
        const agentMessage = {
          type: 'agent',
          message: data.result,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, agentMessage]);
      } else {
        const errorMessage = {
          type: 'error',
          message: 'Erro ao processar sua pergunta. Tente novamente.',
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (err) {
      const errorMessage = {
        type: 'error',
        message: 'Erro de conexão. Verifique sua conexão e tente novamente.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  // Scroll automático no chat
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatMessages]);

  useEffect(() => {
    // Carrega análise inicial automaticamente
    fetchAnalysis('performance');
  }, []);

  const formatContent = (content) => {
    if (!content) return [];
    
    return content.split('\n').filter(line => line.trim()).map((line, index) => {
      const trimmedLine = line.trim();
      
      // Detectar títulos (começam com #)
      if (trimmedLine.startsWith('#')) {
        const level = (trimmedLine.match(/^#+/) || [''])[0].length;
        const text = trimmedLine.replace(/^#+\s*/, '');
        const headerClass = level === 1 ? 'text-lg font-bold text-gray-900 mt-4 mb-2' :
                          level === 2 ? 'text-base font-semibold text-gray-800 mt-3 mb-2' :
                          'text-sm font-medium text-gray-700 mt-2 mb-1';
        
        return (
          <div key={index} className={headerClass}>
            {text}
          </div>
        );
      }
      
      // Detectar listas (começam com - ou *)
      if (trimmedLine.match(/^[-*]\s/)) {
        const text = trimmedLine.replace(/^[-*]\s/, '');
        return (
          <div key={index} className="flex items-start space-x-2 text-sm text-gray-600 mb-1">
            <span className="text-blue-500 mt-1">•</span>
            <span>{text}</span>
          </div>
        );
      }
      
      // Detectar números (começam com números)
      if (trimmedLine.match(/^\d+\.\s/)) {
        return (
          <div key={index} className="text-sm text-gray-600 mb-1 ml-4">
            {trimmedLine}
          </div>
        );
      }
      
      // Texto normal
      if (trimmedLine) {
        return (
          <p key={index} className="text-sm text-gray-600 mb-2">
            {trimmedLine}
          </p>
        );
      }
      
      return null;
    }).filter(Boolean);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
              <Brain className="h-7 w-7 text-blue-600" />
              <span>IA & Insights</span>
            </h2>
            <p className="text-gray-600 mt-2">
              Análises inteligentes geradas pelo agente AGNO com raciocínio avançado
            </p>
          </div>
        
          <div className="flex space-x-2">
            <button
              onClick={() => setChatOpen(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
            >
              <MessageCircle className="h-4 w-4" />
              <span>Chat com Agente</span>
            </button>
            
            <button
              onClick={fetchExecutiveReport}
              disabled={loading.reports}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              <BarChart3 className={`h-4 w-4 ${loading.reports ? 'animate-spin' : ''}`} />
              <span>Relatório Executivo</span>
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Seletor de Tipo de Análise */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tipos de Análise</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {analysisTypes.map((type) => {
            const Icon = type.icon;
            const isActive = analysisType === type.id;
            return (
              <button
                key={type.id}
                onClick={() => {
                  setAnalysisType(type.id);
                  fetchAnalysis(type.id);
                }}
                disabled={loading.insights}
                className={`flex items-center space-x-2 p-3 rounded-lg border-2 transition-all ${
                  isActive
                    ? `border-${type.color}-500 bg-${type.color}-50 text-${type.color}-700`
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="text-sm font-medium">{type.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Grid com 2 colunas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Insights Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-gray-900">Análise Atual</h3>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {analysisTypes.find(t => t.id === analysisType)?.name || 'Análise Personalizada'}
            </p>
          </div>
          
          <div className="p-6">
            {loading.insights ? (
              <div className="flex items-center justify-center py-8">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">Analisando dados...</span>
                </div>
              </div>
            ) : insights ? (
              <div className="prose prose-sm max-w-none">
                {formatContent(insights.result)}
                <p className="text-xs text-gray-500 mt-4 border-t pt-2">
                  Análise gerada em: {new Date(insights.timestamp).toLocaleString()}
                </p>
              </div>
            ) : (
              <div className="text-center py-8">
                <Lightbulb className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Selecione um tipo de análise acima</p>
              </div>
            )}
          </div>
        </div>

        {/* Relatório Executivo Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-900">Relatório Executivo</h3>
            </div>
            <p className="text-sm text-gray-600 mt-1">Resumo completo para tomada de decisão</p>
          </div>
          
          <div className="p-6">
            {loading.reports ? (
              <div className="flex items-center justify-center py-8">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">Gerando relatório executivo...</span>
                </div>
              </div>
            ) : reports ? (
              <div className="prose prose-sm max-w-none">
                {formatContent(reports.result)}
                <p className="text-xs text-gray-500 mt-4 border-t pt-2">
                  Relatório gerado em: {new Date(reports.timestamp).toLocaleString()}
                </p>
              </div>
            ) : (
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Clique em "Relatório Executivo" para gerar análise completa</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Status do Agente */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 text-purple-600 mr-2" />
          Status do Agente AGNO
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">🧠</div>
            <div className="text-sm font-medium text-gray-700">Framework AGNO</div>
            <div className="text-xs text-gray-500">Reasoning Avançado</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">🤖</div>
            <div className="text-sm font-medium text-gray-700">OpenAI GPT-4</div>
            <div className="text-xs text-gray-500">Modelo de Linguagem</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">🗄️</div>
            <div className="text-sm font-medium text-gray-700">Memória PostgreSQL</div>
            <div className="text-xs text-gray-500">Aprendizado Contínuo</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">⚡</div>
            <div className="text-sm font-medium text-gray-700">API Dedicada</div>
            <div className="text-xs text-gray-500">Análises em Tempo Real</div>
          </div>
        </div>
      </div>

      {/* Modal de Chat */}
      {chatOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setChatOpen(false)}></div>
          
          <div className={`absolute right-4 top-4 bottom-4 w-96 bg-white rounded-lg shadow-2xl flex flex-col transition-transform ${
            chatMinimized ? 'transform translate-y-full' : ''
          }`}>
            {/* Header do Chat */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-t-lg">
              <div className="flex items-center space-x-2">
                <Brain className="h-5 w-5" />
                <span className="font-semibold">Chat com Agente AGNO</span>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setChatMinimized(!chatMinimized)}
                  className="p-1 hover:bg-white hover:bg-opacity-20 rounded"
                >
                  <Minimize2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setChatOpen(false)}
                  className="p-1 hover:bg-white hover:bg-opacity-20 rounded"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {!chatMinimized && (
              <>
                {/* Mensagens do Chat */}
                <div 
                  ref={chatMessagesRef}
                  className="flex-1 overflow-y-auto p-4 space-y-4"
                >
                  {chatMessages.map((msg, index) => (
                    <div
                      key={index}
                      className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          msg.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : msg.type === 'error'
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        <div className="text-sm whitespace-pre-wrap">{msg.message}</div>
                        <div className="text-xs opacity-70 mt-1">
                          {msg.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {chatLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                          <span className="text-sm">Agente pensando...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input do Chat */}
                <div className="p-4 border-t border-gray-200">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendChatMessage()}
                      placeholder="Digite sua pergunta..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                      disabled={chatLoading}
                    />
                    <button
                      onClick={sendChatMessage}
                      disabled={chatLoading || !chatInput.trim()}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                    >
                      <Send className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Pressione Enter para enviar, Shift+Enter para quebra de linha
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SistemaIA;
