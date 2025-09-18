import { motion } from 'framer-motion'
import { RefreshCw, Sun, Moon, Bell, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

export function Header({ 
  sidebarOpen, 
  setSidebarOpen, 
  refreshInterval, 
  setRefreshInterval 
}) {
  const [isDark, setIsDark] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const { user, logout } = useAuth()

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 py-2 sm:py-4">
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center space-x-2 sm:space-x-4">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setSidebarOpen && setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 min-h-[44px] min-w-[44px] touch-manipulation flex items-center justify-center"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col"
          >
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
              <span className="hidden sm:inline">Dashboard de Métricas</span>
              <span className="sm:hidden">Dashboard</span>
            </h2>
            <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 hidden sm:block">
              {currentTime.toLocaleDateString('pt-BR', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })} - {currentTime.toLocaleTimeString('pt-BR')}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 sm:hidden">
              {currentTime.toLocaleTimeString('pt-BR')}
            </p>
          </motion.div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Auto Refresh Controls */}
          <motion.div 
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className="hidden sm:flex items-center space-x-2 bg-gray-50 dark:bg-gray-700 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-600"
          >
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
              Auto-refresh
            </span>
            {setRefreshInterval && (
              <select
                value={refreshInterval || 30}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="text-xs bg-transparent border-0 text-gray-600 dark:text-gray-400 focus:ring-0 p-0 pr-4"
              >
                <option value={15}>15s</option>
                <option value={30}>30s</option>
                <option value={60}>1m</option>
                <option value={300}>5m</option>
              </select>
            )}
            <div 
              className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" 
            />
          </motion.div>

          {/* Mobile Auto Refresh - Simplified */}
          <motion.div 
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className="sm:hidden flex items-center space-x-1 bg-gray-50 dark:bg-gray-700 px-2 py-1 rounded-lg border border-gray-200 dark:border-gray-600"
          >
            {setRefreshInterval && (
              <select
                value={refreshInterval || 30}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="text-xs bg-transparent border-0 text-gray-600 dark:text-gray-400 focus:ring-0 p-0 pr-2"
              >
                <option value={15}>15s</option>
                <option value={30}>30s</option>
                <option value={60}>1m</option>
                <option value={300}>5m</option>
              </select>
            )}
            <div 
              className="w-1 h-1 rounded-full bg-green-500 animate-pulse" 
            />
          </motion.div>

          {/* Theme Toggle */}
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleTheme}
              className="p-2 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 min-h-[44px] min-w-[44px] touch-manipulation"
            >
              {isDark ? <Sun className="w-4 h-4 sm:w-4 sm:h-4" /> : <Moon className="w-4 h-4 sm:w-4 sm:h-4" />}
            </Button>
          </motion.div>

          {/* Notifications */}
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              variant="outline"
              size="sm"
              className="p-2 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 relative min-h-[44px] min-w-[44px] touch-manipulation"
            >
              <Bell className="w-4 h-4 sm:w-4 sm:h-4" />
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 sm:-top-1 sm:-right-1 w-3 h-3 sm:w-3 sm:h-3 bg-red-500 rounded-full"
              />
            </Button>
          </motion.div>

          {/* User Profile */}
          {user && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center space-x-2 sm:space-x-3 bg-gray-50 dark:bg-gray-700 px-2 sm:px-3 py-1 sm:py-2 rounded-lg border-l border-gray-200 dark:border-gray-700"
            >
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {user.name}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {user.role}
                </span>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={logout}
                className="p-1.5 sm:p-2 hover:bg-red-50 dark:hover:bg-red-900 hover:text-red-600 dark:hover:text-red-400"
                title={user?.name ? `Sair (${user.name})` : 'Sair'}
              >
                <LogOut className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden md:inline ml-1 text-xs">Sair</span>
              </Button>
            </motion.div>
          )}
        </div>
      </div>
    </header>
  )
}

