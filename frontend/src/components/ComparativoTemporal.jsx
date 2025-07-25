import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { TrendingUp, Calendar, BarChart3, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/tabs'
import { Button } from '@/components/ui/button'

const COLORS = {
  concluidas: '#10B981',
  canceladas: '#EF4444',
  perdidas: '#F59E0B',
  total: '#3B82F6'
}

export function ComparativoTemporal() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [periodo, setPeriodo] = useState('7dias')

  useEffect(() => {
    fetchComparativoTemporal()
  }, [periodo])

  const fetchComparativoTemporal = async () => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:5002/api/metrics/comparativo-temporal?periodo=${periodo}`)
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Erro ao buscar comparativo temporal:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePeriodoChange = (novoPeriodo) => {
    setPeriodo(novoPeriodo)
  }

  const getPeriodoLabel = (periodo) => {
    switch (periodo) {
      case '7dias':
        return 'Últimos 7 Dias'
      case '4semanas':
        return 'Últimas 4 Semanas'
      case '6meses':
        return 'Últimos 6 Meses'
      default:
        return 'Período'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-6 h-6 text-gray-400" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Comparativo Temporal</h2>
          </div>
          <div className="flex space-x-2">
            {['7dias', '4semanas', '6meses'].map((p) => (
              <div key={p} className="h-8 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
            ))}
          </div>
        </div>
        
        <div className="space-y-6">
          <Card className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
            </CardHeader>
            <CardContent>
              <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-6 h-6 text-gray-700 dark:text-gray-300" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Comparativo Temporal</h2>
        </div>
        
        {/* Period Selector */}
        <div className="flex space-x-2">
          {[
            { key: '7dias', label: '7 Dias' },
            { key: '4semanas', label: '4 Semanas' },
            { key: '6meses', label: '6 Meses' }
          ].map((p) => (
            <Button
              key={p.key}
              variant={periodo === p.key ? "default" : "outline"}
              size="sm"
              onClick={() => handlePeriodoChange(p.key)}
              className={periodo === p.key ? "bg-black text-white hover:bg-gray-800" : ""}
            >
              {p.label}
            </Button>
          ))}
        </div>
      </motion.div>

      {/* Current Period Display */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400"
      >
        <Calendar className="w-4 h-4" />
        <span>Visualizando: {getPeriodoLabel(periodo)}</span>
      </motion.div>

      {/* Charts */}
      <Tabs defaultValue="linha" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="linha">Gráfico de Linha</TabsTrigger>
          <TabsTrigger value="area">Gráfico de Área</TabsTrigger>
          <TabsTrigger value="barras">Gráfico de Barras</TabsTrigger>
        </TabsList>

        <TabsContent value="linha" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="w-5 h-5" />
                  <span>Tendência de Corridas - {getPeriodoLabel(periodo)}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart
                    data={data?.dados || []}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis 
                      dataKey={periodo === '7dias' ? 'data' : periodo === '4semanas' ? 'semana' : 'mes'} 
                      stroke="#6B7280"
                      fontSize={12}
                    />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="concluidas" 
                      stroke={COLORS.concluidas} 
                      strokeWidth={3}
                      name="Concluídas"
                      dot={{ fill: COLORS.concluidas, strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="canceladas" 
                      stroke={COLORS.canceladas} 
                      strokeWidth={3}
                      name="Canceladas"
                      dot={{ fill: COLORS.canceladas, strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="perdidas" 
                      stroke={COLORS.perdidas} 
                      strokeWidth={3}
                      name="Perdidas"
                      dot={{ fill: COLORS.perdidas, strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="area" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="w-5 h-5" />
                  <span>Distribuição de Corridas - {getPeriodoLabel(periodo)}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart
                    data={data?.dados || []}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis 
                      dataKey={periodo === '7dias' ? 'data' : periodo === '4semanas' ? 'semana' : 'mes'} 
                      stroke="#6B7280"
                      fontSize={12}
                    />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="concluidas"
                      stackId="1"
                      stroke={COLORS.concluidas}
                      fill={COLORS.concluidas}
                      fillOpacity={0.8}
                      name="Concluídas"
                    />
                    <Area
                      type="monotone"
                      dataKey="canceladas"
                      stackId="1"
                      stroke={COLORS.canceladas}
                      fill={COLORS.canceladas}
                      fillOpacity={0.8}
                      name="Canceladas"
                    />
                    <Area
                      type="monotone"
                      dataKey="perdidas"
                      stackId="1"
                      stroke={COLORS.perdidas}
                      fill={COLORS.perdidas}
                      fillOpacity={0.8}
                      name="Perdidas"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="barras" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Comparativo de Corridas - {getPeriodoLabel(periodo)}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={data?.dados || []}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis 
                      dataKey={periodo === '7dias' ? 'data' : periodo === '4semanas' ? 'semana' : 'mes'} 
                      stroke="#6B7280"
                      fontSize={12}
                    />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                    />
                    <Legend />
                    <Bar 
                      dataKey="concluidas" 
                      fill={COLORS.concluidas} 
                      name="Concluídas"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar 
                      dataKey="canceladas" 
                      fill={COLORS.canceladas} 
                      name="Canceladas"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar 
                      dataKey="perdidas" 
                      fill={COLORS.perdidas} 
                      name="Perdidas"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>

      {/* Summary Statistics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {data?.dados && (
          <>
            <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-green-700 dark:text-green-300">
                    Média Concluídas
                  </span>
                </div>
                <div className="text-2xl font-bold text-green-600 mt-1">
                  {Math.round(data.dados.reduce((acc, item) => acc + item.concluidas, 0) / data.dados.length)}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-sm font-medium text-red-700 dark:text-red-300">
                    Média Canceladas
                  </span>
                </div>
                <div className="text-2xl font-bold text-red-600 mt-1">
                  {Math.round(data.dados.reduce((acc, item) => acc + item.canceladas, 0) / data.dados.length)}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                    Média Perdidas
                  </span>
                </div>
                <div className="text-2xl font-bold text-yellow-600 mt-1">
                  {Math.round(data.dados.reduce((acc, item) => acc + item.perdidas, 0) / data.dados.length)}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                    Total Período
                  </span>
                </div>
                <div className="text-2xl font-bold text-blue-600 mt-1">
                  {data.dados.reduce((acc, item) => acc + item.total, 0)}
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </motion.div>
    </div>
  )
}

