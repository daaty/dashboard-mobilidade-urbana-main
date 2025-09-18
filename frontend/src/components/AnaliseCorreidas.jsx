
import React from "react"
import MapaCalorProblemas from "./MapaCalorProblemas"
import { motion } from "framer-motion"
import { Select, SelectOption } from '@/components/ui/select'
import { TrendingUp, CheckCircle, XCircle, AlertTriangle, Clock, BarChart3, Activity, Filter, Calendar } from 'lucide-react'
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = {
  concluidas: '#10B981',
  canceladas: '#EF4444',
  perdidas: '#F59E0B',
  primary: '#000000',
  secondary: '#6B7280',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6'
}

const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: '7 dias', value: '7d' },
  { label: '30 dias', value: '30d' },
  { label: '3 meses', value: '3m' },
  { label: '6 meses', value: '6m' },
  { label: '12 meses', value: '12m' }
]

export default function AnaliseCorreidas() {
  const [data, setData] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [cities, setCities] = React.useState([])
  const [filters, setFilters] = React.useState({
    periodo: '6m',
    cidade: '',
    diaSemana: '',
    horario: ''
  })
  
  // Estado para controlar as abas dos gráficos
  const [activeTab, setActiveTab] = React.useState('horario') // 'horario' ou 'periodo'

  const handleFilterChange = (key, value) => {
    console.log('🔄 AnaliseCorreidas - Filtro mudando:', key, 'de', filters[key], 'para', value);
    setFilters(prev => {
      const newFilters = { ...prev, [key]: value };
      console.log('📊 AnaliseCorreidas - Novos filtros:', newFilters);
      return newFilters;
    });

    // Forçar re-renderização
    setTimeout(() => {
      console.log('🔄 Forçando re-renderização do componente');
    }, 100);
  }

  // Buscar cidades reais do backend
  React.useEffect(() => {
    const fetchCities = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_URL}/api/metrics/cities`)
        if (response.ok) {
          const result = await response.json()
          if (result.success && result.cities) {
            setCities(result.cities)
          }
        }
      } catch (error) {
        console.error('Erro ao buscar cidades:', error)
      }
    }
    fetchCities()
  }, [])

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        
        // Construir parâmetros da query
        const params = new URLSearchParams({
          periodo: filters.periodo
        });
        
        // Adicionar filtro de cidade se selecionado
        if (filters.cidade) {
          params.append('cidade', filters.cidade);
        }
        
        const response = await fetch(`${API_URL}/api/metrics/overview?${params.toString()}`)
        if (response.ok) {
          const result = await response.json()
          setData(result)
        } else {
          setData(null)
        }
      } catch (error) {
        setData(null)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [filters.periodo, filters.cidade])



  const formatNumber = (num) => {
    return new Intl.NumberFormat('pt-BR').format(num)
  }

  const formatPercentage = (num) => {
    return `${num.toFixed(1)}%`
  }

  const calculateMetrics = () => {
    if (!data?.metricas_principais) return null
    const { corridas_concluidas, corridas_canceladas, corridas_perdidas } = data.metricas_principais
    const total = corridas_concluidas + corridas_canceladas + corridas_perdidas
    return {
      total_corridas: total,
      taxa_conclusao: total > 0 ? (corridas_concluidas / total) * 100 : 0,
      taxa_cancelamento: total > 0 ? (corridas_canceladas / total) * 100 : 0,
      taxa_perda: total > 0 ? (corridas_perdidas / total) * 100 : 0,
      corridas_concluidas,
      corridas_canceladas,
      corridas_perdidas
    }
  }

  const metrics = calculateMetrics()
  const chartData = metrics ? [
    { name: 'Concluídas', value: metrics.corridas_concluidas, color: COLORS.concluidas },
    { name: 'Canceladas', value: metrics.corridas_canceladas, color: COLORS.canceladas },
    { name: 'Perdidas', value: metrics.corridas_perdidas, color: COLORS.perdidas }
  ] : []

  // Dados reais para gráficos
  const statusData = data?.distribuicao_status || []
  
  // Debug para ver os nomes dos status
  React.useEffect(() => {
    console.log('Status data:', statusData.map(item => ({ status: item.status, quantidade: item.quantidade })));
  }, [statusData]);
  
  // Criar dados de evolução temporal baseados nos dados disponíveis
  const evolucaoData = React.useMemo(() => {
    if (!data?.comparativo_horarios || data.comparativo_horarios.length === 0) {
      return []
    }
    
    // Converter dados por hora em dados de evolução temporal
    return data.comparativo_horarios.map(item => ({
      data: `${item.hora}:00`,
      taxa_conclusao: item.taxa_conclusao || 0,
      taxa_cancelamento: item.taxa_cancelamento || 0,
      taxa_perda: item.taxa_perda || 0
    }))
  }, [data?.comparativo_horarios])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">Erro ao carregar dados de análise</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Análise de Corridas
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Entenda a saúde e a eficiência da operação. Onde estamos performando bem e onde estão os gargalos?
          </p>
        </motion.div>

        {/* Filtros */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Filter className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Filtros de Análise</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Período</label>
              <Select
                value={filters.periodo}
                onChange={(value) => handleFilterChange('periodo', value)}
                className="w-full bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
              >
                <SelectOption value="">Selecione o período</SelectOption>
                {periodOptions.map(option => (
                  <SelectOption key={option.value} value={option.value}>
                    {option.label}
                  </SelectOption>
                ))}
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Cidade/Região</label>
              <Select
                value={filters.cidade}
                onChange={(value) => handleFilterChange('cidade', value)}
                className="w-full bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
              >
                <SelectOption value="">Todas as cidades</SelectOption>
                {cities.map(city => (
                  <SelectOption key={city} value={city}>
                    {city}
                  </SelectOption>
                ))}
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Dia da Semana</label>
              <Select
                value={filters.diaSemana}
                onChange={(value) => handleFilterChange('diaSemana', value)}
                className="w-full bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
              >
                <SelectOption value="">Todos os dias</SelectOption>
                <SelectOption value="seg">Segunda-feira</SelectOption>
                <SelectOption value="ter">Terça-feira</SelectOption>
                <SelectOption value="qua">Quarta-feira</SelectOption>
                <SelectOption value="qui">Quinta-feira</SelectOption>
                <SelectOption value="sex">Sexta-feira</SelectOption>
                <SelectOption value="sab">Sábado</SelectOption>
                <SelectOption value="dom">Domingo</SelectOption>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Horário</label>
              <Select
                value={filters.horario}
                onChange={(value) => handleFilterChange('horario', value)}
                className="w-full bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
              >
                <SelectOption value="">Todos os horários</SelectOption>
                <SelectOption value="manha">Manhã (6h-12h)</SelectOption>
                <SelectOption value="tarde">Tarde (12h-18h)</SelectOption>
                <SelectOption value="noite">Noite (18h-24h)</SelectOption>
                <SelectOption value="madrugada">Madrugada (0h-6h)</SelectOption>
              </Select>
            </div>
          </div>
        </motion.div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total de Corridas */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium uppercase tracking-wide">Total de Corridas</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {metrics ? formatNumber(metrics.total_corridas) : '0'}
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Volume total da demanda</p>
              </div>
              <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded-lg">
                <Activity className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </motion.div>

          {/* Taxa de Conclusão */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium uppercase tracking-wide">Taxa de Conclusão</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                  {metrics ? formatPercentage(metrics.taxa_conclusao) : '0%'}
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Eficiência geral da operação</p>
              </div>
              <div className="bg-green-100 dark:bg-green-900 p-3 rounded-lg">
                <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </motion.div>

          {/* Taxa de Cancelamento */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium uppercase tracking-wide">Taxa de Cancelamento</p>
                <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
                  {metrics ? formatPercentage(metrics.taxa_cancelamento) : '0%'}
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Corridas canceladas</p>
              </div>
              <div className="bg-red-100 dark:bg-red-900 p-3 rounded-lg">
                <XCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </motion.div>

          {/* Taxa de Perda */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm font-medium uppercase tracking-wide">Taxa de Perda</p>
                <p className="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-2">
                  {metrics ? formatPercentage(metrics.taxa_perda) : '0%'}
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Sem aceite de motorista</p>
              </div>
              <div className="bg-orange-100 dark:bg-orange-900 p-3 rounded-lg">
                <AlertTriangle className="w-8 h-8 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Sistema de Abas para Gráficos */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          {/* Abas */}
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('horario')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-all duration-200 ${
                activeTab === 'horario'
                  ? 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 border-b-2 border-blue-600'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <Clock className="w-4 h-4" />
                Por Horário
              </div>
            </button>
            <button
              onClick={() => setActiveTab('periodo')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-all duration-200 ${
                activeTab === 'periodo'
                  ? 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 border-b-2 border-blue-600'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <Calendar className="w-4 h-4" />
                Por Data/Período
              </div>
            </button>
          </div>

          {/* Conteúdo das Abas */}
          <div className="p-6">
            {activeTab === 'horario' && (
              <div className="space-y-6">
                {/* Gráfico de Performance por Horário */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        Evolução das Taxas de Performance por Horário
                      </h3>
                    </div>
                    <div className="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900 px-3 py-1 rounded-lg">
                      Performance ao longo do dia
                    </div>
                  </div>
                  <div className="h-64 sm:h-80 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 sm:p-4">
                    {evolucaoData && evolucaoData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart 
                          data={evolucaoData} 
                          margin={{ 
                            top: 10, 
                            right: window.innerWidth < 640 ? 5 : 30, 
                            left: window.innerWidth < 640 ? 5 : 20, 
                            bottom: window.innerWidth < 640 ? 30 : 5 
                          }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis 
                            dataKey="data" 
                            tick={{ fontSize: window.innerWidth < 640 ? 10 : 12, fill: '#666' }}
                            label={window.innerWidth >= 640 ? { value: 'Horário', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle' } } : undefined}
                            interval={window.innerWidth < 640 ? 'preserveStartEnd' : 0}
                          />
                          <YAxis 
                            tick={{ fontSize: window.innerWidth < 640 ? 10 : 12, fill: '#666' }}
                            label={window.innerWidth >= 640 ? { value: 'Taxa (%)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } } : undefined}
                            domain={[0, 100]}
                            width={window.innerWidth < 640 ? 30 : 50}
                          />
                          <Tooltip 
                            formatter={(value, name) => [`${value.toFixed(1)}%`, name]}
                            labelFormatter={(hora) => `Horário: ${hora}`}
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                              fontSize: window.innerWidth < 640 ? '11px' : '13px',
                              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                              maxWidth: window.innerWidth < 640 ? '200px' : '300px'
                            }}
                          />
                          {window.innerWidth >= 640 && (
                            <Legend 
                              verticalAlign="top" 
                              height={36}
                              iconType="line"
                              wrapperStyle={{ fontSize: '12px' }}
                            />
                          )}
                          <Line 
                            type="monotone" 
                            dataKey="taxa_conclusao" 
                            stroke={COLORS.concluidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Taxa de Conclusão"
                            dot={{ fill: COLORS.concluidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.concluidas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="taxa_cancelamento" 
                            stroke={COLORS.canceladas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Taxa de Cancelamento"
                            dot={{ fill: COLORS.canceladas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.canceladas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="taxa_perda" 
                            stroke={COLORS.perdidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Taxa de Perda"
                            dot={{ fill: COLORS.perdidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.perdidas, strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="text-gray-600 dark:text-gray-400 text-lg font-medium">Sem dados de performance</div>
                          <div className="text-gray-500 dark:text-gray-500 text-sm mt-1">Nenhum dado encontrado no período selecionado</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Gráfico de Demanda por Horário */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                        <Clock className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        Distribuição de Demanda por Horário
                      </h3>
                    </div>
                    {data?.tempos_operacionais && (
                      <div className="flex gap-4 text-xs">
                        {data.tempos_operacionais.tempo_medio_espera && (
                          <div className="bg-orange-100 dark:bg-orange-900 px-3 py-1 rounded-lg">
                            <span className="text-orange-700 dark:text-orange-300">Espera: </span>
                            <span className="font-semibold text-gray-900 dark:text-white">{data.tempos_operacionais.tempo_medio_espera}min</span>
                          </div>
                        )}
                        {data.tempos_operacionais.tempo_medio_chegada && (
                          <div className="bg-orange-100 dark:bg-orange-900 px-3 py-1 rounded-lg">
                            <span className="text-orange-700 dark:text-orange-300">Chegada: </span>
                            <span className="font-semibold text-gray-900 dark:text-white">{data.tempos_operacionais.tempo_medio_chegada}min</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="h-64 sm:h-80 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 sm:p-4">
                    {data?.comparativo_horarios && data.comparativo_horarios.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart 
                          data={data.comparativo_horarios}
                          margin={{ 
                            top: 10, 
                            right: window.innerWidth < 640 ? 5 : 30, 
                            left: window.innerWidth < 640 ? 5 : 20, 
                            bottom: window.innerWidth < 640 ? 30 : 5 
                          }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis 
                            dataKey="hora" 
                            tick={{ fontSize: window.innerWidth < 640 ? 10 : 12, fill: '#666' }}
                            label={window.innerWidth >= 640 ? { value: 'Horário (24h)', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle' } } : undefined}
                            interval={window.innerWidth < 640 ? 2 : 0}
                          />
                          <YAxis 
                            tick={{ fontSize: window.innerWidth < 640 ? 10 : 12, fill: '#666' }}
                            label={window.innerWidth >= 640 ? { value: 'Volume de Corridas', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } } : undefined}
                            width={window.innerWidth < 640 ? 35 : 50}
                          />
                          <Tooltip 
                            formatter={(value, name) => [value, name]}
                            labelFormatter={(hora) => `${hora}:00`}
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                              fontSize: window.innerWidth < 640 ? '11px' : '13px',
                              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                              maxWidth: window.innerWidth < 640 ? '220px' : '300px'
                            }}
                          />
                          {window.innerWidth >= 640 && (
                            <Legend 
                              verticalAlign="top" 
                              height={36}
                              iconType="line"
                              wrapperStyle={{ fontSize: '12px' }}
                            />
                          )}
                          <Line 
                            type="monotone" 
                            dataKey="concluidas" 
                            stroke={COLORS.concluidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Concluídas"
                            dot={{ fill: COLORS.concluidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.concluidas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="canceladas" 
                            stroke={COLORS.canceladas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Canceladas"
                            dot={{ fill: COLORS.canceladas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.canceladas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="perdidas" 
                            stroke={COLORS.perdidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Perdidas"
                            dot={{ fill: COLORS.perdidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.perdidas, strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="text-gray-600 dark:text-gray-400 text-lg font-medium">Sem dados de demanda</div>
                          <div className="text-gray-500 dark:text-gray-500 text-sm mt-1">Nenhum dado encontrado no período selecionado</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'periodo' && (
              <div className="space-y-6">
                {/* Gráfico de Performance por Período */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        Evolução das Taxas de Performance por {filters.periodo === 'hoje' ? 'Horário' : 'Dia'}
                      </h3>
                    </div>
                    <div className="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900 px-3 py-1 rounded-lg">
                      {filters.periodo === 'hoje' ? 'Performance por hora' : 'Performance diária'}
                    </div>
                  </div>
                  <div className="h-64 sm:h-80 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 sm:p-4">
                    {data?.evolucao && data.evolucao.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart 
                          data={data.evolucao} 
                          margin={{ 
                            top: 10, 
                            right: window.innerWidth < 640 ? 5 : 30, 
                            left: window.innerWidth < 640 ? 5 : 20, 
                            bottom: window.innerWidth < 640 ? 30 : 5 
                          }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis 
                            dataKey="data" 
                            tick={false}
                            label={window.innerWidth >= 640 ? { 
                              value: filters.periodo === 'hoje' ? 'Horário' : 'Data', 
                              position: 'insideBottom', offset: -5, style: { textAnchor: 'middle' } 
                            } : undefined}
                            interval={window.innerWidth < 640 ? 'preserveStartEnd' : 0}
                          />
                          <YAxis 
                            tick={{ fontSize: window.innerWidth < 640 ? 10 : 12, fill: '#666' }}
                            label={window.innerWidth >= 640 ? { value: 'Taxa (%)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } } : undefined}
                            domain={[0, 100]}
                            width={window.innerWidth < 640 ? 30 : 50}
                          />
                          <Tooltip 
                            formatter={(value, name) => [`${value.toFixed(1)}%`, name]}
                            labelFormatter={(data) => {
                              if (filters.periodo === 'hoje') {
                                return `Horário: ${data}`;
                              } else {
                                const date = new Date(data);
                                return `Data: ${date.toLocaleDateString('pt-BR')}`;
                              }
                            }}
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                              fontSize: window.innerWidth < 640 ? '11px' : '13px',
                              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                              maxWidth: window.innerWidth < 640 ? '200px' : '300px'
                            }}
                          />
                          {window.innerWidth >= 640 && (
                            <Legend 
                              verticalAlign="top" 
                              height={36}
                              iconType="line"
                              wrapperStyle={{ fontSize: '12px' }}
                            />
                          )}
                          <Line 
                            type="monotone" 
                            dataKey="taxa_conclusao" 
                            stroke={COLORS.concluidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Taxa de Conclusão"
                            dot={{ fill: COLORS.concluidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.concluidas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="taxa_cancelamento" 
                            stroke={COLORS.canceladas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Taxa de Cancelamento"
                            dot={{ fill: COLORS.canceladas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.canceladas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="taxa_perda" 
                            stroke={COLORS.perdidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Taxa de Perda"
                            dot={{ fill: COLORS.perdidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.perdidas, strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="text-gray-600 dark:text-gray-400 text-lg font-medium">Sem dados de performance</div>
                          <div className="text-gray-500 dark:text-gray-500 text-sm mt-1">Nenhum dado encontrado no período selecionado</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Gráfico de Demanda por Período */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                        <Calendar className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        Distribuição de Demanda por {filters.periodo === 'hoje' ? 'Horário' : 'Dia'}
                      </h3>
                    </div>
                    <div className="text-xs text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900 px-3 py-1 rounded-lg">
                      Total: {data?.evolucao ? data.evolucao.reduce((sum, item) => sum + item.concluidas + item.canceladas + item.perdidas, 0) : 0} corridas
                    </div>
                  </div>
                  <div className="h-64 sm:h-80 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 sm:p-4">
                    {data?.evolucao && data.evolucao.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart 
                          data={data.evolucao}
                          margin={{ 
                            top: 10, 
                            right: window.innerWidth < 640 ? 5 : 30, 
                            left: window.innerWidth < 640 ? 5 : 20, 
                            bottom: window.innerWidth < 640 ? 30 : 5 
                          }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis 
                            dataKey="data" 
                            tick={false}
                            label={window.innerWidth >= 640 ? { 
                              value: filters.periodo === 'hoje' ? 'Horário' : 'Data', 
                              position: 'insideBottom', offset: -5, style: { textAnchor: 'middle' } 
                            } : undefined}
                            interval={window.innerWidth < 640 ? 'preserveStartEnd' : 0}
                          />
                          <YAxis 
                            tick={{ fontSize: window.innerWidth < 640 ? 10 : 12, fill: '#666' }}
                            label={window.innerWidth >= 640 ? { value: 'Volume de Corridas', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } } : undefined}
                            width={window.innerWidth < 640 ? 35 : 50}
                          />
                          <Tooltip 
                            formatter={(value, name) => [value, name]}
                            labelFormatter={(data) => {
                              if (filters.periodo === 'hoje') {
                                return `Horário: ${data}`;
                              } else {
                                const date = new Date(data);
                                return `Data: ${date.toLocaleDateString('pt-BR')}`;
                              }
                            }}
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                              fontSize: window.innerWidth < 640 ? '11px' : '13px',
                              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                              maxWidth: window.innerWidth < 640 ? '220px' : '300px'
                            }}
                          />
                          {window.innerWidth >= 640 && (
                            <Legend 
                              verticalAlign="top" 
                              height={36}
                              iconType="line"
                              wrapperStyle={{ fontSize: '12px' }}
                            />
                          )}
                          <Line 
                            type="monotone" 
                            dataKey="concluidas" 
                            stroke={COLORS.concluidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Concluídas"
                            dot={{ fill: COLORS.concluidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.concluidas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="canceladas" 
                            stroke={COLORS.canceladas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Canceladas"
                            dot={{ fill: COLORS.canceladas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.canceladas, strokeWidth: 2 }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="perdidas" 
                            stroke={COLORS.perdidas} 
                            strokeWidth={window.innerWidth < 640 ? 2 : 3}
                            name="Perdidas"
                            dot={{ fill: COLORS.perdidas, strokeWidth: 2, r: window.innerWidth < 640 ? 3 : 4 }}
                            activeDot={{ r: window.innerWidth < 640 ? 5 : 6, stroke: COLORS.perdidas, strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="text-gray-600 dark:text-gray-400 text-lg font-medium">Sem dados de demanda</div>
                          <div className="text-gray-500 dark:text-gray-500 text-sm mt-1">Nenhum dado encontrado no período selecionado</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Cards de Estatísticas Rápidas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Gráfico de Pizza - Distribuição de Status */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[320px] sm:h-96">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-600 rounded-xl">
                <BarChart3 className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-200">
                Distribuição por Status das Corridas
              </h3>
            </div>
            <div className="h-64 sm:h-80 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 sm:p-4">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="quantidade"
                    nameKey="status"
                    cx="50%"
                    cy="50%"
                    outerRadius={window.innerWidth < 640 ? 60 : 80}
                    label={window.innerWidth >= 640 ? ({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%` : false}
                    labelLine={false}
                  >
                    {statusData.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={
                        entry.status === 'Concluídas' ? COLORS.concluidas :
                        entry.status === 'Canceladas' ? COLORS.canceladas :
                        entry.status === 'Perdidas' ? COLORS.perdidas :
                        Object.values(COLORS)[idx % Object.values(COLORS).length]
                      } />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name) => [`${value} corridas`, name]} 
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Análise de Cancelamentos */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 min-h-[320px]"
          >
            <div className="flex items-center gap-3 mb-4 sm:mb-6">
              <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                <XCircle className="w-4 h-4 sm:w-5 sm:h-5 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-base sm:text-xl font-bold text-gray-900 dark:text-white">
                Análise de Causa Raiz - Cancelamentos
              </h3>
            </div>
            <div className="h-64 sm:h-80 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 sm:p-4">
              {data?.motivos_cancelamento && data.motivos_cancelamento.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.motivos_cancelamento}
                      cx="50%"
                      cy="50%"
                      outerRadius={window.innerWidth < 640 ? 70 : 100}
                      fill="#8884d8"
                      dataKey="quantidade"
                      nameKey="motivo"
                      label={window.innerWidth >= 640 ? true : false}
                    >
                      {data.motivos_cancelamento.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={`hsl(${index * 360 / data.motivos_cancelamento.length}, 70%, 50%)`} 
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name) => [`${value} cancelamentos`, name]}
                      labelFormatter={(motivo) => `Motivo: ${motivo}`}
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: window.innerWidth < 640 ? '11px' : '14px',
                        maxWidth: window.innerWidth < 640 ? '200px' : '300px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="text-gray-600 dark:text-gray-400 text-lg font-medium">Sem dados de cancelamentos</div>
                    <div className="text-gray-500 dark:text-gray-500 text-sm mt-1">Nenhum cancelamento encontrado no período</div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Números Detalhados */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Corridas Concluídas */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                Corridas Concluídas
              </h3>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-green-600 dark:text-green-400 mb-2">
                {metrics ? formatNumber(metrics.corridas_concluidas) : '0'}
              </p>
              <p className="text-gray-600 dark:text-gray-400 font-medium mb-4">
                {metrics ? formatPercentage(metrics.taxa_conclusao) : '0%'} do total
              </p>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-3 border border-gray-200 dark:border-gray-600">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Meta ideal: &gt; 85%
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 font-medium">
                  {metrics && metrics.taxa_conclusao >= 85 ? '✓ Meta atingida' : '⚠ Abaixo da meta'}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Corridas Canceladas */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                Corridas Canceladas
              </h3>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-red-600 dark:text-red-400 mb-2">
                {metrics ? formatNumber(metrics.corridas_canceladas) : '0'}
              </p>
              <p className="text-gray-600 dark:text-gray-400 font-medium mb-4">
                {metrics ? formatPercentage(metrics.taxa_cancelamento) : '0%'} do total
              </p>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-3 border border-gray-200 dark:border-gray-600">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Meta ideal: &lt; 10%
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 font-medium">
                  {metrics && metrics.taxa_cancelamento <= 10 ? '✓ Meta atingida' : '⚠ Acima da meta'}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Corridas Perdidas */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                Corridas Perdidas
              </h3>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                {metrics ? formatNumber(metrics.corridas_perdidas) : '0'}
              </p>
              <p className="text-gray-600 dark:text-gray-400 font-medium mb-4">
                {metrics ? formatPercentage(metrics.taxa_perda) : '0%'} do total
              </p>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-3 border border-gray-200 dark:border-gray-600">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Meta ideal: &lt; 5%
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 font-medium">
                  {metrics && metrics.taxa_perda <= 5 ? '✓ Meta atingida' : '⚠ Acima da meta - Falta de motoristas'}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Mapa de Calor de Problemas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <BarChart3 className="w-5 h-5 text-orange-600 dark:text-orange-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              Mapa de Calor de Problemas
            </h3>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4 border border-gray-200 dark:border-gray-600">
            <MapaCalorProblemas
              key={`mapa-${filters.periodo}-${filters.cidade}-${Date.now()}`}
              periodo={filters.periodo}
              cidade={filters.cidade}
            />
          </div>
        </motion.div>

        {/* Insights e Recomendações */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <BarChart3 className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              Insights e Recomendações Operacionais
            </h3>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4 border border-gray-200 dark:border-gray-600">
            {data ? (
              <div className="space-y-4">
                {/* Insights baseados nos dados reais */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    {/* Insight de Performance */}
                    <div className="bg-white rounded-lg p-4 border border-purple-100">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className="font-medium text-gray-800">Performance Geral</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {(() => {
                          const total = (data.metricas_principais?.corridas_concluidas || 0) + 
                                      (data.metricas_principais?.corridas_canceladas || 0) + 
                                      (data.metricas_principais?.corridas_perdidas || 0);
                          const taxa_sucesso = total > 0 ? ((data.metricas_principais?.corridas_concluidas || 0) / total * 100).toFixed(1) : 0;
                          
                          return taxa_sucesso > 70 ? 
                            `Excelente! Taxa de sucesso de ${taxa_sucesso}% está acima da média.` :
                            taxa_sucesso > 50 ?
                            `Taxa de sucesso de ${taxa_sucesso}% pode ser melhorada.` :
                            `Taxa de sucesso de ${taxa_sucesso}% necessita atenção urgente.`;
                        })()}
                      </div>
                    </div>

                    {/* Insight de Cancelamentos */}
                    <div className="bg-white rounded-lg p-4 border border-purple-100">
                      <div className="flex items-center gap-2 mb-2">
                        <XCircle className="w-4 h-4 text-red-600" />
                        <span className="font-medium text-gray-800">Principal Causa de Cancelamento</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {data.motivos_cancelamento && data.motivos_cancelamento.length > 0 ? (
                          `"${data.motivos_cancelamento[0].motivo}" representa ${data.motivos_cancelamento[0].quantidade} cancelamentos.`
                        ) : (
                          "Nenhum cancelamento registrado no período."
                        )}
                      </div>
                    </div>

                    {/* Insight de Horários */}
                    <div className="bg-white rounded-lg p-4 border border-purple-100">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-4 h-4 text-blue-600" />
                        <span className="font-medium text-gray-800">Horário de Pico</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {(() => {
                          if (!data.comparativo_horarios || data.comparativo_horarios.length === 0) {
                            return "Sem dados de horários disponíveis.";
                          }
                          
                          const horario_pico = data.comparativo_horarios.reduce((max, curr) => 
                            (curr.concluidas > max.concluidas) ? curr : max
                          );
                          
                          return `Maior atividade às ${horario_pico.hora}:00h com ${horario_pico.concluidas} corridas concluídas.`;
                        })()}
                      </div>
                    </div>

                    {/* Insight de Perdas */}
                    <div className="bg-white rounded-lg p-4 border border-purple-100">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-4 h-4 text-yellow-600" />
                        <span className="font-medium text-gray-800">Oportunidades Perdidas</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {data.motivos_perda && data.motivos_perda.length > 0 ? (
                          `${data.metricas_principais?.corridas_perdidas || 0} corridas perdidas. Principal motivo: "${data.motivos_perda[0].motivo}".`
                        ) : (
                          "Nenhuma corrida perdida no período."
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Recomendações */}
                  <div className="mt-6 p-4 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg">
                    <h4 className="font-medium text-purple-800 mb-3 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      Recomendações Inteligentes
                    </h4>
                    <div className="space-y-2 text-sm">
                      {(() => {
                        const recomendacoes = [];
                        const total = (data.metricas_principais?.corridas_concluidas || 0) + 
                                    (data.metricas_principais?.corridas_canceladas || 0) + 
                                    (data.metricas_principais?.corridas_perdidas || 0);
                        const taxa_cancelamento = total > 0 ? ((data.metricas_principais?.corridas_canceladas || 0) / total * 100) : 0;
                        const taxa_perda = total > 0 ? ((data.metricas_principais?.corridas_perdidas || 0) / total * 100) : 0;

                        if (taxa_cancelamento > 20) {
                          recomendacoes.push("🎯 Focar na redução de cancelamentos - taxa acima de 20%");
                        }
                        
                        if (taxa_perda > 15) {
                          recomendacoes.push("⚡ Melhorar tempo de resposta - muitas corridas perdidas por timeout");
                        }

                        if (data.motivos_cancelamento && data.motivos_cancelamento[0]?.motivo.includes("motorista")) {
                          recomendacoes.push("👥 Treinamento para motoristas sobre pontualidade");
                        }

                        if (data.comparativo_horarios && data.comparativo_horarios.some(h => h.perdidas > h.concluidas)) {
                          recomendacoes.push("📱 Aumentar disponibilidade de motoristas nos horários de pico");
                        }

                        if (recomendacoes.length === 0) {
                          recomendacoes.push("✅ Operação funcionando bem! Continue monitorando as métricas.");
                        }

                        return recomendacoes.map((rec, idx) => (
                          <div key={idx} className="text-gray-700 dark:text-gray-300">{rec}</div>
                        ));
                      })()}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-600 dark:text-gray-400 font-medium">
                  Carregando insights...
                </div>
              )}
            </div>
          </motion.div>
      </div>
    </div>
  )
}

