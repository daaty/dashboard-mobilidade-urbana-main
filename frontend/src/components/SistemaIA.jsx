import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, AlertCircle, Lightbulb, BarChart3, RefreshCw } from 'lucide-react';

const SistemaIA = () => {
  const [insights, setInsights] = useState(null);
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState({
    insights: false,
    reports: false
  });
  const [error, setError] = useState(null);

  const fetchInsights = async () => {
    setLoading(prev => ({ ...prev, insights: true }));
    setError(null);
    
    try {
      const response = await fetch('/api/llm/insights', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await response.json();
      
      if (data.success) {
        setInsights(data.data);
      } else {
        setError('Erro ao gerar insights');
      }
    } catch (err) {
      setError('Erro de conexão ao gerar insights');
    } finally {
      setLoading(prev => ({ ...prev, insights: false }));
    }
  };

  const fetchReports = async () => {
    setLoading(prev => ({ ...prev, reports: true }));
    setError(null);
    
    try {
      const response = await fetch('/api/llm/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}) // Dados serão obtidos do dashboard automaticamente
      });
      
      const data = await response.json();
      
      if (data.success) {
        setReports(data.data);
      } else {
        setError('Erro ao gerar relatório');
      }
    } catch (err) {
      setError('Erro de conexão ao gerar relatório');
    } finally {
      setLoading(prev => ({ ...prev, reports: false }));
    }
  };

  useEffect(() => {
    // Carrega insights automaticamente ao montar o componente
    fetchInsights();
  }, []);

  const formatContent = (content) => {
    if (!content) return [];
    
    return content.split('\n').filter(line => line.trim()).map((line, index) => (
      <p key={index} className="mb-2 text-sm leading-relaxed">
        {line.trim()}
      </p>
    ));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="h-8 w-8 text-purple-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Sistema de IA</h2>
            <p className="text-gray-600">Insights inteligentes e relatórios automatizados</p>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={fetchInsights}
          disabled={loading.insights}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${loading.insights ? 'animate-spin' : ''}`} />
          <span>Atualizar Insights</span>
        </button>          <button
            onClick={fetchReports}
            disabled={loading.reports}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            <BarChart3 className={`h-4 w-4 ${loading.reports ? 'animate-spin' : ''}`} />
            <span>Gerar Relatório</span>
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Insights Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-gray-900">Insights Inteligentes</h3>
            </div>
            <p className="text-sm text-gray-600 mt-1">Análises automáticas dos dados</p>
          </div>
          
          <div className="p-6">
            {loading.insights ? (
              <div className="flex items-center justify-center py-8">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
                  <span className="text-gray-600">Gerando insights...</span>
                </div>
              </div>
            ) : insights ? (
              <div className="prose prose-sm max-w-none">
                {insights.insights ? formatContent(insights.insights) : (
                  <p className="text-gray-600">Nenhum insight disponível no momento.</p>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <Lightbulb className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Clique em "Atualizar Insights" para gerar análises</p>
              </div>
            )}
          </div>
        </div>

        {/* Reports Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-900">Relatório Executivo</h3>
            </div>
            <p className="text-sm text-gray-600 mt-1">Relatório detalhado automático</p>
          </div>
          
          <div className="p-6">
            {loading.reports ? (
              <div className="flex items-center justify-center py-8">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">Gerando relatório...</span>
                </div>
              </div>
            ) : reports ? (
              <div className="prose prose-sm max-w-none">
                {reports.report ? formatContent(reports.report) : (
                  <p className="text-gray-600">Nenhum relatório disponível no momento.</p>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Clique em "Gerar Relatório" para criar análise executiva</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Estatísticas do Sistema */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 text-purple-600 mr-2" />
          Status do Sistema de IA
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">✅</div>
            <div className="text-sm font-medium text-gray-700">LLM Ativo</div>
            <div className="text-xs text-gray-500">Gemini 1.5 Flash</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">🚀</div>
            <div className="text-sm font-medium text-gray-700">Cache Ativo</div>
            <div className="text-xs text-gray-500">Respostas Otimizadas</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">⚡</div>
            <div className="text-sm font-medium text-gray-700">Tempo Real</div>
            <div className="text-xs text-gray-500">Análises Instantâneas</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SistemaIA;
