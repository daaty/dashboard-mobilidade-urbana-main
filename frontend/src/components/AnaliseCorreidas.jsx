import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { PieChart as PieChartIcon, BarChart3, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/tabs'

const COLORS = {
  primary: '#000000',
  secondary: '#6B7280',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6'
}

const RADIAN = Math.PI / 180
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)

  return (
    <text 
      x={x} 
      y={y} 
      fill="white" 
      textAnchor={x > cx ? 'start' : 'end'} 
      dominantBaseline="central"
      fontSize="12"
      fontWeight="bold"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

export function AnaliseCorreidas() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchAnaliseCorreidas()
  }, [])

  const fetchAnaliseCorreidas = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/metrics/analise-corridas`)
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Erro ao buscar análise de corridas:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDataForPieChart = (motivos) => {
    return Object.entries(motivos).map(([motivo, quantidade], index) => ({
      name: motivo,
      value: quantidade,
      color: Object.values(COLORS)[index % Object.values(COLORS).length]
    }))
  }

  const formatDataForBarChart = (motivosCancelamento, motivosPerda) => {
    const allMotivos = new Set([
      ...Object.keys(motivosCancelamento),
      ...Object.keys(motivosPerda)
    ])

    return Array.from(allMotivos).map(motivo => ({
      motivo: motivo.length > 15 ? motivo.substring(0, 15) + '...' : motivo,
      canceladas: motivosCancelamento[motivo] || 0,
      perdidas: motivosPerda[motivo] || 0
    }))
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-2">
          <PieChartIcon className="w-6 h-6 text-gray-400" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Análise de Corridas</h2>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500 dark:text-gray-400">Erro ao carregar dados de análise</p>
      </div>
    )
  }

  const cancelamentosData = formatDataForPieChart(data.motivos_cancelamento || {})
  const perdasData = formatDataForPieChart(data.motivos_perda || {})
  const comparativoData = formatDataForBarChart(data.motivos_cancelamento || {}, data.motivos_perda || {})

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-2"
      >
        <PieChartIcon className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Análise de Corridas</h2>
      </motion.div>

      {/* Tabs for different views */}
      <Tabs defaultValue="graficos" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="graficos">Gráficos de Pizza</TabsTrigger>
          <TabsTrigger value="comparativo">Comparativo</TabsTrigger>
        </TabsList>

        <TabsContent value="graficos" className="space-y-6">
          {/* Pie Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Cancelamentos */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <span>Motivos de Cancelamento</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={cancelamentosData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={renderCustomizedLabel}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {cancelamentosData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value, name) => [value, name]}
                        contentStyle={{
                          backgroundColor: 'rgba(0, 0, 0, 0.8)',
                          border: 'none',
                          borderRadius: '8px',
                          color: 'white'
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>

            {/* Perdas */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <span>Motivos de Perda</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={perdasData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={renderCustomizedLabel}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {perdasData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value, name) => [value, name]}
                        contentStyle={{
                          backgroundColor: 'rgba(0, 0, 0, 0.8)',
                          border: 'none',
                          borderRadius: '8px',
                          color: 'white'
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </TabsContent>

        <TabsContent value="comparativo" className="space-y-6">
          {/* Comparative Bar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Comparativo: Cancelamentos vs Perdas</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={comparativoData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis 
                      dataKey="motivo" 
                      stroke="#6B7280"
                      fontSize={12}
                      angle={-45}
                      textAnchor="end"
                      height={80}
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
                      dataKey="canceladas" 
                      fill={COLORS.danger} 
                      name="Canceladas"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar 
                      dataKey="perdidas" 
                      fill={COLORS.warning} 
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

      {/* Summary Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium text-red-700 dark:text-red-300">
                Total Cancelamentos
              </span>
            </div>
            <div className="text-2xl font-bold text-red-600 mt-1">
              {Object.values(data.motivos_cancelamento || {}).reduce((a, b) => a + b, 0)}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                Total Perdas
              </span>
            </div>
            <div className="text-2xl font-bold text-yellow-600 mt-1">
              {Object.values(data.motivos_perda || {}).reduce((a, b) => a + b, 0)}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                Tipos Cancelamento
              </span>
            </div>
            <div className="text-2xl font-bold text-blue-600 mt-1">
              {Object.keys(data.motivos_cancelamento || {}).length}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-sm font-medium text-purple-700 dark:text-purple-300">
                Tipos Perda
              </span>
            </div>
            <div className="text-2xl font-bold text-purple-600 mt-1">
              {Object.keys(data.motivos_perda || {}).length}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

