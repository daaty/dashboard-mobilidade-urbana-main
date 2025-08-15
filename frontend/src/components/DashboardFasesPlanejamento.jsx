import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Target, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Activity,
  CheckCircle,
  Clock,
  PlayCircle,
  AlertTriangle,
  BarChart3,
  Building2,
  MapPin
} from 'lucide-react';

// Configuração da URL da API
const API_URL = import.meta.env.VITE_API_URL || 
               (import.meta.env.PROD 
                 ? 'https://fastapi.urbanmt.com.br' 
                 : 'http://localhost:8000');

const DashboardFasesPlanejamento = () => {
  const [fases, setFases] = useState([]);
  const [resumoFases, setResumoFases] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFasesData();
    fetchResumoFases();
  }, []);

  const fetchFasesData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/fases-planejamento`);
      if (!response.ok) throw new Error('Erro ao buscar fases');
      const data = await response.json();
      setFases(data);
    } catch (err) {
      setError(err.message);
      console.error('Erro ao buscar fases:', err);
    }
  };

  const fetchResumoFases = async () => {
    try {
      const response = await fetch(`${API_URL}/api/fases-planejamento/resumo`);
      if (!response.ok) throw new Error('Erro ao buscar resumo');
      const data = await response.json();
      setResumoFases(data);
    } catch (err) {
      setError(err.message);
      console.error('Erro ao buscar resumo:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'em_execucao':
        return <PlayCircle className="h-5 w-5 text-blue-500" />;
      case 'concluida':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'planejada':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'suspensa':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'em_execucao':
        return 'bg-blue-100 text-blue-800';
      case 'concluida':
        return 'bg-green-100 text-green-800';
      case 'planejada':
        return 'bg-yellow-100 text-yellow-800';
      case 'suspensa':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', { 
      style: 'currency', 
      currency: 'BRL' 
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold">Erro ao carregar dados</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Fases de Planejamento
          </h1>
          <p className="text-gray-600 mt-1">
            Acompanhe o progresso das fases de expansão
          </p>
        </div>
        <div className="bg-blue-100 p-3 rounded-lg">
          <BarChart3 className="h-8 w-8 text-blue-600" />
        </div>
      </div>

      {/* Resumo Geral */}
      {resumoFases && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white p-6 rounded-lg shadow-md border"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total de Fases</p>
                <p className="text-2xl font-bold text-gray-900">
                  {resumoFases.total_fases_ativas}
                </p>
              </div>
              <Target className="h-8 w-8 text-blue-500" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white p-6 rounded-lg shadow-md border"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Orçamento Total</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(resumoFases.orcamento_total_previsto)}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-500" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white p-6 rounded-lg shadow-md border"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Meta de Cidades</p>
                <p className="text-2xl font-bold text-gray-900">
                  {resumoFases.meta_total_cidades}
                </p>
              </div>
              <Building2 className="h-8 w-8 text-purple-500" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white p-6 rounded-lg shadow-md border"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Progresso Médio</p>
                <p className="text-2xl font-bold text-gray-900">
                  {resumoFases.progresso_medio?.toFixed(1)}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-orange-500" />
            </div>
          </motion.div>
        </div>
      )}

      {/* Lista de Fases */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {fases.map((fase, index) => (
          <motion.div
            key={fase.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-lg shadow-md border overflow-hidden"
          >
            {/* Header da Fase */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{fase.nome}</h3>
                {getStatusIcon(fase.status)}
              </div>
              <p className="text-blue-100 text-sm mt-1">{fase.descricao}</p>
            </div>

            {/* Conteúdo da Fase */}
            <div className="p-4 space-y-4">
              {/* Status e Progresso */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(fase.status)}`}>
                    {fase.status.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-600">
                    {fase.progresso_percentual?.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${fase.progresso_percentual}%` }}
                  ></div>
                </div>
              </div>

              {/* Datas */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Início</p>
                  <p className="font-medium">{formatDate(fase.data_inicio)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Fim</p>
                  <p className="font-medium">{formatDate(fase.data_fim)}</p>
                </div>
              </div>

              {/* Métricas Financeiras */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Orçamento Previsto</span>
                  <span className="font-medium">{formatCurrency(fase.orcamento_previsto)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Empenhado</span>
                  <span className="font-medium text-blue-600">{formatCurrency(fase.orcamento_empenhado)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Pago</span>
                  <span className="font-medium text-green-600">{formatCurrency(fase.orcamento_pago)}</span>
                </div>
              </div>

              {/* Metas e Resultados */}
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-2">Metas vs Resultados</h4>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div className="text-center">
                    <p className="text-gray-600">Cidades</p>
                    <p className="font-bold">{fase.resultado_cidades}/{fase.meta_cidades}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-600">Motoristas</p>
                    <p className="font-bold">{fase.resultado_motoristas}/{fase.meta_motoristas}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-600">Corridas</p>
                    <p className="font-bold">{fase.resultado_corridas}/{fase.meta_corridas}</p>
                  </div>
                </div>
              </div>

              {/* Responsável */}
              {fase.responsavel && (
                <div className="flex items-center space-x-2 text-sm">
                  <Users className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-600">Responsável:</span>
                  <span className="font-medium">{fase.responsavel}</span>
                </div>
              )}

              {/* Observações */}
              {fase.observacoes && (
                <div className="bg-gray-50 p-3 rounded text-sm">
                  <p className="text-gray-700">{fase.observacoes}</p>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default DashboardFasesPlanejamento;
