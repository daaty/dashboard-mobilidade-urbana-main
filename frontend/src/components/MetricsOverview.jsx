import { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, AlertCircle, MessageCircle, TrendingUp } from 'lucide-react'

const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: '7d', value: '7d' },
  { label: '30d', value: '30d' },
]

export function MetricsOverview({ data, loading = false, onPeriodChange }) {
  // Garante que data nunca será null/undefined
  const safeData = data || {};
  const [period, setPeriod] = useState('7d')

  // Simulação de dados caso não venha da API
  const metricas = safeData.metricas_principais || {
    corridas_concluidas: 0,
    corridas_canceladas: 0,
    corridas_perdidas: 0,
    variacao_concluidas: 0,
    variacao_canceladas: 0,
    variacao_perdidas: 0,
  }
  const atividadeRecente = safeData.atividade_recente || {
    concluidas: [],
    canceladas: [],
    perdidas: []
  }

  // Dispara callback para buscar dados ao trocar período
  const handlePeriodChange = (e) => {
    setPeriod(e.target.value)
    if (onPeriodChange) onPeriodChange(e.target.value)
  }


  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="w-full max-w-7xl mx-auto space-y-8">
        {/* Header com filtro de período */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Visão Geral
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Acompanhe as principais métricas do sistema
            </p>
          </div>
          
          {/* Filtro de período */}
          <div className="flex gap-2">
            {periodOptions.map(opt => (
              <button
                key={opt.value}
                type="button"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  period === opt.value
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-blue-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => {
                  setPeriod(opt.value);
                  if (onPeriodChange) onPeriodChange(opt.value);
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* KPIs principais */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Corridas Concluídas</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {metricas.corridas_concluidas.toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              {metricas.variacao_concluidas >= 0 ? (
                <TrendingUp className="w-4 h-4 mr-1 text-green-600" />
              ) : (
                <TrendingUp className="w-4 h-4 mr-1 text-red-600 rotate-180" />
              )}
              <span className={`text-sm ${
                metricas.variacao_concluidas >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {metricas.variacao_concluidas >= 0 ? '+' : ''}{metricas.variacao_concluidas}% vs período anterior
              </span>
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
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Corridas Canceladas</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {metricas.corridas_canceladas.toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              {metricas.variacao_canceladas >= 0 ? (
                <TrendingUp className="w-4 h-4 mr-1 text-red-600" />
              ) : (
                <TrendingUp className="w-4 h-4 mr-1 text-green-600 rotate-180" />
              )}
              <span className={`text-sm ${
                metricas.variacao_canceladas >= 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {metricas.variacao_canceladas >= 0 ? '+' : ''}{metricas.variacao_canceladas}% vs período anterior
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
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Corridas Perdidas</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {metricas.corridas_perdidas.toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              {metricas.variacao_perdidas >= 0 ? (
                <TrendingUp className="w-4 h-4 mr-1 text-red-600" />
              ) : (
                <TrendingUp className="w-4 h-4 mr-1 text-green-600 rotate-180" />
              )}
              <span className={`text-sm ${
                metricas.variacao_perdidas >= 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {metricas.variacao_perdidas >= 0 ? '+' : ''}{metricas.variacao_perdidas}% vs período anterior
              </span>
            </div>
          </motion.div>
        </div>

        {/* Bloco de Atividade Recente */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Atividade Recente</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Corridas Concluídas */}
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-3 rounded-t-lg font-semibold flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Últimas 3 Concluídas
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-b-lg p-4 space-y-4">
                {atividadeRecente.concluidas.map((corrida, idx) => (
                  <div key={idx} className="flex gap-3 items-start border-b border-gray-200 dark:border-gray-600 last:border-b-0 pb-3 last:pb-0">
                    <img src={corrida.avatar} alt={corrida.nome} className="w-10 h-10 rounded-full object-cover" />
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-gray-900 dark:text-white">{corrida.nome}</span>
                        <span className="text-green-600 font-medium text-sm">{corrida.hora}</span>
                      </div>
                      <a 
                        href={`https://wa.me/${corrida.grupo.replace(/\+/g, '')}`} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-sm text-green-600 hover:text-green-700 underline flex items-center gap-1 mt-1"
                      >
                        <MessageCircle className="w-3 h-3" />
                        {corrida.grupo}
                      </a>
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{corrida.local}</div>
                      <div className="text-xs font-medium text-gray-700 dark:text-gray-300">{corrida.destino}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{corrida.cidade} • {corrida.tempo}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Corridas Canceladas */}
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-3 rounded-t-lg font-semibold flex items-center gap-2">
                <XCircle className="w-5 h-5" />
                Últimas 3 Canceladas
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-b-lg p-4 space-y-4">
                {atividadeRecente.canceladas.map((corrida, idx) => (
                  <div key={idx} className="flex gap-3 items-start border-b border-gray-200 dark:border-gray-600 last:border-b-0 pb-3 last:pb-0">
                    <img src={corrida.avatar} alt={corrida.nome} className="w-10 h-10 rounded-full object-cover" />
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-gray-900 dark:text-white">{corrida.nome}</span>
                        <span className="text-red-600 font-medium text-sm">{corrida.hora}</span>
                      </div>
                      <a 
                        href={`https://wa.me/${corrida.grupo.replace(/\+/g, '')}`} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-sm text-green-600 hover:text-green-700 underline flex items-center gap-1 mt-1"
                      >
                        <MessageCircle className="w-3 h-3" />
                        {corrida.grupo}
                      </a>
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{corrida.local}</div>
                      <div className="text-xs font-medium text-red-600 dark:text-red-400">{corrida.motivo}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Corridas Perdidas */}
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white px-4 py-3 rounded-t-lg font-semibold flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Últimas 3 Perdidas
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-b-lg p-4 space-y-4">
                {atividadeRecente.perdidas.map((corrida, idx) => (
                  <div key={idx} className="flex gap-3 items-start border-b border-gray-200 dark:border-gray-600 last:border-b-0 pb-3 last:pb-0">
                    <img src={corrida.avatar} alt={corrida.nome} className="w-10 h-10 rounded-full object-cover" />
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-gray-900 dark:text-white">{corrida.nome}</span>
                        <span className="text-yellow-600 font-medium text-sm">{corrida.hora}</span>
                      </div>
                      <a 
                        href={`https://wa.me/${corrida.grupo.replace(/\+/g, '')}`} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-sm text-green-600 hover:text-green-700 underline flex items-center gap-1 mt-1"
                      >
                        <MessageCircle className="w-3 h-3" />
                        {corrida.grupo}
                      </a>
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{corrida.local}</div>
                      <div className="text-xs font-medium text-yellow-600 dark:text-yellow-400">{corrida.motivo}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

