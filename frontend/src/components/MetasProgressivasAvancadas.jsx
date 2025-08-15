import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Target, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Activity,
  MapPin,
  Clock,
  Award,
  BarChart3,
  LineChart,
  Filter,
  Calendar,
  Building2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

// Configuração da URL da API
const API_URL = import.meta.env.VITE_API_URL || 
               (import.meta.env.PROD 
                 ? 'https://fastapi.urbanmt.com.br' 
                 : 'http://localhost:8000');

const MetasProgressivasAvancadas = () => {
  const [metas, setMetas] = useState([]);
  const [cidades, setCidades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtros
  const [filtros, setFiltros] = useState({
    cidade_id: '',
    mes: '',
    status: '',
    tipo_meta: ''
  });

  useEffect(() => {
    fetchCidades();
    fetchMetas();
  }, []);

  useEffect(() => {
    fetchMetas();
  }, [filtros]);

  const fetchCidades = async () => {
    try {
      const response = await fetch(`${API_URL}/api/cidades`);
      if (!response.ok) throw new Error('Erro ao buscar cidades');
      const data = await response.json();
      setCidades(data);
    } catch (err) {
      console.error('Erro ao buscar cidades:', err);
    }
  };

  const fetchMetas = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      // Adicionar filtros não vazios
      Object.keys(filtros).forEach(key => {
        if (filtros[key]) {
          params.append(key, filtros[key]);
        }
      });

      const response = await fetch(`${API_URL}/api/metas-progressivas?${params}`);
      if (!response.ok) throw new Error('Erro ao buscar metas');
      const data = await response.json();
      setMetas(data);
    } catch (err) {
      setError(err.message);
      console.error('Erro ao buscar metas:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFiltroChange = (key, value) => {
    setFiltros(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFiltros = () => {
    setFiltros({
      cidade_id: '',
      mes: '',
      status: '',
      tipo_meta: ''
    });
  };

  const getTipoMetaColor = (tipo) => {
    switch (tipo) {
      case 'muito_baixa':
        return 'bg-blue-100 text-blue-800';
      case 'baixa':
        return 'bg-green-100 text-green-800';
      case 'media':
        return 'bg-yellow-100 text-yellow-800';
      case 'alta':
        return 'bg-orange-100 text-orange-800';
      case 'agressiva':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status, atingida) => {
    if (atingida) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    switch (status) {
      case 'ativa':
        return <Activity className="h-4 w-4 text-blue-500" />;
      case 'pausada':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'cancelada':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Target className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', { 
      style: 'currency', 
      currency: 'BRL' 
    }).format(value);
  };

  const calcularResumo = () => {
    if (!metas.length) return {};

    const totalMetas = metas.length;
    const metasAtingidas = metas.filter(m => m.atingida).length;
    const investimentoTotal = metas.reduce((sum, m) => sum + m.investimento_previsto, 0);
    const receitaEsperada = metas.reduce((sum, m) => sum + m.meta_receita, 0);
    const progressoMedio = metas.reduce((sum, m) => sum + m.percentual_atingido_geral, 0) / totalMetas;

    return {
      totalMetas,
      metasAtingidas,
      taxaAtingimento: (metasAtingidas / totalMetas) * 100,
      investimentoTotal,
      receitaEsperada,
      progressoMedio
    };
  };

  const resumo = calcularResumo();

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
            Metas Progressivas
          </h1>
          <p className="text-gray-600 mt-1">
            Acompanhamento detalhado das metas por cidade e período
          </p>
        </div>
        <div className="bg-purple-100 p-3 rounded-lg">
          <Target className="h-8 w-8 text-purple-600" />
        </div>
      </div>

      {/* Resumo Geral */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white p-4 rounded-lg shadow-md border"
        >
          <div className="text-center">
            <p className="text-sm text-gray-600">Total de Metas</p>
            <p className="text-2xl font-bold text-gray-900">{resumo.totalMetas}</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white p-4 rounded-lg shadow-md border"
        >
          <div className="text-center">
            <p className="text-sm text-gray-600">Metas Atingidas</p>
            <p className="text-2xl font-bold text-green-600">{resumo.metasAtingidas}</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-4 rounded-lg shadow-md border"
        >
          <div className="text-center">
            <p className="text-sm text-gray-600">Taxa de Atingimento</p>
            <p className="text-2xl font-bold text-blue-600">{resumo.taxaAtingimento?.toFixed(1)}%</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-4 rounded-lg shadow-md border"
        >
          <div className="text-center">
            <p className="text-sm text-gray-600">Progresso Médio</p>
            <p className="text-2xl font-bold text-purple-600">{resumo.progressoMedio?.toFixed(1)}%</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white p-4 rounded-lg shadow-md border"
        >
          <div className="text-center">
            <p className="text-sm text-gray-600">Investimento</p>
            <p className="text-lg font-bold text-orange-600">{formatCurrency(resumo.investimentoTotal)}</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white p-4 rounded-lg shadow-md border"
        >
          <div className="text-center">
            <p className="text-sm text-gray-600">Receita Esperada</p>
            <p className="text-lg font-bold text-green-600">{formatCurrency(resumo.receitaEsperada)}</p>
          </div>
        </motion.div>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow-md border">
        <div className="flex items-center space-x-4 mb-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <h3 className="font-medium text-gray-900">Filtros</h3>
          <button
            onClick={clearFiltros}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Limpar Filtros
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filtros.cidade_id}
            onChange={(e) => handleFiltroChange('cidade_id', e.target.value)}
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
            value={filtros.mes}
            onChange={(e) => handleFiltroChange('mes', e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">Todos os Períodos</option>
            <option value="1">1 Mês</option>
            <option value="2">2 Meses</option>
            <option value="3">3 Meses</option>
            <option value="6">6 Meses</option>
            <option value="12">12 Meses</option>
          </select>

          <select
            value={filtros.tipo_meta}
            onChange={(e) => handleFiltroChange('tipo_meta', e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">Todos os Tipos</option>
            <option value="muito_baixa">Muito Baixa</option>
            <option value="baixa">Baixa</option>
            <option value="media">Média</option>
            <option value="alta">Alta</option>
            <option value="agressiva">Agressiva</option>
          </select>

          <select
            value={filtros.status}
            onChange={(e) => handleFiltroChange('status', e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">Todos os Status</option>
            <option value="ativa">Ativa</option>
            <option value="pausada">Pausada</option>
            <option value="concluida">Concluída</option>
            <option value="cancelada">Cancelada</option>
          </select>
        </div>
      </div>

      {/* Lista de Metas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {metas.map((meta, index) => (
          <motion.div
            key={meta.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-lg shadow-md border overflow-hidden"
          >
            {/* Header da Meta */}
            <div className="bg-gradient-to-r from-purple-500 to-blue-600 text-white p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <h3 className="font-semibold">{meta.cidade_nome}</h3>
                </div>
                {getStatusIcon(meta.status, meta.atingida)}
              </div>
              <div className="flex items-center space-x-2 mt-1">
                <Calendar className="h-4 w-4" />
                <span className="text-sm">{meta.mes} mês(es)</span>
                <span className={`px-2 py-1 rounded-full text-xs ${getTipoMetaColor(meta.tipo_meta)}`}>
                  {meta.tipo_meta.replace('_', ' ')}
                </span>
              </div>
            </div>

            {/* Conteúdo da Meta */}
            <div className="p-4 space-y-4">
              {/* Progresso Geral */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Progresso Geral</span>
                  <span className="text-sm font-medium">{meta.percentual_atingido_geral?.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${meta.percentual_atingido_geral}%` }}
                  ></div>
                </div>
              </div>

              {/* Metas vs Resultados */}
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Metas vs Resultados</h4>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Corridas</span>
                    <div className="text-right">
                      <span className="font-medium">{meta.resultado_corridas}/{meta.meta_corridas}</span>
                      <div className="text-xs text-gray-500">
                        {meta.percentual_atingido_corridas?.toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Motoristas</span>
                    <div className="text-right">
                      <span className="font-medium">{meta.resultado_motoristas}/{meta.meta_motoristas}</span>
                      <div className="text-xs text-gray-500">
                        {meta.percentual_atingido_motoristas?.toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Usuários Ativos</span>
                    <span className="font-medium">{meta.resultado_usuarios_ativos}/{meta.meta_usuarios_ativos}</span>
                  </div>
                </div>
              </div>

              {/* Financeiro */}
              <div className="border-t pt-3">
                <h4 className="font-medium text-gray-900 mb-2">Financeiro</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Meta de Receita</span>
                    <span className="font-medium">{formatCurrency(meta.meta_receita)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Receita Atual</span>
                    <span className="font-medium text-green-600">{formatCurrency(meta.resultado_receita)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Investimento</span>
                    <span className="font-medium text-orange-600">{formatCurrency(meta.investimento_previsto)}</span>
                  </div>
                  {meta.roi_meta > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">ROI</span>
                      <span className="font-medium text-purple-600">{meta.roi_meta?.toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Estratégia */}
              {meta.estrategia && (
                <div className="bg-gray-50 p-3 rounded text-sm">
                  <p className="text-gray-700">{meta.estrategia}</p>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {metas.length === 0 && (
        <div className="text-center py-12">
          <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Nenhuma meta encontrada com os filtros selecionados.</p>
        </div>
      )}
    </div>
  );
};

export default MetasProgressivasAvancadas;
