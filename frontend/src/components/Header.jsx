import { motion } from 'framer-motion'
import { RefreshCw, Sun, Moon, Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState, useEffect } from 'react'

export function Header({ sidebarOpen, setSidebarOpen, onRefresh }) {
  const [isDark, setIsDark] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await onRefresh()
    setTimeout(() => setIsRefreshing(false), 1000)
  }

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col"
          >
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Dashboard de Métricas
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {currentTime.toLocaleDateString('pt-BR', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })} - {currentTime.toLocaleTimeString('pt-BR')}
            </p>
          </motion.div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-3">
          {/* Refresh Button */}
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center space-x-2 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Atualizar</span>
            </Button>
          </motion.div>

          {/* Theme Toggle */}
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleTheme}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
          </motion.div>

          {/* Notifications */}
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              variant="outline"
              size="sm"
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 relative"
            >
              <Bell className="w-4 h-4" />
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"
              />
            </Button>
          </motion.div>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="w-2 h-2 bg-green-500 rounded-full"
            />
            <span className="text-sm text-gray-600 dark:text-gray-400 hidden sm:inline">
              Online
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

