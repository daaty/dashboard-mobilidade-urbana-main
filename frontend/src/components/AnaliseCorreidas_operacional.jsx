import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, AreaChart, Area } from 'recharts'
import { TrendingUp, TrendingDown, CheckCircle, XCircle, AlertTriangle, Clock, MapPin, Target, BarChart3, Car, Filter, Users, Calendar, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectOption } from '@/components/ui/select'

const COLORS = {
  concluidas: '#10B981',    // Verde
  canceladas: '#EF4444',    // Vermelho
  perdidas: '#F59E0B',      // Amarelo/Laranja
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
  { label: '90 dias', value: '90d' }
]

export default function AnaliseCorreidas() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    periodo: '30d',
    cidade: '',
    categoria: '',
    diaSemana: '',
    horario: ''
  })

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await fetch(`/api/metrics/overview?periodo=${filters.periodo}`)
        if (response.ok) {
          const result = await response.json()
          console.log('Dados recebidos da API:', result)
          setData(result)
        } else {
          console.error('Erro ao buscar dados:', response.statusText)
        }
      } catch (error) {
        console.error('Erro ao buscar dados:', error)
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

  const generateChartData = () => {
    if (!data?.metricas_principais) return []

    const metrics = calculateMetrics()
    return [
      { name: 'Concluídas', value: metrics.corridas_concluidas, color: COLORS.concluidas },
      { name: 'Canceladas', value: metrics.corridas_canceladas, color: COLORS.canceladas },
      { name: 'Perdidas', value: metrics.corridas_perdidas, color: COLORS.perdidas }
    ]
  }

  const generateTrendData = () => {
    // Dados simulados para demonstração - seria ideal vir da API
    return [
      { periodo: 'Sem 1', conclusao: 85, cancelamento: 10, perda: 5 },
      { periodo: 'Sem 2', conclusao: 88, cancelamento: 8, perda: 4 },
      { periodo: 'Sem 3', conclusao: 82, cancelamento: 12, perda: 6 },
      { periodo: 'Sem 4', conclusao: 90, cancelamento: 7, perda: 3 }
    ]
  }

  const generateCancelamentoData = () => {
    return [
      { motivo: 'Motorista cancelou', valor: 45, cor: '#EF4444' },
      { motivo: 'Passageiro cancelou', valor: 35, cor: '#F59E0B' },
      { motivo: 'Problema técnico', valor: 12, cor: '#6B7280' },
      { motivo: 'Outros motivos', valor: 8, cor: '#9CA3AF' }
    ]
  }

  const generateTempoData = () => {
    return [
      { categoria: 'Tempo de Espera', tempo: 4.2, meta: 5.0, status: 'bom' },
      { categoria: 'Tempo até Chegada', tempo: 8.5, meta: 10.0, status: 'bom' },
      { categoria: 'Duração Média', tempo: 18.3, meta: 20.0, status: 'bom' }
    ]
  }

  const metrics = calculateMetrics()
  const chartData = generateChartData()
  const trendData = generateTrendData()
  const cancelamentoData = generateCancelamentoData()
  const tempoData = generateTempoData()

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
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

        {/* Filtros */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filtros de Análise
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <Select
                  value={filters.periodo}
                  onChange={(value) => handleFilterChange('periodo', value)}
                >
                  <SelectOption value="">Período</SelectOption>
                  {periodOptions.map(option => (
                    <SelectOption key={option.value} value={option.value}>
                      {option.label}
                    </SelectOption>
                  ))}
                </Select>
                <Select
                  value={filters.cidade}
                  onChange={(value) => handleFilterChange('cidade', value)}
                >
                  <SelectOption value="">Cidade/Região</SelectOption>
                  <SelectOption value="sp">São Paulo</SelectOption>
                  <SelectOption value="rj">Rio de Janeiro</SelectOption>
                  <SelectOption value="bh">Belo Horizonte</SelectOption>
                </Select>
                <Select
                  value={filters.categoria}
                  onChange={(value) => handleFilterChange('categoria', value)}
                >
                  <SelectOption value="">Categoria do Veículo</SelectOption>
                  <SelectOption value="economico">Econômico</SelectOption>
                  <SelectOption value="executivo">Executivo</SelectOption>
                  <SelectOption value="premium">Premium</SelectOption>
                </Select>
                <Select
                  value={filters.diaSemana}
                  onChange={(value) => handleFilterChange('diaSemana', value)}
                >
                  <SelectOption value="">Dia da Semana</SelectOption>
                  <SelectOption value="seg">Segunda</SelectOption>
                  <SelectOption value="ter">Terça</SelectOption>
                  <SelectOption value="qua">Quarta</SelectOption>
                  <SelectOption value="qui">Quinta</SelectOption>
                  <SelectOption value="sex">Sexta</SelectOption>
                  <SelectOption value="sab">Sábado</SelectOption>
                  <SelectOption value="dom">Domingo</SelectOption>
                </Select>
                <Select
                  value={filters.horario}
                  onChange={(value) => handleFilterChange('horario', value)}
                >
                  <SelectOption value="">Hora do Dia</SelectOption>
                  <SelectOption value="manha">Manhã (6h-12h)</SelectOption>
                  <SelectOption value="tarde">Tarde (12h-18h)</SelectOption>
                  <SelectOption value="noite">Noite (18h-24h)</SelectOption>
                  <SelectOption value="madrugada">Madrugada (0h-6h)</SelectOption>
                </Select>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* KPI Cards - Scorecards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {/* Total de Corridas */}
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium">Total de Corridas Solicitadas</p>
                  <p className="text-3xl font-bold">{metrics ? formatNumber(metrics.total_corridas) : '0'}</p>
                  <p className="text-blue-200 text-sm mt-1">Volume total da demanda</p>
                </div>
                <Activity className="w-12 h-12 text-blue-200" />
              </div>
            </CardContent>
          </Card>

          {/* Taxa de Conclusão */}
          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0 shadow-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm font-medium">Taxa de Conclusão</p>
                  <p className="text-3xl font-bold">{metrics ? formatPercentage(metrics.taxa_conclusao) : '0%'}</p>
                  <p className="text-green-200 text-sm mt-1">Eficiência geral da operação</p>
                </div>
                <CheckCircle className="w-12 h-12 text-green-200" />
              </div>
            </CardContent>
          </Card>

          {/* Taxa de Cancelamento */}
          <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white border-0 shadow-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-red-100 text-sm font-medium">Taxa de Cancelamento</p>
                  <p className="text-3xl font-bold">{metrics ? formatPercentage(metrics.taxa_cancelamento) : '0%'}</p>
                  <p className="text-red-200 text-sm mt-1">Corridas canceladas</p>
                </div>
                <XCircle className="w-12 h-12 text-red-200" />
              </div>
            </CardContent>
          </Card>

          {/* Taxa de Perda */}
          <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0 shadow-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm font-medium">Taxa de Perda</p>
                  <p className="text-3xl font-bold">{metrics ? formatPercentage(metrics.taxa_perda) : '0%'}</p>
                  <p className="text-orange-200 text-sm mt-1">Sem aceite de motorista</p>
                </div>
                <AlertTriangle className="w-12 h-12 text-orange-200" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Row 1: Distribuição e Tendências */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Gráfico de Pizza - Distribuição de Status */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl h-96">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Distribuição por Status das Corridas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatNumber(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Gráfico de Tendências */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl h-96">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Evolução das Taxas de Performance (%)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="periodo" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="conclusao"
                      stroke={COLORS.concluidas}
                      strokeWidth={3}
                      name="Taxa de Conclusão"
                    />
                    <Line
                      type="monotone"
                      dataKey="cancelamento"
                      stroke={COLORS.canceladas}
                      strokeWidth={3}
                      name="Taxa de Cancelamento"
                    />
                    <Line
                      type="monotone"
                      dataKey="perda"
                      stroke={COLORS.perdidas}
                      strokeWidth={3}
                      name="Taxa de Perda"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Row 2: Análise de Cancelamentos e Tempos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Análise de Cancelamentos */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl h-96">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  Análise de Causa Raiz - Cancelamentos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={cancelamentoData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="motivo" type="category" width={100} />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Bar dataKey="valor" fill={COLORS.canceladas} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Análise de Tempos */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
          >
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl h-96">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Análise de Tempos Operacionais
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {tempoData.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{item.categoria}</p>
                        <p className="text-sm text-gray-600">Meta: {item.meta} min</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-blue-600">{item.tempo} min</p>
                        <p className={`text-sm ${item.status === 'bom' ? 'text-green-600' : 'text-red-600'}`}>
                          {item.status === 'bom' ? '✓ Dentro da meta' : '⚠ Acima da meta'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Números Detalhados */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          {/* Corridas Concluídas */}
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <CheckCircle className="w-5 h-5" />
                Corridas Concluídas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-4xl font-bold text-green-600 mb-2">
                  {metrics ? formatNumber(metrics.corridas_concluidas) : '0'}
                </p>
                <p className="text-gray-600">
                  {metrics ? formatPercentage(metrics.taxa_conclusao) : '0%'} do total
                </p>
                <div className="mt-4 bg-green-100 rounded-lg p-3">
                  <p className="text-sm text-green-700">
                    Meta ideal: &gt; 85%
                  </p>
                  <p className="text-xs text-green-600 mt-1">
                    {metrics && metrics.taxa_conclusao >= 85 ? '✓ Meta atingida' : '⚠ Abaixo da meta'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Corridas Canceladas */}
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <XCircle className="w-5 h-5" />
                Corridas Canceladas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-4xl font-bold text-red-600 mb-2">
                  {metrics ? formatNumber(metrics.corridas_canceladas) : '0'}
                </p>
                <p className="text-gray-600">
                  {metrics ? formatPercentage(metrics.taxa_cancelamento) : '0%'} do total
                </p>
                <div className="mt-4 bg-red-100 rounded-lg p-3">
                  <p className="text-sm text-red-700">
                    Meta ideal: &lt; 10%
                  </p>
                  <p className="text-xs text-red-600 mt-1">
                    {metrics && metrics.taxa_cancelamento <= 10 ? '✓ Meta atingida' : '⚠ Acima da meta'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Corridas Perdidas */}
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-600">
                <AlertTriangle className="w-5 h-5" />
                Corridas Perdidas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-4xl font-bold text-orange-600 mb-2">
                  {metrics ? formatNumber(metrics.corridas_perdidas) : '0'}
                </p>
                <p className="text-gray-600">
                  {metrics ? formatPercentage(metrics.taxa_perda) : '0%'} do total
                </p>
                <div className="mt-4 bg-orange-100 rounded-lg p-3">
                  <p className="text-sm text-orange-700">
                    Meta ideal: &lt; 5%
                  </p>
                  <p className="text-xs text-orange-600 mt-1">
                    {metrics && metrics.taxa_perda <= 5 ? '✓ Meta atingida' : '⚠ Acima da meta - Falta de motoristas'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Insights e Recomendações */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Insights e Recomendações Operacionais
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-green-600 mb-3">✅ Pontos Fortes</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>
                        Taxa de conclusão {metrics ? formatPercentage(metrics.taxa_conclusao) : '0%'} 
                        {metrics && metrics.taxa_conclusao >= 85 ? ' - Dentro da meta' : ' - Precisa melhorar'}
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Volume de demanda: {metrics ? formatNumber(metrics.total_corridas) : '0'} corridas solicitadas</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Tempos operacionais dentro das metas estabelecidas</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-red-600 mb-3">⚠️ Pontos de Atenção</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                      <span>
                        Taxa de cancelamento: {metrics ? formatPercentage(metrics.taxa_cancelamento) : '0%'}
                        {metrics && metrics.taxa_cancelamento > 10 ? ' - Acima da meta (>10%)' : ' - Dentro da meta'}
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                      <span>
                        Taxa de perda: {metrics ? formatPercentage(metrics.taxa_perda) : '0%'}
                        {metrics && metrics.taxa_perda > 5 ? ' - Indica falta de motoristas nas áreas/horários' : ' - Dentro da meta'}
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span>Principal motivo de cancelamento: Motoristas cancelando (45%)</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h5 className="font-semibold text-blue-700 mb-2">🎯 Próximos Passos Recomendados:</h5>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Implementar incentivos para motoristas em horários/áreas com alta taxa de perda</li>
                  <li>• Investigar e reduzir principais motivos de cancelamento por motoristas</li>
                  <li>• Monitorar metas de tempo de espera e chegada continuamente</li>
                  <li>• Criar campanhas de engajamento para manter motoristas ativos</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
