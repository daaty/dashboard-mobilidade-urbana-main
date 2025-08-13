import React, { useState, useEffect } from 'react'
import CampanhasFormList from './CampanhasFormList'
import { motion } from 'framer-motion'
import { 
  Target, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Users, 
  DollarSign, 
  BarChart3,
  Activity,
  XCircle,
  Award,
  Filter,
  MapPin,
  Calendar,
  ChevronDown,
  X,
  Edit,
  Plus,
  Building
} from 'lucide-react'

// Cores consistentes com AnaliseCorreidas
const COLORS = {
  concluidas: '#10B981',
  canceladas: '#EF4444',
  perdidas: '#F59E0B',
  metas: '#3B82F6',
  campanhas: '#8B5CF6'
};

// Componentes UI simplificados (mantendo compatibilidade)
const Card = ({ children, className = "", ...props }) => (
  <div className={`bg-white rounded-lg border shadow-sm ${className}`} {...props}>
    {children}
  </div>
);

const CardContent = ({ children, className = "", ...props }) => (
  <div className={`p-6 ${className}`} {...props}>
    {children}
  </div>
);

const CardHeader = ({ children, className = "", ...props }) => (
  <div className={`px-6 pt-6 pb-0 ${className}`} {...props}>
    {children}
  </div>
);

const CardTitle = ({ children, className = "", ...props }) => (
  <h3 className={`text-lg font-semibold ${className}`} {...props}>
    {children}
  </h3>
);

