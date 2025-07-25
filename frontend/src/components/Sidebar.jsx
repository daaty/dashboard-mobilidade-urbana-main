import { motion } from 'framer-motion'
import { 
  BarChart3, 
  Target, 
  PieChart, 
  TrendingUp, 
  Settings,
  Menu,
  X,
  Home,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'


export function Sidebar({ activeTab, setActiveTab, isOpen, onToggle }) {
  const menuItems = [
    { id: 'overview', label: 'Visão Geral', icon: Home },
    { id: 'analises', label: 'Análise de Corridas', icon: PieChart },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'metas', label: 'Metas por Cidade', icon: Target },
    { id: 'comparativo', label: 'Comparativo Temporal', icon: TrendingUp },
    { id: 'alertas', label: 'Alertas', icon: AlertCircle },
    { id: 'ia', label: 'IA & Insights', icon: BarChart3 },
    { id: 'relatorios', label: 'Relatórios', icon: TrendingUp },
    { id: 'importacao', label: 'Importação', icon: Settings },
    { id: 'configuracao', label: 'Configurações', icon: Settings }
  ]

  return (
    <div className={`bg-white dark:bg-gray-900 h-screen shadow-2xl border-r border-gray-200 dark:border-gray-800 relative flex flex-col ${isOpen ? 'w-64' : 'w-16'} transition-all duration-300`}>
      {/* Header Moderno */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex items-center space-x-3"
          >
            <div className="w-9 h-9 bg-black rounded-lg flex items-center justify-center shadow">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-gray-900 dark:text-white tracking-tight leading-tight">Dashboard</h1>
              <p className="text-xs text-gray-700 dark:text-gray-300 font-semibold">Transporte</p>
            </div>
          </motion.div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggle}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {isOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </Button>
      </div>

      {/* Navigation Moderno */}
      <nav className="p-4 flex-1 flex flex-col gap-1">
        {menuItems.map((item, idx) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          // Separador após Visão Geral
          const showDivider = idx === 1
          return (
            <motion.div
              key={item.id}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
            >
              {showDivider && isOpen && (
                <div className="my-2 border-t border-gray-200 dark:border-gray-700 opacity-70" />
              )}
              <button
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 relative overflow-hidden
                  group
                  ${isActive ? 'bg-black text-white shadow-lg' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}
                `}
                style={{ borderLeft: isActive ? '5px solid #111' : '5px solid transparent' }}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-white' : 'text-gray-700 dark:text-gray-300'}`} />
                {isOpen && (
                  <span className={`text-base font-medium transition-colors duration-200 ${isActive ? 'text-white' : ''}`}>{item.label}</span>
                )}
              </button>
            </motion.div>
          )
        })}
      </nav>

      {/* Footer removido conforme solicitado */}
    </div>
  )
}

