import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import { TrendingUp, TrendingDown, CheckCircle, XCircle, AlertTriangle, Clock, MapPin, Target, BarChart3, Car, Filter } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectOption } from '@/components/ui/select'

const COLORS = {
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
        const response = await fetch('/api/metrics/overview')
        if (response.ok) {
          const result = await response.json()
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
  }, [filters])

  // Função para formatar porcentagem
  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(1)}%`
  }

  // Função para determinar cor baseada na performance
  const getPerformanceColor = (value, type = 'taxa') => {
    if (type === 'conclusao') {
      if (value >= 90) return 'text-green-700 dark:text-green-400'
      if (value >= 75) return 'text-yellow-700 dark:text-yellow-400'
      return 'text-red-700 dark:text-red-400'
    }
    if (type === 'cancelamento' || type === 'perda') {
      if (value <= 5) return 'text-green-700 dark:text-green-400'
      if (value <= 15) return 'text-yellow-700 dark:text-yellow-400'
      return 'text-red-700 dark:text-red-400'
    }
    return 'text-blue-700 dark:text-blue-400'
  }

  if (loading) {
    return (
      <div className="min-h-screen p-6 space-y-8 bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-96 mx-auto mb-4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-64 mx-auto"></div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
                  <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen p-6 space-y-8 bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
        <div className="text-center py-12">
          <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">Erro ao carregar dados de análise</p>
        </div>
      </div>
    )
  }

  // KPIs principais (adaptado para o formato do backend)
  const metricas = data.metricas_principais || {}
  const totalSolicitadas = (metricas.corridas_concluidas || 0) + (metricas.corridas_canceladas || 0) + (metricas.corridas_perdidas || 0)
  const concluidas = metricas.corridas_concluidas || 0
  const canceladas = metricas.corridas_canceladas || 0
  const perdidas = metricas.corridas_perdidas || 0
  
  // Variações
  const variacaoConcluidas = metricas.variacao_concluidas || 0
  const variacaoCanceladas = metricas.variacao_canceladas || 0
  const variacaoPerdidas = metricas.variacao_perdidas || 0
  
  // Taxas
  const taxaConclusao = totalSolicitadas > 0 ? ((concluidas / totalSolicitadas) * 100) : 0
  const taxaCancelamento = totalSolicitadas > 0 ? ((canceladas / totalSolicitadas) * 100) : 0
  const taxaPerda = totalSolicitadas > 0 ? ((perdidas / totalSolicitadas) * 100) : 0

  return (
    <div className="min-h-screen p-6 space-y-8 bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      {/* Header Section */}
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent mb-4">
            ANÁLISE OPERACIONAL DE CORRIDAS
          </h1>
          <p className="text-gray-600 dark:text-gray-300 text-lg">
            Painel de controle para análise operacional e performance de corridas
          </p>
        </div>

        {/* Filtros */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-8 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4 flex items-center">
            <Filter className="mr-2 text-blue-600" size={20} />
            Filtros de Análise
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Período
              </label>
              <Select 
                value={filters.periodo} 
                onChange={(value) => handleFilterChange('periodo', value)}
                className="w-full"
              >
                {periodOptions.map(option => (
                  <SelectOption key={option.value} value={option.value}>
                    {option.label}
                  </SelectOption>
                ))}
              </Select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Cidade
              </label>
              <Select 
                value={filters.cidade} 
                onChange={(value) => handleFilterChange('cidade', value)}
                className="w-full"
              >
                <SelectOption value="">Todas as cidades</SelectOption>
                {(data.cidades || []).map(c => (
                  <SelectOption key={c} value={c}>{c}</SelectOption>
                ))}
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Categoria
              </label>
              <Select 
                value={filters.categoria} 
                onChange={(value) => handleFilterChange('categoria', value)}
                className="w-full"
              >
                <SelectOption value="">Todas as categorias</SelectOption>
                <SelectOption value="economica">Econômica</SelectOption>
                <SelectOption value="conforto">Conforto</SelectOption>
                <SelectOption value="premium">Premium</SelectOption>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Dia da Semana
              </label>
              <Select 
                value={filters.diaSemana} 
                onChange={(value) => handleFilterChange('diaSemana', value)}
                className="w-full"
              >
                <SelectOption value="">Todos os dias</SelectOption>
                <SelectOption value="segunda">Segunda-feira</SelectOption>
                <SelectOption value="terca">Terça-feira</SelectOption>
                <SelectOption value="quarta">Quarta-feira</SelectOption>
                <SelectOption value="quinta">Quinta-feira</SelectOption>
                <SelectOption value="sexta">Sexta-feira</SelectOption>
                <SelectOption value="sabado">Sábado</SelectOption>
                <SelectOption value="domingo">Domingo</SelectOption>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Horário
              </label>
              <Select 
                value={filters.horario} 
                onChange={(value) => handleFilterChange('horario', value)}
                className="w-full"
              >
                <SelectOption value="">Todos os horários</SelectOption>
                <SelectOption value="madrugada">Madrugada (00-06h)</SelectOption>
                <SelectOption value="manha">Manhã (06-12h)</SelectOption>
                <SelectOption value="tarde">Tarde (12-18h)</SelectOption>
                <SelectOption value="noite">Noite (18-00h)</SelectOption>
              </Select>
            </div>
          </div>
        </div>

        {/* KPIs Principais */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total de Corridas */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-700 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Car className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2" />
                <h3 className="text-sm font-medium text-blue-700 dark:text-blue-300">Total de Corridas</h3>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                {totalSolicitadas.toLocaleString()}
              </div>
              <div className="text-sm text-blue-600 dark:text-blue-400">
                Corridas solicitadas no período
              </div>
            </div>
          </div>

          {/* Taxa de Conclusão */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-2xl p-6 border border-green-200 dark:border-green-700 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
                <h3 className="text-sm font-medium text-green-700 dark:text-green-300">Taxa de Conclusão</h3>
              </div>
              <div className={`flex items-center text-xs px-2 py-1 rounded-full ${getPerformanceColor(taxaConclusao, 'conclusao').includes('green') ? 'bg-green-100 text-green-700' : getPerformanceColor(taxaConclusao, 'conclusao').includes('yellow') ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                {variacaoConcluidas >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                {Math.abs(variacaoConcluidas)}%
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-green-900 dark:text-green-100">
                {formatPercentage(taxaConclusao)}
              </div>
              <div className="text-sm text-green-600 dark:text-green-400">
                {concluidas.toLocaleString()} corridas concluídas
              </div>
            </div>
          </div>

          {/* Taxa de Cancelamento */}
          <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-2xl p-6 border border-red-200 dark:border-red-700 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
                <h3 className="text-sm font-medium text-red-700 dark:text-red-300">Taxa de Cancelamento</h3>
              </div>
              <div className={`flex items-center text-xs px-2 py-1 rounded-full ${getPerformanceColor(taxaCancelamento, 'cancelamento').includes('green') ? 'bg-green-100 text-green-700' : getPerformanceColor(taxaCancelamento, 'cancelamento').includes('yellow') ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                {variacaoCanceladas >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                {Math.abs(variacaoCanceladas)}%
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-red-900 dark:text-red-100">
                {formatPercentage(taxaCancelamento)}
              </div>
              <div className="text-sm text-red-600 dark:text-red-400">
                {canceladas.toLocaleString()} corridas canceladas
              </div>
            </div>
          </div>

          {/* Taxa de Perda */}
          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 rounded-2xl p-6 border border-yellow-200 dark:border-yellow-700 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-2" />
                <h3 className="text-sm font-medium text-yellow-700 dark:text-yellow-300">Taxa de Perda</h3>
              </div>
              <div className={`flex items-center text-xs px-2 py-1 rounded-full ${getPerformanceColor(taxaPerda, 'perda').includes('green') ? 'bg-green-100 text-green-700' : getPerformanceColor(taxaPerda, 'perda').includes('yellow') ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                {variacaoPerdidas >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                {Math.abs(variacaoPerdidas)}%
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-yellow-900 dark:text-yellow-100">
                {formatPercentage(taxaPerda)}
              </div>
              <div className="text-sm text-yellow-600 dark:text-yellow-400">
                {perdidas.toLocaleString()} corridas perdidas
              </div>
            </div>
          </div>
        </div>

        {/* Placeholder para gráficos futuros */}
        <div className="text-center py-8">
          <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">Gráficos e análises detalhadas em desenvolvimento</p>
        </div>
      </div>
    </div>
  )
}
