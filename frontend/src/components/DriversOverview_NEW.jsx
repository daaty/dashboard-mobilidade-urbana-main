import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  Clock, 
  Star, 
  BarChart3,
  Filter,
  Download,
  Search,
  MapPin,
  Calendar,
  Activity
} from 'lucide-react'

// Configuração da URL da API
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Componente de Filtros
const DriversFilters = ({ filters, onFiltersChange, cities, loading }) => {
  const periodOptions = [
    { value: 'hoje', label: 'Hoje' },
    { value: '7_days', label: '7 Dias' },
    { value: '30_days', label: '30 Dias' },
    { value: '3_months', label: '3 Meses' },
    { value: '6_months', label: '6 Meses' },
    { value: '12_months', label: '12 Meses' }
  ]

  const statusOptions = [
    { value: 'all', label: 'Todos' },
    { value: 'active', label: 'Ativos' },
    { value: 'inactive', label: 'Inativos' }
  ]

  const performanceOptions = [
    { value: 'all', label: 'Todos' },
    { value: 'excellent', label: 'Excelente (≥4.5)' },
    { value: 'good', label: 'Bom (4.0-4.4)' },
    { value: 'medium', label: 'Médio (3.5-3.9)' },
    { value: 'below', label: 'Abaixo (<3.5)' }
  ]

  const revenueOptions = [
    { value: 'all', label: 'Todas as faixas' },
    { value: '0-500', label: 'R$ 0 - R$ 500' },
    { value: '500-1000', label: 'R$ 500 - R$ 1.000' },
    { value: '1000-2000', label: 'R$ 1.000 - R$ 2.000' },
    { value: '2000+', label: 'R$ 2.000+' }
  ]

  const orderOptions = [
    { value: 'rating', label: 'Por Avaliação' },
    { value: 'rides', label: 'Por Corridas' },
    { value: 'revenue', label: 'Por Receita' },
    { value: 'name', label: 'Por Nome' }
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Filter className="w-5 h-5 mr-2" />
        Filtros de Análise - Motoristas
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Período */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Período</label>
          <select
            value={filters.period}
            onChange={(e) => onFiltersChange({ ...filters, period: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {periodOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
          <select
            value={filters.status}
            onChange={(e) => onFiltersChange({ ...filters, status: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {statusOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Performance */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Performance</label>
          <select
            value={filters.performance}
            onChange={(e) => onFiltersChange({ ...filters, performance: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {performanceOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Cidade */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Cidade</label>
          <select
            value={filters.city}
            onChange={(e) => onFiltersChange({ ...filters, city: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          >
            <option value="all">Todas as Cidades</option>
            {cities.map(city => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        </div>

        {/* Faixa de Receita */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Faixa de Receita</label>
          <select
            value={filters.revenue_range}
            onChange={(e) => onFiltersChange({ ...filters, revenue_range: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {revenueOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Ordenação */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Ordenação</label>
          <select
            value={filters.order_by}
            onChange={(e) => onFiltersChange({ ...filters, order_by: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {orderOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}

// Componente de KPIs
const DriversKPIs = ({ kpis, loading }) => {
  const kpiCards = [
    {
      title: 'Total de Motoristas',
      value: kpis?.total_drivers || 0,
      subtitle: `${kpis?.active_drivers || 0} com atividade registrada`,
      icon: Users,
      color: 'blue'
    },
    {
      title: 'Corridas Canceladas',
      value: kpis?.cancelled_rides || 0,
      subtitle: 'Total por todos os motoristas',
      icon: Activity,
      color: 'red'
    },
    {
      title: 'Média por Motorista',
      value: `${kpis?.avg_hours_online || 0}h`,
      subtitle: 'Horas online médias',
      icon: Clock,
      color: 'green'
    },
    {
      title: 'Rating Médio',
      value: kpis?.avg_rating || 0,
      subtitle: 'Avaliação média dos motoristas',
      icon: Star,
      color: 'yellow'
    },
    {
      title: 'Receita Total',
      value: `R$ ${(kpis?.total_revenue || 0).toFixed(2)}`,
      subtitle: 'Últimos 90 dias',
      icon: DollarSign,
      color: 'purple'
    },
    {
      title: 'Taxa de Aceitação',
      value: `${(kpis?.acceptance_rate || 0).toFixed(1)}%`,
      subtitle: 'Média geral',
      icon: TrendingUp,
      color: 'indigo'
    },
    {
      title: 'Receita por Hora',
      value: `R$ ${(kpis?.revenue_per_hour || 0).toFixed(2)}`,
      subtitle: 'Produtividade média',
      icon: BarChart3,
      color: 'pink'
    },
    {
      title: 'Distância Total',
      value: `${(kpis?.total_distance || 0).toFixed(1)} km`,
      subtitle: 'Quilometragem acumulada',
      icon: MapPin,
      color: 'cyan'
    }
  ]

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {Array(8).fill(0).map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {kpiCards.map((kpi, index) => {
        const Icon = kpi.icon
        return (
          <motion.div
            key={kpi.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg bg-${kpi.color}-100`}>
                <Icon className={`w-6 h-6 text-${kpi.color}-600`} />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">{kpi.value}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">{kpi.title}</p>
            <p className="text-xs text-gray-500">{kpi.subtitle}</p>
          </motion.div>
        )
      })}
    </div>
  )
}

// Componente principal
const DriversOverview = () => {
  const [filters, setFilters] = useState({
    period: '3_months',
    city: 'all',
    status: 'all',
    performance: 'all',
    revenue_range: 'all',
    order_by: 'rating'
  })

  const [kpis, setKpis] = useState(null)
  const [drivers, setDrivers] = useState([])
  const [cities, setCities] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingKpis, setLoadingKpis] = useState(true)
  const [loadingDrivers, setLoadingDrivers] = useState(true)

  // Buscar cidades disponíveis
  useEffect(() => {
    fetchCities()
  }, [])

  // Buscar dados quando filtros mudarem
  useEffect(() => {
    fetchKpis()
    fetchDrivers()
    fetchAnalytics()
  }, [filters])

  const fetchCities = async () => {
    try {
      const response = await fetch(`${API_URL}/api/drivers/cities`)
      const data = await response.json()
      if (data.success) {
        setCities(data.data)
      }
    } catch (error) {
      console.error('Erro ao buscar cidades:', error)
    }
  }

  const fetchKpis = async () => {
    try {
      setLoadingKpis(true)
      const params = new URLSearchParams({
        period: filters.period,
        city: filters.city,
        status: filters.status
      })
      
      const response = await fetch(`${API_URL}/api/drivers/kpis?${params}`)
      const data = await response.json()
      
      if (data.success) {
        setKpis(data.data)
      }
    } catch (error) {
      console.error('Erro ao buscar KPIs:', error)
    } finally {
      setLoadingKpis(false)
    }
  }

  const fetchDrivers = async () => {
    try {
      setLoadingDrivers(true)
      const params = new URLSearchParams({
        period: filters.period,
        city: filters.city,
        status: filters.status,
        performance: filters.performance,
        revenue_range: filters.revenue_range,
        order_by: filters.order_by,
        limit: 50,
        offset: 0
      })
      
      const response = await fetch(`${API_URL}/api/drivers/list?${params}`)
      const data = await response.json()
      
      if (data.success) {
        setDrivers(data.data.drivers)
      }
    } catch (error) {
      console.error('Erro ao buscar motoristas:', error)
    } finally {
      setLoadingDrivers(false)
      setLoading(false)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const params = new URLSearchParams({
        period: filters.period,
        city: filters.city
      })
      
      const response = await fetch(`${API_URL}/api/drivers/analytics?${params}`)
      const data = await response.json()
      
      if (data.success) {
        setAnalytics(data.data)
      }
    } catch (error) {
      console.error('Erro ao buscar analytics:', error)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">GESTÃO DE MOTORISTAS</h1>
        <p className="text-gray-600">Dashboard executivo com KPIs e métricas de performance dos motoristas</p>
        
        <div className="mt-4 flex items-center space-x-4 text-sm">
          <div className="flex items-center text-green-600">
            <div className="w-2 h-2 bg-green-600 rounded-full mr-2"></div>
            Dados Analíticos: Conectado
          </div>
          <div className="flex items-center text-blue-600">
            <div className="w-2 h-2 bg-blue-600 rounded-full mr-2"></div>
            Modal de Detalhes: Disponível
          </div>
        </div>
      </div>

      {/* Filtros */}
      <DriversFilters 
        filters={filters}
        onFiltersChange={setFilters}
        cities={cities}
        loading={loading}
      />

      {/* KPIs */}
      <DriversKPIs kpis={kpis} loading={loadingKpis} />

      {/* Lista de Motoristas */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Ranking e Performance - Todos os Motoristas
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Lista Completa de Motoristas
          </p>
        </div>

        <div className="overflow-x-auto">
          {loadingDrivers ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-500 mt-2">Carregando motoristas...</p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Motorista
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Horas Online
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Corridas
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rating
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cidade
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {drivers.map((driver, index) => (
                  <tr key={driver.driver_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8">
                          <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center text-sm font-medium text-gray-700">
                            {index + 1}
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {driver.name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {driver.hours_online}h online
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>
                        <div>{driver.total_rides} corridas</div>
                        <div className="text-xs text-gray-500">{driver.cancelled_rides} canceladas</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Star className="w-4 h-4 text-yellow-400 mr-1" />
                        <span className="text-sm text-gray-900">{driver.rating}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        driver.performance_category === 'excellent' ? 'bg-green-100 text-green-800' :
                        driver.performance_category === 'good' ? 'bg-blue-100 text-blue-800' :
                        driver.performance_category === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {driver.performance_category === 'excellent' ? 'Excelente' :
                         driver.performance_category === 'good' ? 'Bom' :
                         driver.performance_category === 'medium' ? 'Médio' : 'Abaixo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {driver.city}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

export default DriversOverview
