import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Target, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Activity,
  Award,
  MapPin,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  PlayCircle,
  Building2,
  BarChart3,
  Filter,
  RefreshCw
} from 'lucide-react';

// Configuração da URL da API
const API_URL = import.meta.env.VITE_API_URL || 
               (import.meta.env.PROD 
                 ? 'https://fastapi.urbanmt.com.br' 
                 : 'http://localhost:8000');

const MetasCidadesIntegrado = () => {
  const [fases, setFases] = useState([]);
  const [metas, setMetas] = useState([]);
  const [cidades, setCidades] = useState([]);
  const [campanhas, setCampanhas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('overview'); // overview, fases, metas
  const [filtros, setFiltros] = useState({
    fase_id: '',
    cidade_id: '',
    periodo: ''
  });

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Buscar dados em paralelo
      const [fasesRes, metasRes, cidadesRes, campanhasRes] = await Promise.all([
        fetch(`${API_URL}/api/fases-planejamento`),
        fetch(`${API_URL}/api/metas-progressivas`),
        fetch(`${API_URL}/api/cidades`),
        fetch(`${API_URL}/api/dashboard-executivo/campanhas`)
      ]);

      const [fasesData, metasData, cidadesData, campanhasData] = await Promise.all([
        fasesRes.json(),
        metasRes.json(),
        cidadesRes.json(),
        campanhasRes.json()
      ]);

      setFases(fasesData);
      setMetas(metasData);
      setCidades(cidadesData);
      setCampanhas(campanhasData.campanhas || []);
      
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const calcularResumoGeral = () => {
    if (!fases.length || !metas.length) return {};

    const totalFases = fases.length;
    const fasesAtivas = fases.filter(f => f.status === 'em_execucao').length;
    const totalMetas = metas.length;
    const metasAtingidas = metas.filter(m => m.atingida).length;
    const investimentoTotal = metas.reduce((sum, m) => sum + m.investimento_previsto, 0);
    const receitaEsperada = metas.reduce((sum, m) => sum + m.meta_receita, 0);
    const progressoMedio = fases.reduce((sum, f) => sum + f.progresso_percentual, 0) / totalFases;

    // Agrupar metas por cidade para analytics
    const metasPorCidade = metas.reduce((acc, meta) => {
      const cidade = meta.cidade_nome;
      if (!acc[cidade]) {
        acc[cidade] = {
          totalMetas: 0,
          metasAtingidas: 0,
          investimento: 0,
          receita: 0
        };
      }
      acc[cidade].totalMetas++;
      if (meta.atingida) acc[cidade].metasAtingidas++;
      acc[cidade].investimento += meta.investimento_previsto;
      acc[cidade].receita += meta.meta_receita;
      return acc;
    }, {});

    return {
      totalFases,
      fasesAtivas,
      totalMetas,
      metasAtingidas,
      taxaAtingimento: (metasAtingidas / totalMetas) * 100,
      investimentoTotal,
      receitaEsperada,
      progressoMedio,
      metasPorCidade,
      cidadesCobertas: Object.keys(metasPorCidade).length
    };
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'em_execucao':
        return <PlayCircle className="h-4 w-4 text-blue-500" />;
      case 'concluida':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'planejada':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
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
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const resumo = calcularResumoGeral();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Gestão Estratégica de Metas
          </h1>
          <p className="text-gray-600 mt-1">
            Visão integrada de fases de planejamento e metas progressivas
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={fetchAllData}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Atualizar</span>
          </button>
          <div className="bg-green-100 p-3 rounded-lg">
            <Target className="h-8 w-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Navegação */}
      <div className="bg-white rounded-lg shadow-md border">
        <div className="flex border-b">
          {[
            { id: 'overview', label: 'Visão Geral', icon: BarChart3 },
            { id: 'fases', label: 'Fases de Planejamento', icon: Calendar },
            { id: 'metas', label: 'Metas Progressivas', icon: Target }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors ${
                  activeView === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Conteúdo baseado na view ativa */}
      {activeView === 'overview' && (
        <div className="space-y-6">
          {/* Resumo Executivo */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white p-6 rounded-lg shadow-md border"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Fases Ativas</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {resumo.fasesAtivas}/{resumo.totalFases}
                  </p>
                </div>
                <Calendar className="h-8 w-8 text-blue-500" />
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
                  <p className="text-sm text-gray-600">Metas Atingidas</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {resumo.metasAtingidas}/{resumo.totalMetas}
                  </p>
                  <p className="text-xs text-green-600">{resumo.taxaAtingimento?.toFixed(1)}%</p>
                </div>
                <Target className="h-8 w-8 text-green-500" />
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
                  <p className="text-sm text-gray-600">Cidades Cobertas</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {resumo.cidadesCobertas}
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
                    {resumo.progressoMedio?.toFixed(1)}%
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-orange-500" />
              </div>
            </motion.div>
          </div>

          {/* Resumo por Cidade */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Resumo por Cidade</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(resumo.metasPorCidade || {}).map(([cidade, data]) => (
                  <div key={cidade} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-900">{cidade}</h4>
                      <MapPin className="h-4 w-4 text-gray-400" />
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Metas:</span>
                        <span className="font-medium">{data.metasAtingidas}/{data.totalMetas}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Taxa:</span>
                        <span className="font-medium text-green-600">
                          {((data.metasAtingidas / data.totalMetas) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Investimento:</span>
                        <span className="font-medium">{formatCurrency(data.investimento)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === 'fases' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {fases.map((fase, index) => (
            <motion.div
              key={fase.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg shadow-md border overflow-hidden"
            >
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">{fase.nome}</h3>
                  {getStatusIcon(fase.status)}
                </div>
                <p className="text-blue-100 text-sm mt-1">{fase.descricao}</p>
              </div>

              <div className="p-4 space-y-4">
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

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Orçamento</span>
                    <span className="font-medium">{formatCurrency(fase.orcamento_previsto)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Empenhado</span>
                    <span className="font-medium text-blue-600">{formatCurrency(fase.orcamento_empenhado)}</span>
                  </div>
                </div>

                <div className="border-t pt-4">
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
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {activeView === 'metas' && (
        <div className="space-y-6">
          {/* Filtros rápidos */}
          <div className="bg-white p-4 rounded-lg shadow-md border">
            <div className="flex items-center space-x-4">
              <Filter className="h-5 w-5 text-gray-500" />
              <select
                value={filtros.cidade_id}
                onChange={(e) => setFiltros(prev => ({ ...prev, cidade_id: e.target.value }))}
                className="border rounded-md px-3 py-2"
              >
                <option value="">Todas as Cidades</option>
                {cidades.map(cidade => (
                  <option key={cidade.id} value={cidade.id}>
                    {cidade.cidade}
                  </option>
                ))}
              </select>
              <select
                value={filtros.periodo}
                onChange={(e) => setFiltros(prev => ({ ...prev, periodo: e.target.value }))}
                className="border rounded-md px-3 py-2"
              >
                <option value="">Todos os Períodos</option>
                <option value="1">1 Mês</option>
                <option value="3">3 Meses</option>
                <option value="6">6 Meses</option>
                <option value="12">12 Meses</option>
              </select>
            </div>
          </div>

          {/* Lista simplificada de metas */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {metas
              .filter(meta => {
                if (filtros.cidade_id && meta.cidade_id !== parseInt(filtros.cidade_id)) return false;
                if (filtros.periodo && meta.mes !== parseInt(filtros.periodo)) return false;
                return true;
              })
              .slice(0, 12) // Limitar para performance
              .map((meta, index) => (
                <motion.div
                  key={meta.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-white rounded-lg shadow-md border p-4"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{meta.cidade_nome}</h4>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {meta.mes}m
                    </span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Corridas:</span>
                      <span className="font-medium">{meta.resultado_corridas}/{meta.meta_corridas}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Progresso:</span>
                      <span className="font-medium text-blue-600">
                        {meta.percentual_atingido_geral?.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Investimento:</span>
                      <span className="font-medium">{formatCurrency(meta.investimento_previsto)}</span>
                    </div>
                  </div>

                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full"
                        style={{ width: `${meta.percentual_atingido_geral}%` }}
                      ></div>
                    </div>
                  </div>
                </motion.div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MetasCidadesIntegrado;
