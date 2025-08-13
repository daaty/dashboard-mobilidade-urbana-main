
import React from "react"
import { motion } from "framer-motion"
import { Select, SelectOption } from '@/components/ui/select'
import { TrendingUp, CheckCircle, XCircle, AlertTriangle, Clock, BarChart3, Activity, Filter } from 'lucide-react'
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
    periodo: '30d',
    cidade: '',
    categoria: '',
    diaSemana: '',
    horario: ''
  })

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
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
        const response = await fetch(`${API_URL}/api/metrics/overview?periodo=${filters.periodo}`)
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
  }, [filters.periodo])

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
  const evolucaoData = data?.evolucao || []

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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            ANÁLISE OPERACIONAL DE CORRIDAS
          </h1>
          <p className="text-gray-600 text-lg">
            Entenda a saúde e a eficiência da operação. Onde estamos performando bem e onde estão os gargalos?
          </p>
        </motion.div>

        {/* Filtros - Executive Style */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
              <div className="flex items-center gap-3 text-lg font-semibold">
                <div className="bg-blue-500/20 p-2 rounded-lg">
                  <Filter className="w-5 h-5 text-blue-400" />
                </div>
                Filtros de Análise
              </div>
            </div>
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Período</label>
                  <Select
                    value={filters.periodo}
                    onChange={(value) => handleFilterChange('periodo', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
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
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Cidade/Região</label>
                  <Select
                    value={filters.cidade}
                    onChange={(value) => handleFilterChange('cidade', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
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
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Categoria</label>
                  <Select
                    value={filters.categoria}
                    onChange={(value) => handleFilterChange('categoria', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
                  >
                    <SelectOption value="">Todas as categorias</SelectOption>
                    <SelectOption value="economico">Econômico</SelectOption>
                    <SelectOption value="executivo">Executivo</SelectOption>
                    <SelectOption value="premium">Premium</SelectOption>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Dia da Semana</label>
                  <Select
                    value={filters.diaSemana}
                    onChange={(value) => handleFilterChange('diaSemana', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
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
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Horário</label>
                  <Select
                    value={filters.horario}
                    onChange={(value) => handleFilterChange('horario', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
                  >
                    <SelectOption value="">Todos os horários</SelectOption>
                    <SelectOption value="manha">Manhã (6h-12h)</SelectOption>
                    <SelectOption value="tarde">Tarde (12h-18h)</SelectOption>
                    <SelectOption value="noite">Noite (18h-24h)</SelectOption>
                    <SelectOption value="madrugada">Madrugada (0h-6h)</SelectOption>
                  </Select>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* KPI Cards - Executive Style */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {/* Total de Corridas */}
          <div className="bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm font-medium tracking-wide uppercase">Total de Corridas Solicitadas</p>
                <p className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mt-2">
                  {metrics ? formatNumber(metrics.total_corridas) : '0'}
                </p>
                <p className="text-slate-400 text-sm mt-2">Volume total da demanda</p>
              </div>
              <div className="bg-blue-500/20 p-4 rounded-xl">
                <Activity className="w-8 h-8 text-blue-400" />
              </div>
            </div>
          </div>

          {/* Taxa de Conclusão */}
          <div className="bg-gradient-to-br from-emerald-600 via-emerald-700 to-emerald-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-emerald-200 text-sm font-medium tracking-wide uppercase">Taxa de Conclusão</p>
                <p className="text-4xl font-bold bg-gradient-to-r from-emerald-300 to-green-300 bg-clip-text text-transparent mt-2">
                  {metrics ? formatPercentage(metrics.taxa_conclusao) : '0%'}
                </p>
                <p className="text-emerald-300 text-sm mt-2">Eficiência geral da operação</p>
              </div>
              <div className="bg-emerald-500/20 p-4 rounded-xl">
                <CheckCircle className="w-8 h-8 text-emerald-400" />
              </div>
            </div>
          </div>

          {/* Taxa de Cancelamento */}
          <div className="bg-gradient-to-br from-red-600 via-red-700 to-red-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-200 text-sm font-medium tracking-wide uppercase">Taxa de Cancelamento</p>
                <p className="text-4xl font-bold bg-gradient-to-r from-red-300 to-pink-300 bg-clip-text text-transparent mt-2">
                  {metrics ? formatPercentage(metrics.taxa_cancelamento) : '0%'}
                </p>
                <p className="text-red-300 text-sm mt-2">Corridas canceladas</p>
              </div>
              <div className="bg-red-500/20 p-4 rounded-xl">
                <XCircle className="w-8 h-8 text-red-400" />
              </div>
            </div>
          </div>

          {/* Taxa de Perda */}
          <div className="bg-gradient-to-br from-amber-600 via-orange-700 to-orange-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-200 text-sm font-medium tracking-wide uppercase">Taxa de Perda</p>
                <p className="text-4xl font-bold bg-gradient-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent mt-2">
                  {metrics ? formatPercentage(metrics.taxa_perda) : '0%'}
                </p>
                <p className="text-orange-300 text-sm mt-2">Sem aceite de motorista</p>
              </div>
              <div className="bg-orange-500/20 p-4 rounded-xl">
                <AlertTriangle className="w-8 h-8 text-orange-400" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Gráficos e análises detalhadas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Gráfico de Pizza - Distribuição de Status */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 h-96">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-600 rounded-xl">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-blue-800">
                Distribuição por Status das Corridas
              </h3>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="quantidade"
                    nameKey="status"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {statusData.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={Object.values(COLORS)[idx % Object.values(COLORS).length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Gráfico de Tendências */}
          <div className="bg-gradient-to-br from-emerald-50 to-green-100 border border-emerald-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 h-96">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-emerald-600 rounded-xl">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-emerald-800">
                Evolução das Taxas de Performance (%)
              </h3>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={evolucaoData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="data" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="taxa_conclusao" stroke={COLORS.success} name="Conclusão (%)" />
                  <Line type="monotone" dataKey="taxa_cancelamento" stroke={COLORS.danger} name="Cancelamento (%)" />
                  <Line type="monotone" dataKey="taxa_perda" stroke={COLORS.warning} name="Perda (%)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Row 2: Análise de Cancelamentos e Tempos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Análise de Cancelamentos */}
          <div className="bg-gradient-to-br from-red-50 to-pink-100 border border-red-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 h-96">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-600 rounded-xl">
                <XCircle className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-red-800">
                Análise de Causa Raiz - Cancelamentos
              </h3>
            </div>
            <div className="h-80 flex items-center justify-center bg-white/60 backdrop-blur-sm rounded-xl border border-red-200">
              <div className="text-center">
                <div className="text-red-600 text-lg font-medium">Gráfico de cancelamentos</div>
                <div className="text-red-500 text-sm mt-1">(em breve)</div>
              </div>
            </div>
          </div>
          
          {/* Análise de Tempos */}
          <div className="bg-gradient-to-br from-amber-50 to-yellow-100 border border-amber-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 h-96">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-amber-600 rounded-xl">
                <Clock className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-amber-800">
                Análise de Tempos Operacionais
              </h3>
            </div>
            <div className="h-80 flex items-center justify-center bg-white/60 backdrop-blur-sm rounded-xl border border-amber-200">
              <div className="text-center">
                <div className="text-amber-600 text-lg font-medium">Gráfico de tempos</div>
                <div className="text-amber-500 text-sm mt-1">(em breve)</div>
              </div>
            </div>
          </div>
        </div>

        {/* Números Detalhados */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          {/* Corridas Concluídas */}
          <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 border border-emerald-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-emerald-600 rounded-xl">
                <CheckCircle className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-emerald-800">
                Corridas Concluídas
              </h3>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-emerald-700 mb-2">
                {metrics ? formatNumber(metrics.corridas_concluidas) : '0'}
              </p>
              <p className="text-emerald-600 font-medium mb-4">
                {metrics ? formatPercentage(metrics.taxa_conclusao) : '0%'} do total
              </p>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-emerald-200">
                <p className="text-sm font-medium text-emerald-700">
                  Meta ideal: &gt; 85%
                </p>
                <p className="text-xs text-emerald-600 mt-1 font-medium">
                  {metrics && metrics.taxa_conclusao >= 85 ? '✓ Meta atingida' : '⚠ Abaixo da meta'}
                </p>
              </div>
            </div>
          </div>

          {/* Corridas Canceladas */}
          <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-600 rounded-xl">
                <XCircle className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-red-800">
                Corridas Canceladas
              </h3>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-red-700 mb-2">
                {metrics ? formatNumber(metrics.corridas_canceladas) : '0'}
              </p>
              <p className="text-red-600 font-medium mb-4">
                {metrics ? formatPercentage(metrics.taxa_cancelamento) : '0%'} do total
              </p>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-red-200">
                <p className="text-sm font-medium text-red-700">
                  Meta ideal: &lt; 10%
                </p>
                <p className="text-xs text-red-600 mt-1 font-medium">
                  {metrics && metrics.taxa_cancelamento <= 10 ? '✓ Meta atingida' : '⚠ Acima da meta'}
                </p>
              </div>
            </div>
          </div>

          {/* Corridas Perdidas */}
          <div className="bg-gradient-to-br from-amber-50 to-amber-100 border border-amber-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-amber-600 rounded-xl">
                <AlertTriangle className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-amber-800">
                Corridas Perdidas
              </h3>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-amber-700 mb-2">
                {metrics ? formatNumber(metrics.corridas_perdidas) : '0'}
              </p>
              <p className="text-amber-600 font-medium mb-4">
                {metrics ? formatPercentage(metrics.taxa_perda) : '0%'} do total
              </p>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-amber-200">
                <p className="text-sm font-medium text-amber-700">
                  Meta ideal: &lt; 5%
                </p>
                <p className="text-xs text-amber-600 mt-1 font-medium">
                  {metrics && metrics.taxa_perda <= 5 ? '✓ Meta atingida' : '⚠ Acima da meta - Falta de motoristas'}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Insights e Recomendações (placeholder) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <div className="bg-gradient-to-br from-purple-50 to-indigo-100 border border-purple-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-600 rounded-xl">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-purple-800">
                Insights e Recomendações Operacionais
              </h3>
            </div>
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-purple-200">
              <div className="text-center text-purple-600 font-medium">
                Em breve: recomendações automáticas baseadas nos dados reais.
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

