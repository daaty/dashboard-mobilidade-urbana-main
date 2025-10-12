import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Settings, Save, Lock, Bell, Palette, 
  AlertCircle, CheckCircle, Eye, EyeOff, 
  Moon, Sun, Monitor, Globe, Clock, Shield,
  Zap, RefreshCw, Mail, Volume2, Info
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'

export function ConfiguracaoSheets() {
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  })
  
  const [settings, setSettings] = useState({
    theme: localStorage.getItem('theme') || 'system',
    language: 'pt-BR',
    timezone: 'America/Sao_Paulo',
    autoRefresh: true,
    refreshInterval: 30,
    notifications: {
      email: true,
      push: false,
      sound: true
    }
  })
  
  const [loading, setLoading] = useState(false)
  const [saveResult, setSaveResult] = useState(null)
  const [activeSection, setActiveSection] = useState('security')

  const handlePasswordChange = (field, value) => {
    setPasswordForm(prev => ({ ...prev, [field]: value }))
  }

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }))
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setSaveResult({ status: 'error', message: 'As senhas não coincidem!' })
      return
    }

    if (passwordForm.newPassword.length < 8) {
      setSaveResult({ status: 'error', message: 'A senha deve ter no mínimo 8 caracteres!' })
      return
    }

    try {
      setLoading(true)
      setSaveResult(null)
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setSaveResult({ status: 'success', message: 'Senha alterada com sucesso!' })
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
      
      setTimeout(() => setSaveResult(null), 3000)
    } catch (error) {
      setSaveResult({ status: 'error', message: 'Erro ao alterar senha: ' + error.message })
    } finally {
      setLoading(false)
    }
  }

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleNotificationChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      notifications: { ...prev.notifications, [key]: value }
    }))
  }

  const handleThemeChange = (theme) => {
    setSettings(prev => ({ ...prev, theme }))
    localStorage.setItem('theme', theme)
    
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (theme === 'light') {
      document.documentElement.classList.remove('dark')
    } else {
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }

  const handleSaveSettings = async () => {
    try {
      setLoading(true)
      setSaveResult(null)
      
      localStorage.setItem('dashboard_settings', JSON.stringify(settings))
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setSaveResult({ status: 'success', message: 'Configurações salvas com sucesso!' })
      setTimeout(() => setSaveResult(null), 3000)
    } catch (error) {
      setSaveResult({ status: 'error', message: 'Erro ao salvar configurações: ' + error.message })
    } finally {
      setLoading(false)
    }
  }

  // Toggle Switch Component
  const ToggleSwitch = ({ checked, onChange, disabled = false }) => (
    <label className="relative inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="sr-only peer"
      />
      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
    </label>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg">
                <Settings className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                  Configurações
                </h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">
                  Personalize sua experiência no dashboard
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-2 flex space-x-2 overflow-x-auto">
            {[
              { id: 'security', label: 'Segurança', icon: Shield },
              { id: 'appearance', label: 'Aparência', icon: Palette },
              { id: 'notifications', label: 'Notificações', icon: Bell },
              { id: 'preferences', label: 'Preferências', icon: Settings }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveSection(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl transition-all duration-300 whitespace-nowrap font-medium ${
                  activeSection === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md transform scale-105'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Alert de Resultado */}
        <AnimatePresence>
          {saveResult && (
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="mb-6"
            >
              <Alert className={`shadow-lg ${
                saveResult.status === 'success' 
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/30 border-l-4' 
                  : 'border-red-500 bg-red-50 dark:bg-red-900/30 border-l-4'
              }`}>
                {saveResult.status === 'success' ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-600" />
                )}
                <AlertDescription className={`font-semibold ${
                  saveResult.status === 'success' 
                    ? 'text-green-800 dark:text-green-200' 
                    : 'text-red-800 dark:text-red-200'
                }`}>
                  {saveResult.message}
                </AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Content Sections */}
        <AnimatePresence mode="wait">
          {/* Seção: Segurança */}
          {activeSection === 'security' && (
            <motion.div
              key="security"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
                  <CardTitle className="flex items-center space-x-3">
                    <Shield className="w-6 h-6" />
                    <div>
                      <h3 className="text-2xl font-bold">Segurança da Conta</h3>
                      <p className="text-sm text-blue-100 mt-1">Altere sua senha e mantenha sua conta segura</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-8">
                  <form onSubmit={handlePasswordSubmit} className="space-y-6">
                    {/* Senha Atual */}
                    <div className="space-y-2">
                      <Label className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                        <Lock className="w-4 h-4 text-blue-600" />
                        <span>Senha Atual</span>
                      </Label>
                      <div className="relative">
                        <Input
                          type={showPasswords.current ? "text" : "password"}
                          value={passwordForm.currentPassword}
                          onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
                          placeholder="••••••••"
                          className="h-14 pr-12 text-base border-2 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-gray-50 dark:bg-gray-700/50"
                        />
                        <button
                          type="button"
                          onClick={() => togglePasswordVisibility('current')}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600 transition-colors"
                        >
                          {showPasswords.current ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    {/* Nova Senha */}
                    <div className="space-y-2">
                      <Label className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                        <Lock className="w-4 h-4 text-blue-600" />
                        <span>Nova Senha</span>
                      </Label>
                      <div className="relative">
                        <Input
                          type={showPasswords.new ? "text" : "password"}
                          value={passwordForm.newPassword}
                          onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                          placeholder="Mínimo 8 caracteres"
                          className="h-14 pr-12 text-base border-2 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-gray-50 dark:bg-gray-700/50"
                        />
                        <button
                          type="button"
                          onClick={() => togglePasswordVisibility('new')}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600 transition-colors"
                        >
                          {showPasswords.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                      {passwordForm.newPassword && passwordForm.newPassword.length < 8 && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-sm text-amber-600 dark:text-amber-400 flex items-center space-x-1"
                        >
                          <Info className="w-4 h-4" />
                          <span>A senha deve ter no mínimo 8 caracteres</span>
                        </motion.p>
                      )}
                    </div>

                    {/* Confirmar Senha */}
                    <div className="space-y-2">
                      <Label className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                        <Lock className="w-4 h-4 text-blue-600" />
                        <span>Confirmar Nova Senha</span>
                      </Label>
                      <div className="relative">
                        <Input
                          type={showPasswords.confirm ? "text" : "password"}
                          value={passwordForm.confirmPassword}
                          onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
                          placeholder="Digite novamente"
                          className="h-14 pr-12 text-base border-2 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-gray-50 dark:bg-gray-700/50"
                        />
                        <button
                          type="button"
                          onClick={() => togglePasswordVisibility('confirm')}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600 transition-colors"
                        >
                          {showPasswords.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                      {passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-sm text-red-600 dark:text-red-400 flex items-center space-x-1"
                        >
                          <AlertCircle className="w-4 h-4" />
                          <span>As senhas não coincidem</span>
                        </motion.p>
                      )}
                    </div>

                    <div className="pt-6">
                      <Button
                        type="submit"
                        disabled={loading || !passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword}
                        className="group relative w-full rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 h-16 text-xl font-bold shadow-2xl hover:shadow-[0_20px_50px_rgba(59,130,246,0.5)] transform hover:scale-[1.03] active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none overflow-hidden"
                      >
                        {/* Efeito de brilho animado */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                        
                        {/* Conteúdo do botão */}
                        <div className="relative flex items-center justify-center space-x-3">
                          {loading ? (
                            <>
                              <RefreshCw className="w-6 h-6 animate-spin" />
                              <span className="tracking-wide">Alterando Senha...</span>
                            </>
                          ) : (
                            <>
                              <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                                <Lock className="w-6 h-6" />
                              </div>
                              <span className="tracking-wide">Alterar Senha</span>
                              <div className="absolute right-6 opacity-0 group-hover:opacity-100 group-hover:translate-x-0 translate-x-2 transition-all duration-300">
                                →
                              </div>
                            </>
                          )}
                        </div>
                      </Button>
                      
                      {/* Texto auxiliar */}
                      <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-3 flex items-center justify-center space-x-1">
                        <Shield className="w-3 h-3" />
                        <span>Suas credenciais estão protegidas com criptografia</span>
                      </p>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Seção: Aparência */}
          {activeSection === 'appearance' && (
            <motion.div
              key="appearance"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
                  <CardTitle className="flex items-center space-x-3">
                    <Palette className="w-6 h-6" />
                    <div>
                      <h3 className="text-2xl font-bold">Aparência</h3>
                      <p className="text-sm text-purple-100 mt-1">Personalize o visual do dashboard</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-8 space-y-6">
                  {/* Tema */}
                  <div className="space-y-3">
                    <Label className="text-sm font-bold text-gray-700 dark:text-gray-300">Tema do Dashboard</Label>
                    <div className="grid grid-cols-3 gap-4">
                      {[
                        { id: 'light', label: 'Claro', icon: Sun, gradient: 'from-yellow-400 to-orange-500' },
                        { id: 'dark', label: 'Escuro', icon: Moon, gradient: 'from-indigo-600 to-purple-700' },
                        { id: 'system', label: 'Sistema', icon: Monitor, gradient: 'from-gray-500 to-gray-700' }
                      ].map((theme) => (
                        <button
                          key={theme.id}
                          onClick={() => handleThemeChange(theme.id)}
                          className={`p-6 border-2 rounded-2xl flex flex-col items-center space-y-3 transition-all duration-300 ${
                            settings.theme === theme.id 
                              ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20 shadow-lg scale-105' 
                              : 'border-gray-300 dark:border-gray-600 hover:border-purple-400 hover:shadow-md'
                          }`}
                        >
                          <div className={`p-3 rounded-xl bg-gradient-to-br ${theme.gradient}`}>
                            <theme.icon className="w-8 h-8 text-white" />
                          </div>
                          <span className="font-semibold text-gray-900 dark:text-white">{theme.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Idioma */}
                  <div className="space-y-3">
                    <Label className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                      <Globe className="w-4 h-4 text-purple-600" />
                      <span>Idioma</span>
                    </Label>
                    <select
                      value={settings.language}
                      onChange={(e) => handleSettingChange('language', e.target.value)}
                      className="w-full h-12 px-4 text-lg border-2 border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                    >
                      <option value="pt-BR">🇧🇷 Português (Brasil)</option>
                      <option value="en-US">🇺🇸 English (US)</option>
                      <option value="es">🇪🇸 Español</option>
                    </select>
                  </div>

                  {/* Fuso Horário */}
                  <div className="space-y-3">
                    <Label className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-purple-600" />
                      <span>Fuso Horário</span>
                    </Label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => handleSettingChange('timezone', e.target.value)}
                      className="w-full h-12 px-4 text-lg border-2 border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                    >
                      <option value="America/Sao_Paulo">🕐 Brasília (GMT-3)</option>
                      <option value="America/New_York">🕐 Nova York (GMT-5)</option>
                      <option value="Europe/London">🕐 Londres (GMT+0)</option>
                      <option value="Asia/Tokyo">🕐 Tóquio (GMT+9)</option>
                    </select>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Seção: Notificações */}
          {activeSection === 'notifications' && (
            <motion.div
              key="notifications"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white">
                  <CardTitle className="flex items-center space-x-3">
                    <Bell className="w-6 h-6" />
                    <div>
                      <h3 className="text-2xl font-bold">Notificações</h3>
                      <p className="text-sm text-yellow-100 mt-1">Gerencie como você recebe alertas</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-8 space-y-6">
                  {[
                    { 
                      key: 'email', 
                      label: 'Notificações por E-mail', 
                      description: 'Receber atualizações e alertas por e-mail',
                      icon: Mail,
                      color: 'text-blue-600'
                    },
                    { 
                      key: 'push', 
                      label: 'Notificações Push', 
                      description: 'Receber notificações no navegador em tempo real',
                      icon: Bell,
                      color: 'text-green-600'
                    },
                    { 
                      key: 'sound', 
                      label: 'Som de Notificações', 
                      description: 'Reproduzir som ao receber notificações',
                      icon: Volume2,
                      color: 'text-purple-600'
                    }
                  ].map((notification) => (
                    <div key={notification.key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:shadow-md transition-shadow">
                      <div className="flex items-start space-x-4">
                        <div className={`p-3 bg-white dark:bg-gray-800 rounded-lg ${notification.color}`}>
                          <notification.icon className="w-6 h-6" />
                        </div>
                        <div>
                          <p className="font-bold text-gray-900 dark:text-white">{notification.label}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{notification.description}</p>
                        </div>
                      </div>
                      <ToggleSwitch
                        checked={settings.notifications[notification.key]}
                        onChange={(e) => handleNotificationChange(notification.key, e.target.checked)}
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Seção: Preferências */}
          {activeSection === 'preferences' && (
            <motion.div
              key="preferences"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-green-600 to-teal-600 text-white">
                  <CardTitle className="flex items-center space-x-3">
                    <Settings className="w-6 h-6" />
                    <div>
                      <h3 className="text-2xl font-bold">Preferências do Dashboard</h3>
                      <p className="text-sm text-green-100 mt-1">Configure o comportamento do sistema</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-8 space-y-6">
                  {/* Auto-refresh */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:shadow-md transition-shadow">
                    <div className="flex items-start space-x-4">
                      <div className="p-3 bg-white dark:bg-gray-800 rounded-lg text-green-600">
                        <RefreshCw className="w-6 h-6" />
                      </div>
                      <div>
                        <p className="font-bold text-gray-900 dark:text-white">Atualização Automática</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Atualizar dados automaticamente em segundo plano</p>
                      </div>
                    </div>
                    <ToggleSwitch
                      checked={settings.autoRefresh}
                      onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
                    />
                  </div>

                  {/* Intervalo de atualização */}
                  <AnimatePresence>
                    {settings.autoRefresh && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="pl-4 border-l-4 border-green-600 space-y-3"
                      >
                        <Label className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                          <Zap className="w-4 h-4 text-green-600" />
                          <span>Intervalo de Atualização (segundos)</span>
                        </Label>
                        <div className="flex items-center space-x-4">
                          <Input
                            type="range"
                            min="10"
                            max="300"
                            step="10"
                            value={settings.refreshInterval}
                            onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
                            className="flex-1"
                          />
                          <div className="px-4 py-2 bg-green-100 dark:bg-green-900/30 rounded-lg text-green-800 dark:text-green-200 font-bold min-w-[80px] text-center">
                            {settings.refreshInterval}s
                          </div>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Os dados serão atualizados a cada {settings.refreshInterval} segundos
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Botão Salvar Global */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-10 flex flex-col items-center space-y-4"
        >
          <Button
            onClick={handleSaveSettings}
            disabled={loading}
            className="group relative rounded-2xl bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 hover:from-green-700 hover:via-emerald-700 hover:to-teal-700 text-white px-12 py-6 h-auto text-xl font-bold shadow-2xl hover:shadow-[0_20px_50px_rgba(16,185,129,0.6)] transform hover:scale-[1.05] active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none overflow-hidden min-w-[320px]"
          >
            {/* Efeito de brilho animado */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
            
            {/* Partículas de fundo (efeito decorativo) */}
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-2 left-4 w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <div className="absolute top-4 right-8 w-1 h-1 bg-white rounded-full animate-pulse delay-75"></div>
              <div className="absolute bottom-3 left-12 w-1.5 h-1.5 bg-white rounded-full animate-pulse delay-150"></div>
              <div className="absolute bottom-2 right-6 w-1 h-1 bg-white rounded-full animate-pulse delay-300"></div>
            </div>

            {/* Conteúdo do botão */}
            <div className="relative flex items-center justify-center space-x-3">
              {loading ? (
                <>
                  <RefreshCw className="w-7 h-7 animate-spin" />
                  <span className="tracking-wide">Salvando Configurações...</span>
                </>
              ) : (
                <>
                  <div className="p-2.5 bg-white/20 rounded-xl backdrop-blur-sm group-hover:rotate-12 transition-transform duration-300">
                    <Save className="w-7 h-7" />
                  </div>
                  <span className="tracking-wide">Salvar Todas as Configurações</span>
                  <div className="absolute right-8 opacity-0 group-hover:opacity-100 group-hover:translate-x-0 translate-x-2 transition-all duration-300 text-2xl">
                    ✓
                  </div>
                </>
              )}
            </div>
          </Button>

          {/* Texto auxiliar com ícones */}
          <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Salvo localmente</span>
            </div>
            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
            <div className="flex items-center space-x-1">
              <Shield className="w-4 h-4 text-blue-600" />
              <span>Dados protegidos</span>
            </div>
            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
            <div className="flex items-center space-x-1">
              <Zap className="w-4 h-4 text-yellow-600" />
              <span>Aplicado instantaneamente</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
