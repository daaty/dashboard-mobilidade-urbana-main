import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Target, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

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
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-2">
          <Target className="w-6 h-6 text-gray-700 dark:text-gray-300" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Metas por Cidade</h2>
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

