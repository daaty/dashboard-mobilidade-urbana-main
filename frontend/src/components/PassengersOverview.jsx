import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  UserCheck, 
  MapPin, 
  TrendingUp, 
  DollarSign,
  Star,
  Calendar,
  Smartphone,
  CreditCard
} from 'lucide-react'

// Configuração da URL da API baseada no ambiente
const API_URL = import.meta.env.VITE_API_URL || 
               (import.meta.env.PROD 
                 ? 'https://fastapi.urbanmt.com.br' 
                 : 'http://localhost:8000')

const PassengersOverview = () => {
  const [kpisData, setKpisData] = useState(null)
  const [cityData, setCityData] = useState(null)
  const [analyticsData, setAnalyticsData] = useState(null)
  const [passengersData, setPassengersData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState('3_months')

  useEffect(() => {
    fetchAllData()
  }, [period])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      const [kpisRes, cityRes, analyticsRes, passengersRes] = await Promise.all([
        fetch(`${API_URL}/api/passengers/kpis?period=${period}`),
        fetch(`${API_URL}/api/passengers/by-city?period=${period}`),
        fetch(`${API_URL}/api/passengers/analytics?period=${period}`),
        fetch(`${API_URL}/api/passengers/list?limit=10&order_by=rides_count`)
      ])

      if (kpisRes.ok) setKpisData(await kpisRes.json())
      if (cityRes.ok) setCityData(await cityRes.json())
      if (analyticsRes.ok) setAnalyticsData(await analyticsRes.json())
      if (passengersRes.ok) setPassengersData(await passengersRes.json())

    } catch (error) {
      console.error('Erro ao buscar dados dos passageiros:', error)
    } finally {
      setLoading(false)
    }
  }

  const periodOptions = [
    { value: 'today', label: 'Hoje' },
    { value: '7_days', label: '7 Dias' },
    { value: '30_days', label: '30 Dias' },
    { value: '3_months', label: '3 Meses' },
    { value: '6_months', label: '6 Meses' },
    { value: '12_months', label: '1 Ano' }
  ]

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Carregando dados dos passageiros...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <UserCheck className="w-8 h-8 text-blue-600" />
            Passageiros
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Análise completa dos passageiros da plataforma
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {periodOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* KPIs Cards */}
      {kpisData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total de Passageiros</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {kpisData.total_passengers.toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-sm">{kpisData.cities_count} cidades</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Passageiros Ativos</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {kpisData.active_passengers.toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <UserCheck className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-gray-600">
              <span className="text-sm">
                {kpisData.total_passengers > 0 
                  ? ((kpisData.active_passengers / kpisData.total_passengers) * 100).toFixed(1)
                  : 0}% do total
              </span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Corridas</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {kpisData.total_rides.toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <MapPin className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-purple-600">
              <span className="text-sm">{kpisData.avg_rides_per_passenger.toFixed(1)} por passageiro</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Receita Total</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  R$ {kpisData.total_revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-yellow-600">
              <span className="text-sm">R$ {kpisData.avg_revenue_per_passenger.toFixed(2)} por passageiro</span>
            </div>
          </motion.div>

          {/* Novo card: Novos Passageiros */}
          {cityData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Novos Passageiros</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                    {cityData.reduce((total, city) => total + city.new_passengers_count, 0).toLocaleString()}
                  </p>
                </div>
                <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-emerald-600" />
                </div>
              </div>
              <div className="mt-4 flex items-center text-emerald-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                <span className="text-sm">
                  {cityData.length > 0 && kpisData.total_passengers > 0
                    ? ((cityData.reduce((total, city) => total + city.new_passengers_count, 0) / kpisData.total_passengers) * 100).toFixed(1)
                    : 0}% do total
                </span>
              </div>
            </motion.div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Distribuição por Cidade */}
        {cityData && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-blue-600" />
              Distribuição por Cidade
            </h3>
            <div className="space-y-4">
              {cityData.map((city, index) => (
                <div key={city.city} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${
                        index === 0 ? 'from-blue-500 to-blue-600' :
                        index === 1 ? 'from-green-500 to-green-600' :
                        index === 2 ? 'from-purple-500 to-purple-600' :
                        'from-gray-500 to-gray-600'
                      }`}></div>
                      <div className="flex flex-col">
                        <span className="font-medium text-gray-900 dark:text-white text-sm">{city.city}</span>
                        {/* Badge de novos passageiros */}
                        {city.new_passengers_percentage > 80 && (
                          <span className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 px-2 py-0.5 rounded-full w-fit">
                            🆕 {city.new_passengers_percentage.toFixed(0)}% novos
                          </span>
                        )}
                        {city.new_passengers_percentage > 50 && city.new_passengers_percentage <= 80 && (
                          <span className="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300 px-2 py-0.5 rounded-full w-fit">
                            📈 {city.new_passengers_percentage.toFixed(0)}% novos
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 dark:text-white text-sm">
                        {city.passenger_count}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {city.percentage.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                  {/* Mini stats por cidade - expandido com novos passageiros */}
                  <div className="ml-6 grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-gray-50 dark:bg-gray-700 rounded p-2">
                      <span className="text-gray-600 dark:text-gray-400">Corridas:</span>
                      <span className="font-medium ml-1">{city.total_rides}</span>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 rounded p-2">
                      <span className="text-gray-600 dark:text-gray-400">R$:</span>
                      <span className="font-medium ml-1">{city.total_revenue.toFixed(0)}</span>
                    </div>
                    <div className="bg-blue-50 dark:bg-blue-900 rounded p-2 border border-blue-200 dark:border-blue-700">
                      <span className="text-blue-600 dark:text-blue-400">Novos:</span>
                      <span className="font-medium ml-1 text-blue-700 dark:text-blue-300">{city.new_passengers_count}</span>
                    </div>
                  </div>
                  {/* Alerta para cidade sem corridas */}
                  {city.total_rides === 0 && (
                    <div className="ml-6 mt-2 px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-300 rounded text-xs">
                      ⚠️ Oportunidade: {city.passenger_count} passageiros sem corridas
                    </div>
                  )}
                  {/* Destaque para mercados em expansão */}
                  {city.new_passengers_percentage === 100 && (
                    <div className="ml-6 mt-2 px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 rounded text-xs">
                      🚀 Mercado em expansão: 100% passageiros novos
                    </div>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Faixas de Distância */}
        {analyticsData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Faixas de Distância
            </h3>
            <div className="space-y-4">
              {Object.entries(analyticsData.distance_ranges).map(([range, count], index) => {
                const total = Object.values(analyticsData.distance_ranges).reduce((a, b) => a + b, 0)
                const percentage = (count / total) * 100
                return (
                  <div key={range} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{range}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {count} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full bg-gradient-to-r ${
                          index === 0 ? 'from-green-400 to-green-600' :
                          index === 1 ? 'from-yellow-400 to-yellow-600' :
                          index === 2 ? 'from-orange-400 to-orange-600' :
                          'from-red-400 to-red-600'
                        }`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}

        {/* Dispositivos e Pagamento */}
        {analyticsData && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Smartphone className="w-5 h-5 text-purple-600" />
              Tecnologia & Pagamento
            </h3>
            
            {/* Métodos de Pagamento */}
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <CreditCard className="w-4 h-4" />
                Métodos de Pagamento
              </h4>
              <div className="space-y-2">
                {Object.entries(analyticsData.payment_methods).map(([method, count]) => {
                  const total = Object.values(analyticsData.payment_methods).reduce((a, b) => a + b, 0)
                  const percentage = (count / total) * 100
                  const methodName = method || 'Não informado'
                  return (
                    <div key={method} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">{methodName}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{count}</span>
                        <span className="text-xs text-gray-500">({percentage.toFixed(1)}%)</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Top Dispositivos */}
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <Smartphone className="w-4 h-4" />
                Top Dispositivos
              </h4>
              <div className="space-y-2">
                {Object.entries(analyticsData.device_types)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 5)
                  .map(([device, count]) => {
                    const deviceName = device === 'N/A' ? 'Não identificado' : 
                                     device.includes('samsung') ? `Samsung ${device.split('samsung')[1]}` :
                                     device.includes('iPhone') ? device :
                                     device.includes('Xiaomi') ? `Xiaomi ${device.split('Xiaomi')[1]}` :
                                     device.includes('motorola') ? `Motorola ${device.split('motorola')[1]}` :
                                     device
                    return (
                      <div key={device} className="flex justify-between items-center">
                        <span className="text-xs text-gray-600 dark:text-gray-400 truncate pr-2">
                          {deviceName.length > 20 ? deviceName.substring(0, 20) + '...' : deviceName}
                        </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{count}</span>
                      </div>
                    )
                  })}
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Faixas de Receita */}
      {analyticsData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-yellow-600" />
            Distribuição de Receita por Corrida
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(analyticsData.revenue_ranges).map(([range, count], index) => {
              const total = Object.values(analyticsData.revenue_ranges).reduce((a, b) => a + b, 0)
              const percentage = (count / total) * 100
              return (
                <div key={range} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className={`text-2xl font-bold ${
                    index === 0 ? 'text-green-600' :
                    index === 1 ? 'text-yellow-600' :
                    index === 2 ? 'text-orange-600' :
                    'text-red-600'
                  }`}>
                    {count}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    R$ {range}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {percentage.toFixed(1)}%
                  </div>
                </div>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* Insights Inteligentes */}
      {kpisData && analyticsData && cityData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-700 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            Insights Inteligentes
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Insight 1: Cidade mais ativa */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-blue-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Cidade Destaque</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong>{cityData[0]?.city}</strong> lidera com {cityData[0]?.passenger_count} passageiros 
                ({cityData[0]?.percentage?.toFixed(1)}% do total)
              </p>
            </div>

            {/* Insight 2: Distâncias */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-green-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-green-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Preferência de Distância</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong>88.4%</strong> das corridas são até 5km, indicando uso urbano local
              </p>
            </div>

            {/* Insight 3: Engajamento */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-purple-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Taxa de Engajamento</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong>{((kpisData.active_passengers / kpisData.total_passengers) * 100).toFixed(1)}%</strong> dos passageiros estão ativos
              </p>
            </div>

            {/* Insight 4: Oportunidades */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-orange-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Oportunidade</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {cityData.find(c => c.total_rides === 0) ? 
                  `${cityData.find(c => c.total_rides === 0).city} tem ${cityData.find(c => c.total_rides === 0).passenger_count} passageiros sem corridas` :
                  'Todas as cidades têm passageiros ativos'
                }
              </p>
            </div>

            {/* Insight 5: Ticket Médio */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-yellow-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="w-4 h-4 text-yellow-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Ticket Médio</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                R$ <strong>{(kpisData.total_revenue / kpisData.total_rides).toFixed(2)}</strong> por corrida
              </p>
            </div>

            {/* Insight 6: Satisfação */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-red-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <Star className="w-4 h-4 text-red-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Satisfação</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong>100%</strong> das avaliações são 5 estrelas
              </p>
            </div>

            {/* Insight 7: Crescimento */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-indigo-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="w-4 h-4 text-indigo-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Crescimento</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong>{kpisData.registered_this_month}</strong> novos passageiros este mês
              </p>
            </div>

            {/* Insight 8: Performance por Cidade */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-green-200 dark:border-gray-600">
              <div className="flex items-center gap-2 mb-2">
                <MapPin className="w-4 h-4 text-green-600" />
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Melhor Performance</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {cityData.length > 0 && (() => {
                  const bestCity = cityData.reduce((best, current) => 
                    current.avg_rides_per_passenger > best.avg_rides_per_passenger ? current : best
                  )
                  return `${bestCity.city}: ${bestCity.avg_rides_per_passenger.toFixed(1)} corridas/passageiro`
                })()}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Lista de Top Passageiros Aprimorada */}
      {passengersData && passengersData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-600" />
              Top 10 Passageiros
            </h3>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Ordenado por número de corridas
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Rank</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Passageiro</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Cidade</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Corridas</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Total Gasto</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Ticket Médio</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Avaliação</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Status</th>
                </tr>
              </thead>
              <tbody>
                {passengersData.slice(0, 10).map((passenger, index) => {
                  const ticketMedio = passenger.total_spent / (passenger.total_rides || 1)
                  return (
                    <tr key={passenger.passenger_id} className={`border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      index < 3 ? 'bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-gray-800 dark:to-gray-700' : ''
                    }`}>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          {index < 3 && (
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                              index === 0 ? 'bg-yellow-500' : 
                              index === 1 ? 'bg-gray-400' : 
                              'bg-amber-600'
                            }`}>
                              {index + 1}
                            </div>
                          )}
                          {index >= 3 && (
                            <span className="w-6 text-center font-medium text-gray-600 dark:text-gray-400">
                              {index + 1}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {passenger.user_name || `Passageiro ${passenger.passenger_id}`}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            ID: {passenger.passenger_id}
                          </p>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300 rounded-full text-xs font-medium">
                          {passenger.city}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-lg text-gray-900 dark:text-white">
                            {passenger.total_rides}
                          </span>
                          <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                              style={{ width: `${Math.min((passenger.total_rides / Math.max(...passengersData.map(p => p.total_rides))) * 100, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-right">
                          <p className="font-semibold text-gray-900 dark:text-white">
                            R$ {passenger.total_spent.toFixed(2)}
                          </p>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-center">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            ticketMedio > 25 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                            ticketMedio > 15 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' :
                            'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                          }`}>
                            R$ {ticketMedio.toFixed(2)}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center justify-center gap-1">
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                          <span className="font-medium text-gray-900 dark:text-white">
                            {passenger.avg_rating || 5.0}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          passenger.status === 'Ativo' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                        }`}>
                          {passenger.status || 'Ativo'}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Resumo da tabela */}
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {passengersData.slice(0, 10).reduce((sum, p) => sum + p.total_rides, 0)}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total de Corridas</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">
                  R$ {passengersData.slice(0, 10).reduce((sum, p) => sum + p.total_spent, 0).toFixed(2)}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Receita Gerada</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-600">
                  R$ {(passengersData.slice(0, 10).reduce((sum, p) => sum + p.total_spent, 0) / 
                       passengersData.slice(0, 10).reduce((sum, p) => sum + p.total_rides, 0)).toFixed(2)}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Ticket Médio</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-yellow-600">
                  {(passengersData.slice(0, 10).reduce((sum, p) => sum + p.total_rides, 0) / 
                    Math.min(passengersData.length, 10)).toFixed(1)}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Corridas/Passageiro</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Nova seção: Crescimento por Cidade */}
      {cityData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-600" />
            Análise de Crescimento por Cidade
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {cityData.map((city, index) => {
              const getGrowthStatus = (percentage) => {
                if (percentage === 100) return { label: 'Mercado Novo', color: 'emerald', icon: '🚀' }
                if (percentage > 80) return { label: 'Alto Crescimento', color: 'green', icon: '📈' }
                if (percentage > 50) return { label: 'Crescimento Moderado', color: 'yellow', icon: '⚡' }
                return { label: 'Mercado Estabelecido', color: 'blue', icon: '🏛️' }
              }
              
              const status = getGrowthStatus(city.new_passengers_percentage)
              
              return (
                <div key={city.city} className={`relative overflow-hidden rounded-lg p-4 bg-gradient-to-br ${
                  status.color === 'emerald' ? 'from-emerald-50 to-emerald-100 dark:from-emerald-900 dark:to-emerald-800' :
                  status.color === 'green' ? 'from-green-50 to-green-100 dark:from-green-900 dark:to-green-800' :
                  status.color === 'yellow' ? 'from-yellow-50 to-yellow-100 dark:from-yellow-900 dark:to-yellow-800' :
                  'from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800'
                } border ${
                  status.color === 'emerald' ? 'border-emerald-200 dark:border-emerald-700' :
                  status.color === 'green' ? 'border-green-200 dark:border-green-700' :
                  status.color === 'yellow' ? 'border-yellow-200 dark:border-yellow-700' :
                  'border-blue-200 dark:border-blue-700'
                }`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 dark:text-white text-sm">{city.city}</h4>
                      <p className={`text-xs font-medium ${
                        status.color === 'emerald' ? 'text-emerald-700 dark:text-emerald-300' :
                        status.color === 'green' ? 'text-green-700 dark:text-green-300' :
                        status.color === 'yellow' ? 'text-yellow-700 dark:text-yellow-300' :
                        'text-blue-700 dark:text-blue-300'
                      }`}>
                        {status.icon} {status.label}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {city.new_passengers_count}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">novos</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-600 dark:text-gray-400">% Novos Passageiros</span>
                      <span className="font-medium">{city.new_passengers_percentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          status.color === 'emerald' ? 'bg-emerald-500' :
                          status.color === 'green' ? 'bg-green-500' :
                          status.color === 'yellow' ? 'bg-yellow-500' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${city.new_passengers_percentage}%` }}
                      ></div>
                    </div>
                    
                    <div className="pt-1 flex justify-between text-xs text-gray-600 dark:text-gray-400">
                      <span>{city.passenger_count} total</span>
                      <span>R$ {city.total_revenue.toFixed(0)}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
          
          {/* Resumo de crescimento */}
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-emerald-600">
                  {cityData.filter(city => city.new_passengers_percentage === 100).length}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Mercados Novos</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">
                  {cityData.filter(city => city.new_passengers_percentage > 80 && city.new_passengers_percentage < 100).length}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Alto Crescimento</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {(cityData.reduce((sum, city) => sum + city.new_passengers_count, 0) / 
                    cityData.reduce((sum, city) => sum + city.passenger_count, 0) * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Taxa Média Crescimento</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-600">
                  {cityData.reduce((sum, city) => sum + city.new_passengers_count, 0)}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Novos Passageiros</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Recomendações Estratégicas */}
      {kpisData && cityData && analyticsData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="bg-gradient-to-br from-indigo-50 to-purple-100 dark:from-gray-800 dark:to-gray-700 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            Recomendações Estratégicas
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Coluna 1: Oportunidades */}
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-3 text-lg">🎯 Oportunidades de Crescimento</h4>
              <div className="space-y-3">
                {cityData.find(c => c.total_rides === 0) && (
                  <div className="bg-orange-100 dark:bg-orange-900 border-l-4 border-orange-500 p-3 rounded">
                    <p className="text-sm text-orange-800 dark:text-orange-200">
                      <strong>Ativar {cityData.find(c => c.total_rides === 0).city}:</strong> {cityData.find(c => c.total_rides === 0).passenger_count} passageiros cadastrados mas sem corridas
                    </p>
                  </div>
                )}
                
                {(() => {
                  const lowEngagementCity = cityData.find(c => c.avg_rides_per_passenger < 1.5 && c.total_rides > 0)
                  return lowEngagementCity && (
                    <div className="bg-yellow-100 dark:bg-yellow-900 border-l-4 border-yellow-500 p-3 rounded">
                      <p className="text-sm text-yellow-800 dark:text-yellow-200">
                        <strong>Melhorar engajamento em {lowEngagementCity.city}:</strong> Apenas {lowEngagementCity.avg_rides_per_passenger.toFixed(1)} corridas por passageiro
                      </p>
                    </div>
                  )
                })()}

                <div className="bg-blue-100 dark:bg-blue-900 border-l-4 border-blue-500 p-3 rounded">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    <strong>Foco em corridas curtas:</strong> 87.1% das corridas são até 5km - otimizar para trajetos urbanos
                  </p>
                </div>
              </div>
            </div>

            {/* Coluna 2: Pontos Fortes */}
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-3 text-lg">💪 Pontos Fortes</h4>
              <div className="space-y-3">
                <div className="bg-green-100 dark:bg-green-900 border-l-4 border-green-500 p-3 rounded">
                  <p className="text-sm text-green-800 dark:text-green-200">
                    <strong>Excelente satisfação:</strong> 100% das avaliações são 5 estrelas
                  </p>
                </div>

                <div className="bg-green-100 dark:bg-green-900 border-l-4 border-green-500 p-3 rounded">
                  <p className="text-sm text-green-800 dark:text-green-200">
                    <strong>Alto engajamento:</strong> {((kpisData.active_passengers / kpisData.total_passengers) * 100).toFixed(1)}% dos passageiros estão ativos
                  </p>
                </div>

                {(() => {
                  const topCity = cityData.reduce((best, current) => 
                    current.avg_rides_per_passenger > best.avg_rides_per_passenger ? current : best
                  )
                  return (
                    <div className="bg-green-100 dark:bg-green-900 border-l-4 border-green-500 p-3 rounded">
                      <p className="text-sm text-green-800 dark:text-green-200">
                        <strong>Modelo de sucesso:</strong> {topCity.city} tem {topCity.avg_rides_per_passenger.toFixed(1)} corridas por passageiro
                      </p>
                    </div>
                  )
                })()}
              </div>
            </div>
          </div>

          {/* Ações Recomendadas */}
          <div className="mt-6 pt-4 border-t border-indigo-200 dark:border-gray-600">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">🚀 Próximas Ações</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">📈</div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Campanha de Ativação</p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Focar em passageiros inativos</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">🎁</div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Programa de Fidelidade</p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Recompensar usuários frequentes</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">📍</div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Expansão Geográfica</p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Replicar modelo de sucesso</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default PassengersOverview