import React, { useState, useEffect, useRef } from 'react';
import { Brain, TrendingUp, AlertCircle, Lightbulb, BarChart3, RefreshCw, MessageCircle, Target, Users, DollarSign, MapPin, Calendar, Send, X, Minimize2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

// URL da API do agente - usando o endpoint do playground
const AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL || 
  (import.meta.env.PROD 
    ? 'https://agentdash.urbanmt.com.br' 
    : 'http://localhost:8001');

// ID do agente para o playground
const AGENT_ID = 'mobility-agent-sistema-ia';

const SistemaIA = () => {
  const { user } = useAuth(); // Capturar dados do usuário autenticado
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
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatMessagesRef = useRef(null);

  // Inicializar mensagem de boas-vindas personalizada
  useEffect(() => {
    const userName = user?.username && user.username !== 'Usuário' ? user.username : null;
    const welcomeMessage = userName 
      ? `Olá ${userName}! Bem-vindo ao Sistema de IA & Insights. Como posso ajudá-lo com análises de mobilidade urbana hoje?`
      : 'Olá! Bem-vindo ao Sistema de IA & Insights. Como posso ajudá-lo com análises de mobilidade urbana hoje?';
    
    setChatMessages([{
      type: 'agent',
      message: welcomeMessage,
      timestamp: new Date()
    }]);
  }, [user?.username]);

  // Tipos de análise disponíveis
  const analysisTypes = [
    { id: 'performance', name: 'Análise de Performance', icon: TrendingUp, color: 'blue' },
    { id: 'financial', name: 'Saúde Financeira', icon: DollarSign, color: 'green' },
    { id: 'drivers', name: 'Performance de Motoristas', icon: Users, color: 'purple' },
    { id: 'expansion', name: 'Expansão Geográfica', icon: MapPin, color: 'orange' },
    { id: 'trends', name: 'Tendências de Mercado', icon: Calendar, color: 'pink' },
    { id: 'executive', name: 'Relatório Executivo', icon: Target, color: 'indigo' }
  ];

  // Função auxiliar para usar o novo agente playground
  const callAgent = async (message, sessionId = null) => {
    const userName = user?.username && user.username !== 'Usuário' ? user.username : null;
    const userId = user?.id || user?.username || 'sistema_ia_user';
    
    const payload = {
      message: message,
      user_id: userId,
      session_id: sessionId || `sistema_ia_${userId}_${Date.now()}`
    };
    
    // Só adicionar user_name se realmente tiver um nome válido
    if (userName) {
      payload.user_name = userName;
    }
    
    const response = await fetch(`${AGENT_API_URL}/v1/playground/agents/${AGENT_ID}/runs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (data.status !== 'completed') {
      throw new Error(data.error || 'Falha na execução do agente');
    }
    
    return data.content || data.result || data.message;
  };

  const fetchAnalysis = async (type) => {
    setLoading(prev => ({ ...prev, insights: true }));
    setError(null);
    
    try {
      // Mapear tipos de análise para prompts específicos
      const analysisPrompts = {
        'performance': 'Faça uma análise completa de performance da empresa de mobilidade urbana, incluindo métricas de corridas, cancelamentos e tendências.',
        'financial': 'Analise a saúde financeira da empresa, incluindo receitas, custos operacionais e projeções.',
        'drivers': 'Analise a performance dos motoristas, incluindo ratings, eficiência e padrões de comportamento.',
        'expansion': 'Avalie oportunidades de expansão geográfica com base nos dados atuais de performance por cidade.',
        'trends': 'Identifique tendências de mercado e padrões sazonais nos dados de mobilidade urbana.',
        'executive': 'Gere um relatório executivo completo com insights estratégicos e recomendações para a alta direção.'
      };
      
      const prompt = analysisPrompts[type] || `Faça uma análise de ${type} dos dados de mobilidade urbana.`;
      const result = await callAgent(prompt);
      
      setInsights({
        type: type,
        result: result,
        timestamp: new Date().toISOString(),
        metadata: { source: 'agente_playground' }
      });
    } catch (err) {
      setError('Erro ao gerar análise: ' + err.message);
      console.error('Erro na análise:', err);
    } finally {
      setLoading(prev => ({ ...prev, insights: false }));
    }
  };

  const fetchExecutiveReport = async () => {
    setLoading(prev => ({ ...prev, reports: true }));
    setError(null);
    
    try {
      const prompt = 'Gere um relatório executivo detalhado com análise completa da empresa de mobilidade urbana, incluindo KPIs, tendências, insights estratégicos e recomendações acionáveis para a alta direção.';
      const result = await callAgent(prompt);
      
      setReports({
        result: result,
        timestamp: new Date().toISOString()
      });
    } catch (err) {
      setError('Erro ao gerar relatório: ' + err.message);
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
      const result = await callAgent(currentInput, `sistema_ia_chat_${user?.username || 'anonymous'}_${Date.now()}`);
      
      const agentMessage = {
        type: 'agent',
        message: result,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      const errorMessage = {
        type: 'error',
        message: 'Erro ao processar sua pergunta. Tente novamente.',
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
                <Brain className="h-7 w-7 text-blue-600" />
                <span>IA & Insights</span>
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Análises inteligentes geradas pelo agente AGNO com raciocínio avançado
              </p>
            </div>
        
          <div className="flex space-x-2">
            <button
              onClick={() => setChatOpen(true)}
              className="flex items-center space-x-2 px-5 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
            >
              <MessageCircle className="h-5 w-5" />
              <span className="font-medium">Chat com Agente</span>
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
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
            <span className="text-red-800 dark:text-red-200">{error}</span>
          </div>
        )}

        {/* Seletor de Tipo de Análise */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Tipos de Análise</h3>
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
                  className={`flex items-center space-x-2 p-3 rounded-lg border-2 transition-all duration-200 ${
                    isActive
                      ? `border-${type.color}-500 bg-${type.color}-50 dark:bg-${type.color}-900/20 text-${type.color}-700 dark:text-${type.color}-300`
                      : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-600'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
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
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Análise Atual</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {analysisTypes.find(t => t.id === analysisType)?.name || 'Análise Personalizada'}
              </p>
            </div>
            
            <div className="p-6">
              {loading.insights ? (
                <div className="flex items-center justify-center py-8">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600 dark:text-gray-400">Analisando dados...</span>
                  </div>
                </div>
              ) : insights ? (
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  {formatContent(insights.result)}
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 border-t border-gray-200 dark:border-gray-700 pt-2">
                    Análise gerada em: {new Date(insights.timestamp).toLocaleString()}
                  </p>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Lightbulb className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-500 dark:text-gray-400">Selecione um tipo de análise acima</p>
                </div>
              )}
            </div>
          </div>

          {/* Relatório Executivo Card */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-blue-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Relatório Executivo</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Resumo completo para tomada de decisão</p>
            </div>
            
            <div className="p-6">
              {loading.reports ? (
                <div className="flex items-center justify-center py-8">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600 dark:text-gray-400">Gerando relatório executivo...</span>
                  </div>
                </div>
              ) : reports ? (
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  {formatContent(reports.result)}
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 border-t border-gray-200 dark:border-gray-700 pt-2">
                    Relatório gerado em: {new Date(reports.timestamp).toLocaleString()}
                  </p>
                </div>
              ) : (
                <div className="text-center py-8">
                  <BarChart3 className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-500 dark:text-gray-400">Clique em "Relatório Executivo" para gerar análise completa</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Status do Agente */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 text-purple-600 mr-2" />
            Status do Agente AGNO
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">🧠</div>
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Framework AGNO</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Reasoning Avançado</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">🤖</div>
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300">OpenAI GPT-4</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Modelo de Linguagem</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">🗄️</div>
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Memória PostgreSQL</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Aprendizado Contínuo</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">⚡</div>
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300">API Dedicada</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Análises em Tempo Real</div>
            </div>
          </div>
        </div>

        {/* Modal de Chat */}
        {chatOpen && (
          <div className="fixed inset-0 z-50 overflow-hidden">
            <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setChatOpen(false)}></div>
            
            <div className={`absolute right-4 top-4 bottom-4 w-[600px] bg-white dark:bg-gray-800 rounded-xl shadow-2xl flex flex-col transition-transform ${
              chatMinimized ? 'transform translate-y-full' : ''
            }`}>
              {/* Header do Chat */}
              <div className="flex items-center justify-between p-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-t-xl">
                <div className="flex items-center space-x-3">
                  <Brain className="h-6 w-6" />
                  <span className="font-semibold text-lg">Chat com Agente AGNO</span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setChatMinimized(!chatMinimized)}
                    className="p-2 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
                  >
                    <Minimize2 className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => setChatOpen(false)}
                    className="p-2 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {!chatMinimized && (
                <>
                  {/* Mensagens do Chat */}
                  <div 
                    ref={chatMessagesRef}
                    className="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50 dark:bg-gray-900"
                  >
                    {chatMessages.map((msg, index) => (
                      <div
                        key={index}
                        className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-lg px-4 py-3 rounded-lg ${
                          msg.type === 'user'
                            ? 'bg-purple-600 text-white'
                            : msg.type === 'error'
                            ? 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
                            : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600'
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
                        <div className="bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 max-w-lg px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600">
                          <div className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                            <span className="text-sm">Agente pensando...</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Input do Chat */}
                  <div className="p-5 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-b-xl">
                    <div className="flex space-x-3">
                      <input
                        type="text"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendChatMessage()}
                        placeholder="Digite sua pergunta..."
                        className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                        disabled={chatLoading}
                      />
                      <button
                        onClick={sendChatMessage}
                        disabled={chatLoading || !chatInput.trim()}
                        className="px-5 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                      >
                        <Send className="h-5 w-5" />
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      Pressione Enter para enviar, Shift+Enter para quebra de linha
                    </p>
                  </div>
              </>
            )}
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default SistemaIA;
