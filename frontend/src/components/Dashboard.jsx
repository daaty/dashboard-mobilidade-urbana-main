import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { MetricsOverview } from './MetricsOverview'
import DriversOverview from './DriversOverview'
import { FinanceiroOverview } from './FinanceiroOverview'
import MetasCidades from './MetasCidades'
import DashboardExecutivoIntegrado from './DashboardExecutivoIntegradoSimple'
import AnaliseCorreidas from './AnaliseCorreidas'
import { ComparativoTemporal } from './ComparativoTemporal'
import { ConfiguracaoSheets } from './ConfiguracaoSheets'
import SistemaIA from './SistemaIA'
import RelatoriosExecutivos from './RelatoriosExecutivos'
import ImportacaoAvancada from './ImportacaoAvancada'
import { SistemaAlertas } from './SistemaAlertas'
import { ResumoPerformance } from './ResumoPerformance'
import FloatingChat from './FloatingChat'

// Configuração da URL da API baseada no ambiente
const API_URL = import.meta.env.VITE_API_URL || 
               (import.meta.env.PROD 
                 ? 'https://fastapi.urbanmt.com.br' 
                 : 'http://localhost:8000')

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [metricsData, setMetricsData] = useState(null)
  const [financeiroData, setFinanceiroData] = useState(null)
  const [performanceData, setPerformanceData] = useState(null)
  const [alertasData, setAlertasData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingFinanceiro, setLoadingFinanceiro] = useState(true)
  const [loadingPerformance, setLoadingPerformance] = useState(true)
  const [loadingAlertas, setLoadingAlertas] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true) // Sempre ativo - atualização automática
  const [refreshInterval, setRefreshInterval] = useState(30) // Intervalo em segundos

  useEffect(() => {
    fetchMetricsData()
    fetchFinanceiroData()
    fetchPerformanceData()
    fetchAlertasData()
  }, [])

  // Atualizar dados automaticamente ao trocar de aba
  useEffect(() => {
    switch (activeTab) {
      case 'overview':
        fetchMetricsData()
        break
      case 'financeiro':
        fetchFinanceiroData()
        break
      case 'drivers':
        // Os dados dos motoristas são carregados internamente no componente DriversOverview
        // Podemos adicionar uma prop key para forçar re-render
        break
      case 'analises':
        // Os dados das análises são carregados internamente no componente AnaliseCorreidas
        break
      case 'performance':
        fetchPerformanceData()
        break
      case 'alertas':
        fetchAlertasData()
        break
      default:
        break
    }
  }, [activeTab])

  // Sistema de atualização automática (polling)
  useEffect(() => {
    if (!autoRefresh) return

    const intervalId = setInterval(() => {
      console.log('🔄 Atualizando dados automaticamente...')
      
      // Atualizar dados baseado na aba ativa
      switch (activeTab) {
        case 'overview':
          fetchMetricsData()
          break
        case 'financeiro':
          fetchFinanceiroData()
          break
        case 'performance':
          fetchPerformanceData()
          break
        case 'alertas':
          fetchAlertasData()
          break
        default:
          // Para abas que carregam dados internamente, atualizamos todas as principais
          fetchMetricsData()
          break
      }
    }, refreshInterval * 1000) // Converter segundos para millisegundos

    return () => {
      clearInterval(intervalId)
    }
  }, [activeTab, autoRefresh, refreshInterval])

  // Atualização quando a aba do navegador volta ao foco (usuário volta para a página)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && autoRefresh) {
        console.log('👁️ Página voltou ao foco, atualizando dados...')
        fetchMetricsData()
        fetchFinanceiroData()
        fetchPerformanceData()
        fetchAlertasData()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [autoRefresh])

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

  const fetchFinanceiroData = async (period = '365d') => {
    try {
      setLoadingFinanceiro(true)
      // Converte período para número de dias
      let periodoDias = 365; // Padrão 365 dias pois os dados são de maio
      if (period === 'hoje') periodoDias = 1;
      else if (period === '7d') periodoDias = 7;
      else if (period === '30d') periodoDias = 90; // Aumenta para 90 para pegar dados de maio
      else if (period === '90d') periodoDias = 120; // Aumenta para 120 para pegar dados de maio
      else if (period === '365d') periodoDias = 365;
      
      const response = await fetch(`${API_URL}/api/financeiro/overview?periodo=${periodoDias}`)
      const data = await response.json()
      setFinanceiroData(data)
      console.log('Dados financeiros recebidos:', data) // Debug
    } catch (error) {
      console.error('Erro ao buscar dados financeiros:', error)
    } finally {
      setLoadingFinanceiro(false)
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
      setAlertasData(data)
    } catch (error) {
      console.error('Erro ao buscar alertas:', error)
    } finally {
      setLoadingAlertas(false)
    }
  }

  const handleFinanceiroPeriodChange = (period) => {
    fetchFinanceiroData(period)
  }

  const contentVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut"
      }
    }
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'financeiro':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <FinanceiroOverview 
              data={financeiroData} 
              loading={loadingFinanceiro} 
              onPeriodChange={handleFinanceiroPeriodChange}
            />
          </motion.div>
        )
      case 'metas':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <MetasCidades key={`metas-${Date.now()}`} />
          </motion.div>
        )
      case 'config':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <ConfiguracaoSheets key={`config-${Date.now()}`} />
          </motion.div>
        )
      case 'executivo':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <DashboardExecutivoIntegrado key={`executivo-${Date.now()}`} />
          </motion.div>
        )
      case 'analises':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <AnaliseCorreidas key={`analises-${Date.now()}`} />
          </motion.div>
        )
      case 'drivers':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <DriversOverview key={`drivers-${Date.now()}`} />
          </motion.div>
        )
      case 'comparativo':
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <ComparativoTemporal key={`comparativo-${Date.now()}`} />
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
        <div className={`flex-1 transition-all duration-300 ${
          sidebarOpen 
            ? 'md:ml-64 ml-0' // Em mobile, não aplica margin-left quando sidebar está aberta (overlay)
            : 'ml-0 md:ml-16'
        }`}>
          {/* Header */}
        <Header 
          sidebarOpen={sidebarOpen} 
          setSidebarOpen={setSidebarOpen}
          refreshInterval={refreshInterval}
          setRefreshInterval={setRefreshInterval}
        />          {/* Content */}
          <main className="p-3 sm:p-6">
            {renderContent()}
          </main>
        </div>

        {/* Mobile Overlay quando sidebar está aberta */}
        {sidebarOpen && (
          <div 
            className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Chat Flutuante Global */}
        <FloatingChat />
      </div>
    </div>
  )
}

export default Dashboard
