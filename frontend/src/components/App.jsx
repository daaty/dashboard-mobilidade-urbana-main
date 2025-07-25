import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { MetricsOverview } from './MetricsOverview'
import { MetasCidades } from './MetasCidades'
import { AnaliseCorreidas } from './AnaliseCorreidas'
import { ComparativoTemporal } from './ComparativoTemporal'
import { ConfiguracaoSheets } from './ConfiguracaoSheets'
import SistemaIA from './SistemaIA'
import RelatoriosExecutivos from './RelatoriosExecutivos'
import ImportacaoAvancada from './ImportacaoAvancada'
import { SistemaAlertas } from './SistemaAlertas'
import { ResumoPerformance } from './ResumoPerformance'
import '../App.css'


function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [metricsData, setMetricsData] = useState(null)
  const [performanceData, setPerformanceData] = useState(null)
  const [alertasData, setAlertasData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingPerformance, setLoadingPerformance] = useState(true)
  const [loadingAlertas, setLoadingAlertas] = useState(true)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchMetricsData()
    fetchPerformanceData()
    fetchAlertasData()
  }, [])

  const fetchMetricsData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/metrics/overview`)
      const data = await response.json()
      setMetricsData(data)
    } catch (error) {
      console.error('Erro ao buscar métricas:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPerformanceData = async () => {
    try {
      setLoadingPerformance(true)
      const response = await fetch(`${API_URL}/api/metrics/performance`)
      const data = await response.json()
      setPerformanceData(data)
    } catch (error) {
      console.error('Erro ao buscar performance:', error)
    } finally {
      setLoadingPerformance(false)
    }
  }

  const fetchAlertasData = async () => {
    try {
      setLoadingAlertas(true)
      const response = await fetch(`${API_URL}/api/metrics/alertas`)
      const data = await response.json()
      // Adaptar para o formato esperado pelo componente SistemaAlertas
      const mapped = data.map((item) => ({
        tipo: item.level === 'critical' ? 'crítico' : item.level === 'warning' ? 'aviso' : item.level === 'info' ? 'info' : 'sucesso',
        titulo: item.type.charAt(0).toUpperCase() + item.type.slice(1),
        mensagem: item.message,
        icone: null // O componente pode decidir o ícone pelo tipo
      }))
      setAlertasData({ alertas: mapped })
    } catch (error) {
      console.error('Erro ao buscar alertas:', error)
    } finally {
      setLoadingAlertas(false)
    }
  }

  const renderContent = () => {
    const contentVariants = {
      hidden: { opacity: 0, y: 20 },
      visible: { opacity: 1, y: 0, transition: { duration: 0.3 } }
    }

    switch (activeTab) {
      case 'overview':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <MetricsOverview data={metricsData} loading={loading} />
          </motion.div>
        )
      case 'metas':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <MetasCidades />
          </motion.div>
        )
      case 'analises':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <AnaliseCorreidas />
          </motion.div>
        )
      case 'comparativo':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <ComparativoTemporal />
          </motion.div>
        )
      case 'performance':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <ResumoPerformance data={performanceData} loading={loadingPerformance} />
          </motion.div>
        )
      case 'alertas':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <SistemaAlertas data={alertasData} loading={loadingAlertas} />
          </motion.div>
        )
      case 'ia':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <SistemaIA data={metricsData} />
          </motion.div>
        )
      case 'relatorios':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <RelatoriosExecutivos data={metricsData} />
          </motion.div>
        )
      case 'importacao':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <ImportacaoAvancada />
          </motion.div>
        )
      case 'configuracao':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <ConfiguracaoSheets />
          </motion.div>
        )
      default:
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <MetricsOverview data={metricsData} loading={loading} />
          </motion.div>
        )
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex">
        {/* Sidebar */}
        <motion.div
          initial={{ x: -300 }}
          animate={{ x: sidebarOpen ? 0 : -250 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="fixed left-0 top-0 h-full z-30"
        >
          <Sidebar 
            activeTab={activeTab} 
            setActiveTab={setActiveTab}
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
          />
        </motion.div>

        {/* Main Content */}
        <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
          {/* Header */}
          <Header 
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            onRefresh={fetchMetricsData}
          />

          {/* Content */}
          <main className="p-6">
            {renderContent()}
          </main>
        </div>
      </div>
    </div>
  )
}

export default App