const Progress = ({ value, className = "", ...props }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`} {...props}>
    <div 
      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
      style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
    />
  </div>
);

const Select = ({ children, onValueChange, value, className = "", ...props }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value || '');

  const handleSelect = (newValue) => {
    setSelectedValue(newValue);
    onValueChange?.(newValue);
    setIsOpen(false);
  };

  return (
    <div className={`relative ${className}`} {...props}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 text-left bg-white border border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 flex items-center justify-between"
      >
        <span>{selectedValue || 'Selecione...'}</span>
        <ChevronDown className="w-4 h-4" />
      </button>
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
          {React.Children.map(children, (child) => 
            React.cloneElement(child, { onSelect: handleSelect })
          )}
        </div>
      )}
    </div>
  );
};

const SelectOption = ({ children, value, onSelect }) => (
  <div
    onClick={() => onSelect(value)}
    className="px-3 py-2 cursor-pointer hover:bg-gray-100 text-sm"
  >
    {children}
  </div>
);

const Tabs = ({ children, defaultValue, onValueChange, className = "" }) => {
  const [activeTab, setActiveTab] = useState(defaultValue);

  const handleTabChange = (value) => {
    setActiveTab(value);
    onValueChange?.(value);
  };

  return (
    <div className={className}>
      {React.Children.map(children, child => 
        React.cloneElement(child, { activeTab, onTabChange: handleTabChange })
      )}
    </div>
  );
};

// Componente MetaCard - Estilo Executivo com Gradientes
const MetaCard = ({ titulo, realizado, meta, formato = "numero", icon: Icon, color = "blue" }) => {
  const percentual = meta > 0 ? (realizado / meta * 100) : 0
  const status = percentual >= 100 ? 'success' : percentual >= 80 ? 'warning' : 'danger'
  
  const formatValue = (value) => {
    if (formato === "moeda") {
      return typeof value === 'string' ? value : `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
    }
    if (formato === "percentual") {
      return `${value.toFixed(1)}%`
    }
    return typeof value === 'number' ? value.toLocaleString('pt-BR') : value
  }

  const gradients = {
    blue: "bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900",
    green: "bg-gradient-to-br from-emerald-600 via-emerald-700 to-emerald-800",
    purple: "bg-gradient-to-br from-purple-600 via-purple-700 to-purple-800",
    orange: "bg-gradient-to-br from-amber-600 via-orange-700 to-orange-800"
  }

  const iconColors = {
    blue: "text-blue-400 bg-blue-500/20",
    green: "text-emerald-400 bg-emerald-500/20",
    purple: "text-purple-400 bg-purple-500/20",
    orange: "text-orange-400 bg-orange-500/20"
  }

  const textColors = {
    blue: "text-slate-300",
    green: "text-emerald-200",
    purple: "text-purple-200",
    orange: "text-orange-200"
  }

  const progressColors = {
    blue: "from-blue-400 to-cyan-400",
    green: "from-emerald-300 to-green-300",
    purple: "from-purple-300 to-pink-300",
    orange: "from-orange-300 to-yellow-300"
  }

  return (
    <div className={`${gradients[color]} text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`${textColors[color]} text-sm font-medium tracking-wide uppercase`}>{titulo}</p>
          <p className={`text-4xl font-bold bg-gradient-to-r ${progressColors[color]} bg-clip-text text-transparent mt-2`}>
            {formatValue(realizado)}
          </p>
          <p className={`${textColors[color]} text-sm mt-2`}>
            Meta: {formatValue(meta)} • {percentual >= 100 ? `✅ Atingida (${percentual.toFixed(1)}%)` : `${(100 - percentual).toFixed(1)}% restante`}
          </p>
        </div>
        {Icon && (
          <div className={`${iconColors[color]} p-4 rounded-xl`}>
            <Icon className="w-8 h-8" />
          </div>
        )}
      </div>
      <div className="mt-4">
        <div className="w-full bg-white/20 rounded-full h-3">
          <div 
            className={`bg-gradient-to-r ${progressColors[color]} h-3 rounded-full transition-all duration-500`}
            style={{ width: `${Math.min(100, Math.max(0, percentual))}%` }}
          />
        </div>
      </div>
    </div>
  )
}

// Componente TabelaDesempenhoCampanhas
const TabelaDesempenhoCampanhas = ({ fase, cidade }) => {
  const [campanhas, setCampanhas] = useState([])
  const [loading, setLoading] = useState(true)
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchCampanhas()
  }, [fase, cidade])

  const fetchCampanhas = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (fase && fase !== 'todas') params.append('fase', fase)
      if (cidade && cidade !== 'todos') params.append('cidade', cidade)
      
      const response = await fetch(`${API_URL}/api/metrics/tabela-desempenho-campanhas?${params}`)
      const data = await response.json()
      setCampanhas(data.campanhas || [])
    } catch (error) {
      console.error('Erro ao buscar campanhas:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-4">Carregando campanhas...</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Campanha
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Fase/Cidade
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Meta vs Realizado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Atingimento
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Orçamento
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          {campanhas.map((campanha) => (
            <tr key={campanha.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
              <td className="px-6 py-4 whitespace-nowrap">
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {campanha.nome}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {campanha.tipo_campanha}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900 dark:text-white">{campanha.fase}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{campanha.cidade}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900 dark:text-white">
                  {campanha.realizado} / {campanha.meta_quantidade}
                </div>
                <Progress value={Math.min((campanha.realizado / campanha.meta_quantidade) * 100, 100)} className="h-1 mt-1" />
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                  campanha.atingimento_percentual >= 100 ? 'bg-green-100 text-green-800' :
                  campanha.atingimento_percentual >= 80 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {campanha.atingimento_percentual}%
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900 dark:text-white">
                  R$ {campanha.custo_real.toFixed(2)}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  / R$ {campanha.orcamento_previsto.toFixed(2)}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                  campanha.status === 'ativa' ? 'bg-blue-100 text-blue-800' :
                  campanha.status === 'finalizada' ? 'bg-gray-100 text-gray-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {campanha.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {campanhas.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          Nenhuma campanha encontrada
        </div>
      )}
    </div>
  )
}

// Componente principal MetasPerformance
export function MetasPerformance() {
  const [activeTab, setActiveTab] = useState('overview')
  const [cidadeSelecionada, setCidadeSelecionada] = useState('todos')
  const [faseSelecionada, setFaseSelecionada] = useState('todas')
  const [metasAgregadas, setMetasAgregadas] = useState({})
  const [penetracaoMercado, setPenetracaoMercado] = useState({})
  const [loading, setLoading] = useState(true)
  
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchMetasAgregadas()
  }, [faseSelecionada])

  useEffect(() => {
    if (cidadeSelecionada !== 'todos') {
      fetchPenetracaoMercado()
    }
  }, [cidadeSelecionada])

  const fetchMetasAgregadas = async () => {
    try {
      setLoading(true)
      const params = faseSelecionada !== 'todas' ? `?fase=${faseSelecionada}` : ''
      const response = await fetch(`${API_URL}/api/metrics/overview-metas-agregadas${params}`)
      const data = await response.json()
      setMetasAgregadas(data)
    } catch (error) {
      console.error('Erro ao buscar metas agregadas:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPenetracaoMercado = async () => {
    try {
      const response = await fetch(`${API_URL}/api/metrics/penetracao-mercado/${cidadeSelecionada}`)
      const data = await response.json()
      setPenetracaoMercado(data)
    } catch (error) {
      console.error('Erro ao buscar penetração de mercado:', error)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-2">
          <Target className="w-6 h-6 text-gray-400" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Metas & Performance</h2>
        </div>
        <div className="text-center py-8">Carregando...</div>
      </div>
    )
  }

  const tabs = [
    {
      label: 'Visão Geral',
      content: (
        <div className="space-y-8">
          {/* KPI Cards - Estilo Executivo */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <MetaCard 
              titulo="Motoristas Adquiridos"
              realizado={metasAgregadas.motoristas_realizados || 0}
              meta={metasAgregadas.motoristas_meta || 30}
              formato="numero"
              icon={Users}
              color="blue"
            />
            <MetaCard 
              titulo="Corridas de Lançamento"
              realizado={metasAgregadas.corridas_realizadas || 0}
              meta={metasAgregadas.corridas_meta || 250}
              formato="numero"
              icon={Activity}
              color="green"
            />
            <MetaCard 
              titulo="CAC - Motorista"
              realizado={metasAgregadas.cac_motorista || 0}
              meta={150}
              formato="moeda"
              icon={DollarSign}
              color="purple"
            />
            <MetaCard 
              titulo="CAC - Corrida"
              realizado={metasAgregadas.cac_corrida || 0}
              meta={25}
              formato="moeda"
              icon={Award}
              color="orange"
            />
          </motion.div>

          {/* Resumo Financeiro - Estilo Executivo */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-emerald-50 to-green-100 border border-emerald-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-emerald-600 rounded-xl">
                <DollarSign className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-emerald-800">
                Resumo Financeiro Corporativo
              </h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-emerald-200 p-6 text-center">
                <div className="text-3xl font-bold text-emerald-600 mb-2">
                  R$ {(metasAgregadas.orcamento_previsto || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </div>
                <div className="text-sm text-emerald-700 font-medium">Orçamento Aprovado</div>
                <div className="text-xs text-emerald-600 mt-1">Investimento total planejado</div>
              </div>
              
              <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-emerald-200 p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  R$ {(metasAgregadas.custo_real || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </div>
                <div className="text-sm text-blue-700 font-medium">Investimento Realizado</div>
                <div className="text-xs text-blue-600 mt-1">Capital já investido</div>
              </div>
              
              <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-emerald-200 p-6 text-center">
                <div className={`text-3xl font-bold mb-2 ${
                  (metasAgregadas.custo_real || 0) <= (metasAgregadas.orcamento_previsto || 0) ? 'text-green-600' : 'text-red-600'
                }`}>
                  R$ {((metasAgregadas.orcamento_previsto || 0) - (metasAgregadas.custo_real || 0)).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </div>
                <div className={`text-sm font-medium ${
                  (metasAgregadas.custo_real || 0) <= (metasAgregadas.orcamento_previsto || 0) ? 'text-green-700' : 'text-red-700'
                }`}>
                  {(metasAgregadas.custo_real || 0) <= (metasAgregadas.orcamento_previsto || 0) ? 'Economia Gerada' : 'Sobrecusto'}
                </div>
                <div className={`text-xs mt-1 ${
                  (metasAgregadas.custo_real || 0) <= (metasAgregadas.orcamento_previsto || 0) ? 'text-green-600' : 'text-red-600'
                }`}>
                  {(metasAgregadas.custo_real || 0) <= (metasAgregadas.orcamento_previsto || 0) ? 'Otimização orçamentária' : 'Excesso de investimento'}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )
    },
    {
      label: 'Campanhas',
      content: (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-600 rounded-xl">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-blue-800">
              Desempenho Detalhado de Campanhas
            </h3>
          </div>
          
          <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-blue-200 p-6">
            <TabelaDesempenhoCampanhas 
              fase={faseSelecionada}
              cidade={cidadeSelecionada}
            />
          </div>
        </motion.div>
      )
    },
    {
      label: 'Penetração',
      content: (
        cidadeSelecionada !== 'todos' && penetracaoMercado.cidade ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-purple-50 to-pink-100 border border-purple-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-600 rounded-xl">
                <Users className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-purple-800">
                Penetração de Mercado - {penetracaoMercado.cidade}
              </h3>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-purple-200 p-6">
                <h4 className="font-semibold text-purple-800 mb-4 flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Análise Demográfica
                </h4>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm text-purple-700">População Estimada:</span>
                    <span className="font-semibold text-purple-800">{penetracaoMercado.populacao_estimada?.toLocaleString('pt-BR')}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm text-purple-700">Público-Alvo (15-44 anos):</span>
                    <span className="font-semibold text-purple-800">{penetracaoMercado.publico_alvo?.toLocaleString('pt-BR')}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm text-purple-700">Corridas Realizadas:</span>
                    <span className="font-semibold text-green-600">{penetracaoMercado.corridas_realizadas}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg border-2 border-purple-300">
                    <span className="text-sm font-medium text-purple-800">Penetração Atual:</span>
                    <span className="font-bold text-lg text-purple-600">{penetracaoMercado.penetracao_atual}%</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-purple-200 p-6">
                <h4 className="font-semibold text-purple-800 mb-4 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Evolução Temporal
                </h4>
                <div className="space-y-3">
                  {penetracaoMercado.evolucao_mensal?.map((mes, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
                      <span className="text-sm font-medium text-purple-700">{mes.mes}</span>
                      <div className="flex items-center space-x-3">
                        <span className="text-sm text-purple-600">{mes.realizado}/{mes.meta}</span>
                        <div className="flex items-center">
                          <div className="w-16 bg-purple-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${Math.min((mes.realizado / mes.meta) * 100, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-purple-800">{((mes.realizado / mes.meta) * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <div className="bg-gradient-to-br from-gray-50 to-slate-100 border border-slate-200 rounded-2xl p-8 text-center">
            <div className="p-4 bg-slate-600 rounded-xl inline-block mb-4">
              <MapPin className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              Selecione uma Cidade
            </h3>
            <p className="text-slate-500">
              Para visualizar a análise de penetração de mercado, selecione uma cidade específica no filtro acima.
            </p>
          </div>
        )
      )
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      {/* Header Executivo com Gradiente */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-8 mb-8 shadow-2xl"
      >
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Metas & Performance
              </h1>
              <p className="text-blue-100 text-lg opacity-90">
                Acompanhe o desempenho das campanhas e métricas de crescimento
              </p>
            </div>
            <div className="hidden md:flex items-center space-x-4">
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4">
                <Target className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>
        </div>
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full opacity-20 -translate-y-32 translate-x-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-blue-400 to-cyan-400 rounded-full opacity-20 translate-y-24 -translate-x-24"></div>
      </motion.div>

      {/* Panel de Filtros Executivo */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-2xl shadow-xl border border-slate-200 p-6 mb-8"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="p-2 bg-slate-600 rounded-xl">
            <Filter className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-slate-800">Filtros de Análise</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Fase da Campanha
            </label>
            <Select 
              value={faseSelecionada} 
              onValueChange={setFaseSelecionada} 
              className="w-full"
            >
              <SelectOption value="todas">Todas as Fases</SelectOption>
              <SelectOption value="Fase 1">Fase 1 - Lançamento</SelectOption>
              <SelectOption value="Fase 2">Fase 2 - Crescimento</SelectOption>
              <SelectOption value="Fase 3">Fase 3 - Expansão</SelectOption>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Cidade de Foco
            </label>
            <Select 
              value={cidadeSelecionada} 
              onValueChange={setCidadeSelecionada} 
              className="w-full"
            >
              <SelectOption value="todos">Todas as Cidades</SelectOption>
              <SelectOption value="GUARANTA DO NORTE">Guaranta do Norte</SelectOption>
              <SelectOption value="MATUPA">Matupá</SelectOption>
              <SelectOption value="PEIXOTO">Peixoto</SelectOption>
            </Select>
          </div>
        </div>
      </motion.div>

      {/* Tabs com estilo executivo */}
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
          <div className="flex space-x-1">
            {tabs.map((tab, index) => (
              <button
                key={index}
                onClick={() => setActiveTab(index === 0 ? 'overview' : index === 1 ? 'campanhas' : 'penetracao')}
                className={`px-6 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                  (index === 0 && activeTab === 'overview') ||
                  (index === 1 && activeTab === 'campanhas') ||
                  (index === 2 && activeTab === 'penetracao')
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
        
        <div className="p-6">
          {activeTab === 'overview' && tabs[0].content}
          {activeTab === 'campanhas' && tabs[1].content}
          {activeTab === 'penetracao' && tabs[2].content}
        </div>
      </div>
    </div>
  )
}

