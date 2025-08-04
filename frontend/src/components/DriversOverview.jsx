import { useState, useEffect } from 'react'
import { Users, Star, TrendingUp, UserCheck, UserX, Activity, Award, AlertTriangle, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: '7 dias', value: '7d' },
  { label: '30 dias', value: '30d' },
]

export function DriversOverview({ data, loading = false, onPeriodChange }) {
  // Garante que data nunca será null/undefined
  const safeData = data || {};
  const [period, setPeriod] = useState('30d')

  // Dados padrão caso não venha da API
  const driversData = safeData || {
    total_drivers: 0,
    active_drivers: 0,
    inactive_drivers: 0,
    online_drivers: 0,
    average_rating: 0,
    total_rides_completed: 0,
    avg_rides_per_driver: 0,
    top_drivers: [],
    drivers_by_status: {},
    performance_metrics: {
      excellent_drivers: 0,
      good_drivers: 0,
      average_drivers: 0,
      below_average_drivers: 0
    },
    periodo_dias: 30
  }

  // Calcular KPIs avançados com verificações de segurança
  const kpis = {
    activationRate: driversData?.total_drivers > 0 ? (driversData.active_drivers / driversData.total_drivers) * 100 : 0,
    onlineRate: driversData?.active_drivers > 0 ? ((driversData.online_drivers || 0) / driversData.active_drivers) * 100 : 0,
    excellenceRate: driversData?.total_drivers > 0 ? ((driversData?.performance_metrics?.excellent_drivers || 0) / driversData.total_drivers) * 100 : 0,
    avgRatingTrend: (driversData?.average_rating || 0) >= 4.0 ? 'positive' : (driversData?.average_rating || 0) >= 3.5 ? 'neutral' : 'negative',
    performanceDistribution: {
      excellent: driversData?.performance_metrics?.excellent_drivers || 0,
      good: driversData?.performance_metrics?.good_drivers || 0,
      average: driversData?.performance_metrics?.average_drivers || 0,
      below: driversData?.performance_metrics?.below_average_drivers || 0
    }
  }

  // Dispara callback para buscar dados ao trocar período
  const handlePeriodChange = (e) => {
    const newPeriod = e.target.value
    setPeriod(newPeriod)
    if (onPeriodChange) onPeriodChange(newPeriod)
  }

  // Função para gerar avatar
  const getAvatarUrl = (name) => {
    if (!name) return "https://ui-avatars.com/api/?name=User&background=random"
    const cleanName = name.replace("Motorista ", "").replace(" ", "+")
    return `https://ui-avatars.com/api/?name=${cleanName}&background=random`
  }

  // Função para determinar cor baseada no valor com melhor contraste
  const getKpiColor = (value, thresholds = { good: 80, average: 60 }) => {
    if (value >= thresholds.good) return 'text-green-700 dark:text-green-400'
    if (value >= thresholds.average) return 'text-yellow-700 dark:text-yellow-400'
    return 'text-red-700 dark:text-red-400'
  }

  // Função para cores de fundo dos KPIs
  const getKpiBackgroundColor = (value, thresholds = { good: 80, average: 60 }) => {
    if (value >= thresholds.good) return 'from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20'
    if (value >= thresholds.average) return 'from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20'
    return 'from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20'
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-8 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
      {/* Header com filtro de período e resumo executivo */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-200 dark:border-gray-700">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl">
              <Users className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              Gestão de Motoristas
            </h1>
          </div>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
            Dashboard executivo com KPIs e métricas de performance dos motoristas
          </p>
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
              <Clock className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="font-medium text-blue-700 dark:text-blue-300">
                Período: {period === 'hoje' ? '24 horas' : period === '7d' ? '7 dias' : '30 dias'}
              </span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-green-50 dark:bg-green-900/30 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="font-medium text-green-700 dark:text-green-300">
                Atualizado: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex gap-3">
          {periodOptions.map(opt => (
            <button
              key={opt.value}
              type="button"
              className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg
                ${period === opt.value 
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white border-2 border-blue-500 shadow-blue-200 dark:shadow-blue-800' 
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                }`}
              onClick={() => handlePeriodChange({ target: { value: opt.value } })}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700">
              <CardContent className="p-8">
                <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg w-24 mb-4"></div>
                <div className="h-10 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg w-20 mb-3"></div>
                <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg w-32"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <>
          {/* KPIs principais com tendências e contexto */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            {/* Total Motoristas */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-2xl shadow-xl border border-blue-100 dark:border-blue-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Total de Motoristas</CardTitle>
                <div className="p-2 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg">
                  <Users className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{driversData.total_drivers || 0}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  Cadastrados na plataforma
                </p>
              </CardContent>
            </Card>

            {/* Motoristas Ativos */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-green-50 dark:from-gray-800 dark:to-green-900/20 rounded-2xl shadow-xl border border-green-100 dark:border-green-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Motoristas Ativos</CardTitle>
                <div className="p-2 bg-gradient-to-r from-green-500 to-green-600 rounded-xl shadow-lg">
                  <UserCheck className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">{driversData.active_drivers || 0}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  {kpis.activationRate.toFixed(1)}% do total
                </p>
              </CardContent>
            </Card>

            {/* Motoristas Online */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-emerald-50 dark:from-gray-800 dark:to-emerald-900/20 rounded-2xl shadow-xl border border-emerald-100 dark:border-emerald-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Motoristas Online</CardTitle>
                <div className="p-2 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-xl shadow-lg relative">
                  <Activity className="h-4 w-4 text-white" />
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mb-2">{driversData.online_drivers || 0}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                  {kpis.onlineRate.toFixed(1)}% dos ativos
                </p>
              </CardContent>
            </Card>

            {/* Avaliação Média com Tendência */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-yellow-50 dark:from-gray-800 dark:to-yellow-900/20 rounded-2xl shadow-xl border border-yellow-100 dark:border-yellow-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Avaliação Média</CardTitle>
                <div className="flex items-center gap-1">
                  <div className="p-2 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl shadow-lg">
                    <Star className="h-4 w-4 text-white fill-current" />
                  </div>
                  {kpis.avgRatingTrend === 'positive' && <TrendingUp className="h-3 w-3 text-green-500" />}
                  {kpis.avgRatingTrend === 'negative' && <AlertTriangle className="h-3 w-3 text-red-500" />}
                </div>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold mb-2 ${
                  kpis.avgRatingTrend === 'positive' ? 'text-green-600 dark:text-green-400' :
                  kpis.avgRatingTrend === 'neutral' ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'
                }`}>
                  {(driversData.average_rating || 0).toFixed(1)}
                </div>
                <div className="flex items-center gap-1">
                  {[1,2,3,4,5].map(star => (
                    <Star 
                      key={star} 
                      className={`h-3 w-3 transition-all duration-300 ${
                        star <= (driversData.average_rating || 0) 
                          ? 'text-yellow-400 fill-current drop-shadow-sm' 
                          : 'text-gray-300 dark:text-gray-600'
                      }`} 
                    />
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Taxa de Excelência */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-purple-50 dark:from-gray-800 dark:to-purple-900/20 rounded-2xl shadow-xl border border-purple-100 dark:border-purple-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Taxa de Excelência</CardTitle>
                <div className="p-2 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl shadow-lg">
                  <Award className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold mb-2 ${getKpiColor(kpis.excellenceRate)}`}>
                  {kpis.excellenceRate.toFixed(1)}%
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  {driversData?.performance_metrics?.excellent_drivers || 0} com nota ≥ 4.5
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Métricas Operacionais */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-2xl shadow-xl border border-blue-100 dark:border-blue-800">
              <CardHeader className="border-b border-blue-100 dark:border-blue-800 pb-4">
                <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                  <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg">
                    <Clock className="h-6 w-6 text-white" />
                  </div>
                  Métricas Operacionais
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6 pt-6">
                <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Corridas Completadas</span>
                  <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">{driversData.total_rides_completed || 0}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Média por Motorista</span>
                  <span className="text-2xl font-bold text-green-600 dark:text-green-400">{(driversData.avg_rides_per_driver || 0).toFixed(1)}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Período de Análise</span>
                  <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">{driversData.periodo_dias || 0} dias</span>
                </div>
              </CardContent>
            </Card>

            {/* Distribuição por Status */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-green-50 dark:from-gray-800 dark:to-green-900/20 rounded-2xl shadow-xl border border-green-100 dark:border-green-800">
              <CardHeader className="border-b border-green-100 dark:border-green-800 pb-4">
                <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                  <div className="p-3 bg-gradient-to-r from-green-500 to-green-600 rounded-xl shadow-lg">
                    <UserCheck className="h-6 w-6 text-white" />
                  </div>
                  Distribuição por Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6 pt-6">
                <div className="flex justify-between items-center p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-3">
                    <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-green-600 rounded-full shadow-lg"></div>
                    Ativos
                  </span>
                  <span className="text-2xl font-bold text-green-600 dark:text-green-400">{driversData.active_drivers || 0}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-xl">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-3">
                    <div className="w-4 h-4 bg-gradient-to-r from-red-500 to-red-600 rounded-full shadow-lg"></div>
                    Inativos
                  </span>
                  <span className="text-2xl font-bold text-red-600 dark:text-red-400">{driversData.inactive_drivers || 0}</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden shadow-inner">
                  <div 
                    className="h-4 bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-1000 ease-out shadow-lg"
                    style={{ 
                      width: `${driversData.total_drivers > 0 ? (driversData.active_drivers / driversData.total_drivers) * 100 : 0}%` 
                    }}
                  ></div>
                </div>
              </CardContent>
            </Card>

            {/* Distribuição de Performance */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-purple-50 dark:from-gray-800 dark:to-purple-900/20 rounded-2xl shadow-xl border border-purple-100 dark:border-purple-800">
              <CardHeader className="border-b border-purple-100 dark:border-purple-800 pb-4">
                <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                  <div className="p-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl shadow-lg">
                    <TrendingUp className="h-6 w-6 text-white" />
                  </div>
                  Performance dos Motoristas
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-6">
                {[
                  { label: 'Excelente (≥4.5)', value: kpis.performanceDistribution.excellent, color: 'from-green-500 to-green-600', bgColor: 'from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20', textColor: 'text-green-600 dark:text-green-400' },
                  { label: 'Bom (4.0-4.4)', value: kpis.performanceDistribution.good, color: 'from-blue-500 to-blue-600', bgColor: 'from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20', textColor: 'text-blue-600 dark:text-blue-400' },
                  { label: 'Médio (3.5-3.9)', value: kpis.performanceDistribution.average, color: 'from-yellow-500 to-yellow-600', bgColor: 'from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20', textColor: 'text-yellow-600 dark:text-yellow-400' },
                  { label: 'Abaixo (< 3.5)', value: kpis.performanceDistribution.below, color: 'from-red-500 to-red-600', bgColor: 'from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20', textColor: 'text-red-600 dark:text-red-400' }
                ].map((item, index) => (
                  <div key={index} className={`flex justify-between items-center p-4 bg-gradient-to-r ${item.bgColor} rounded-xl`}>
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-3">
                      <div className={`w-3 h-3 bg-gradient-to-r ${item.color} rounded-full shadow-lg`}></div>
                      {item.label}
                    </span>
                    <span className={`text-xl font-bold ${item.textColor}`}>{item.value || 0}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Top Motoristas e Performance */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Top 5 Motoristas */}
            <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-yellow-50 dark:from-gray-800 dark:to-yellow-900/20 rounded-2xl shadow-xl border border-yellow-100 dark:border-yellow-800">
              <CardHeader className="border-b border-yellow-100 dark:border-yellow-800 pb-4">
                <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                  <div className="p-3 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl shadow-lg">
                    <Star className="h-6 w-6 text-white fill-current" />
                  </div>
                  Top Motoristas
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {driversData.top_drivers?.length > 0 ? driversData.top_drivers.map((driver, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-white to-yellow-50 dark:from-gray-700 dark:to-yellow-900/20 rounded-xl shadow-md border border-yellow-100 dark:border-yellow-800 hover:shadow-lg transition-all duration-300">
                      <div className="flex items-center gap-4">
                        <div className="relative">
                          <img 
                            src={getAvatarUrl(driver.name)} 
                            alt={driver.name}
                            className="w-12 h-12 rounded-full shadow-lg border-2 border-yellow-200 dark:border-yellow-700"
                          />
                          <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-lg">
                            {index + 1}
                          </div>
                        </div>
                        <div>
                          <p className="font-bold text-gray-900 dark:text-white text-lg">
                            {driver.name.replace("Motorista ", "")}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            {driver.total_rides} corridas realizadas
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-2 mb-2">
                          <Star className="h-5 w-5 text-yellow-500 fill-current drop-shadow-sm" />
                          <span className="text-2xl font-bold text-gray-900 dark:text-white">
                            {driver.rating ? driver.rating.toFixed(1) : '0.0'}
                          </span>
                        </div>
                        <span className={`text-xs px-3 py-1 rounded-full font-semibold shadow-md ${
                          driver.status === 'active' 
                            ? 'bg-gradient-to-r from-green-100 to-green-200 text-green-800 border border-green-300' 
                            : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800 border border-gray-300'
                        }`}>
                          {driver.status === 'active' ? '🟢 Ativo' : '🔴 Inativo'}
                        </span>
                      </div>
                    </div>
                  )) : (
                    <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                      <Star className="h-12 w-12 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                      <p className="text-lg font-medium">Nenhum motorista encontrado</p>
                      <p className="text-sm">Ajuste o período de análise para ver dados</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Métricas de Performance Visual */}
            <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-2xl shadow-xl border border-blue-100 dark:border-blue-800">
              <CardHeader className="border-b border-blue-100 dark:border-blue-800 pb-4">
                <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                  <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg">
                    <TrendingUp className="h-6 w-6 text-white" />
                  </div>
                  Performance Visual
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Excelentes (≥4.5) ⭐⭐⭐⭐⭐</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                        <div 
                          className="h-3 bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-1000 ease-out shadow-lg" 
                          style={{ 
                            width: `${driversData?.total_drivers > 0 ? ((driversData?.performance_metrics?.excellent_drivers || 0) / driversData.total_drivers) * 100 : 0}%` 
                          }}
                        ></div>
                      </div>
                      <span className="text-xl font-bold text-green-600 dark:text-green-400 min-w-[2rem]">
                        {driversData?.performance_metrics?.excellent_drivers || 0}
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Bons (4.0-4.5) ⭐⭐⭐⭐</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                        <div 
                          className="h-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-1000 ease-out shadow-lg" 
                          style={{ 
                            width: `${driversData?.total_drivers > 0 ? ((driversData?.performance_metrics?.good_drivers || 0) / driversData.total_drivers) * 100 : 0}%` 
                          }}
                        ></div>
                      </div>
                      <span className="text-xl font-bold text-blue-600 dark:text-blue-400 min-w-[2rem]">
                        {driversData?.performance_metrics?.good_drivers || 0}
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Médios (3.5-3.9) ⭐⭐⭐</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                        <div 
                          className="h-3 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-full transition-all duration-1000 ease-out shadow-lg" 
                          style={{ 
                            width: `${driversData?.total_drivers > 0 ? ((driversData?.performance_metrics?.average_drivers || 0) / driversData.total_drivers) * 100 : 0}%` 
                          }}
                        ></div>
                      </div>
                      <span className="text-xl font-bold text-yellow-600 dark:text-yellow-400 min-w-[2rem]">
                        {driversData?.performance_metrics?.average_drivers || 0}
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Abaixo (&lt; 3.5) ⭐⭐</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                        <div 
                          className="h-3 bg-gradient-to-r from-red-500 to-red-600 rounded-full transition-all duration-1000 ease-out shadow-lg" 
                          style={{ 
                            width: `${driversData?.total_drivers > 0 ? ((driversData?.performance_metrics?.below_average_drivers || 0) / driversData.total_drivers) * 100 : 0}%` 
                          }}
                        ></div>
                      </div>
                      <span className="text-xl font-bold text-red-600 dark:text-red-400 min-w-[2rem]">
                        {driversData?.performance_metrics?.below_average_drivers || 0}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Status dos Motoristas - Resumo Final */}
          <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700">
            <CardHeader className="border-b border-gray-200 dark:border-gray-700 pb-6">
              <CardTitle className="text-2xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                <div className="p-4 bg-gradient-to-r from-gray-600 to-gray-700 rounded-xl shadow-lg">
                  <Users className="h-7 w-7 text-white" />
                </div>
                Resumo Geral por Status
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {Object.entries(driversData.drivers_by_status).map(([status, count]) => (
                  <div key={status} className="text-center p-6 bg-gradient-to-br from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                    <div className="text-4xl font-bold text-gray-900 dark:text-white mb-2">{count}</div>
                    <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 capitalize mb-3">
                      {status === 'ativo' ? '🟢 Motoristas Ativos' : 
                       status === 'inativo' ? '🔴 Motoristas Inativos' : 
                       status === 'active' ? '🟢 Ativos' : 
                       status === 'inactive' ? '🔴 Inativos' : status}
                    </div>
                    <div className={`w-full h-2 rounded-full ${
                      status === 'ativo' || status === 'active' ? 'bg-gradient-to-r from-green-500 to-green-600' : 
                      'bg-gradient-to-r from-red-500 to-red-600'
                    } shadow-inner`}></div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