// Componente original MetasCidades mantido
export function MetasCidades() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchMetasCidades()
  }, [])

  const fetchMetasCidades = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/metrics/metas-cidades`)
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Erro ao buscar metas por cidade:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'danger':
        return <AlertTriangle className="w-5 h-5 text-red-500" />
      default:
        return <Target className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20'
      case 'warning':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
      case 'danger':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20'
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20'
    }
  }

  const getProgressColor = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-500'
      case 'warning':
        return 'bg-yellow-500'
      case 'danger':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-2">
          <Target className="w-6 h-6 text-gray-400" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Metas por Cidade</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-10">
      {/* Cadastro e listagem de campanhas */}
      <CampanhasFormList />

      {/* Nova aba de Metas & Performance */}
      <MetasPerformance />

      {/* Cards de metas por cidade - versão simplificada */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-2">
          <Target className="w-6 h-6 text-gray-700 dark:text-gray-300" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Resumo por Cidade</h2>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Meta Atingida</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span>Próximo da Meta</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Abaixo da Meta</span>
          </div>
        </div>
      </motion.div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.map((cidade, index) => (
          <motion.div
            key={cidade.cidade}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <Card className="relative overflow-hidden hover:shadow-lg transition-all duration-300">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                    {cidade.cidade}
                  </CardTitle>
                  <div className={`p-2 rounded-lg ${getStatusColor(cidade.status)}`}>
                    {getStatusIcon(cidade.status)}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Progress Section */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Progresso</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {cidade.percentual.toFixed(1)}%
                    </span>
                  </div>
                  
                  <div className="relative">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(cidade.percentual, 100)}%` }}
                        transition={{ delay: index * 0.1 + 0.5, duration: 1 }}
                        className={`h-3 rounded-full ${getProgressColor(cidade.status)}`}
                      />
                    </div>
                    {cidade.percentual > 100 && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: index * 0.1 + 1 }}
                        className="absolute right-0 top-0 transform translate-x-2 -translate-y-1"
                      >
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      </motion.div>
                    )}
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {cidade.realizado}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Realizado
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {cidade.meta}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Meta
                    </div>
                  </div>
                </div>

                {/* Status Message */}
                <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                  <div className={`text-xs font-medium ${
                    cidade.status === 'success' ? 'text-green-600' :
                    cidade.status === 'warning' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {cidade.status === 'success' && '🎉 Meta atingida!'}
                    {cidade.status === 'warning' && '⚠️ Próximo da meta'}
                    {cidade.status === 'danger' && '🚨 Abaixo da meta'}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {cidade.status === 'success' && `Superou em ${(cidade.percentual - 100).toFixed(1)}%`}
                    {cidade.status === 'warning' && `Faltam ${cidade.meta - cidade.realizado} corridas`}
                    {cidade.status === 'danger' && `Faltam ${cidade.meta - cidade.realizado} corridas`}
                  </div>
                </div>
              </CardContent>

              {/* Decorative element */}
              <div className={`absolute top-0 right-0 w-16 h-16 opacity-10 ${getProgressColor(cidade.status)} rounded-full -translate-y-8 translate-x-8`} />
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Resumo Geral</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                  {data.length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Total de Cidades
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">
                  {data.filter(c => c.status === 'success').length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Metas Atingidas
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600 mb-1">
                  {data.filter(c => c.status === 'warning').length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Próximo da Meta
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600 mb-1">
                  {data.filter(c => c.status === 'danger').length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Abaixo da Meta
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
