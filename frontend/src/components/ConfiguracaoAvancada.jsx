import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Database, 
  Palette, 
  Bell, 
  Shield, 
  Download,
  Upload,
  RefreshCw,
  Check,
  AlertTriangle,
  Info,
  Moon,
  Sun
} from 'lucide-react';

export function ConfiguracaoAvancada() {
  const [activeTab, setActiveTab] = useState('geral');
  const [configuracoes, setConfiguracoes] = useState({
    tema: 'light',
    autoRefresh: true,
    refreshInterval: 30,
    notifications: {
      metasAlcancadas: true,
      corridasAtraso: true,
      motoristaInativo: false,
      receitaBaixa: true
    },
    dashboard: {
      mostrarGraficos: true,
      mostrarMapas: false,
      mostrarPredicoes: true,
      animacoes: true
    },
    backup: {
      autoBackup: false,
      backupInterval: 'weekly',
      ultimoBackup: null
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const tabs = [
    { id: 'geral', label: 'Geral', icon: Settings },
    { id: 'aparencia', label: 'Aparência', icon: Palette },
    { id: 'notificacoes', label: 'Notificações', icon: Bell },
    { id: 'dados', label: 'Dados', icon: Database },
    { id: 'backup', label: 'Backup', icon: Shield }
  ];

  const handleConfigChange = (section, key, value) => {
    setConfiguracoes(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Simular salvamento das configurações
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Salvar no localStorage
      localStorage.setItem('dashboard_config', JSON.stringify(configuracoes));
      
      setMessage({ type: 'success', text: 'Configurações salvas com sucesso!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao salvar configurações' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setConfiguracoes({
      tema: 'light',
      autoRefresh: true,
      refreshInterval: 30,
      notifications: {
        metasAlcancadas: true,
        corridasAtraso: true,
        motoristaInativo: false,
        receitaBaixa: true
      },
      dashboard: {
        mostrarGraficos: true,
        mostrarMapas: false,
        mostrarPredicoes: true,
        animacoes: true
      },
      backup: {
        autoBackup: false,
        backupInterval: 'weekly',
        ultimoBackup: null
      }
    });
    setMessage({ type: 'info', text: 'Configurações resetadas para o padrão' });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleExportData = () => {
    const dataStr = JSON.stringify(configuracoes, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `dashboard-config-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleImportData = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedConfig = JSON.parse(e.target.result);
          setConfiguracoes(importedConfig);
          setMessage({ type: 'success', text: 'Configurações importadas com sucesso!' });
          setTimeout(() => setMessage(null), 3000);
        } catch (error) {
          setMessage({ type: 'error', text: 'Arquivo de configuração inválido' });
          setTimeout(() => setMessage(null), 3000);
        }
      };
      reader.readAsText(file);
    }
  };

  useEffect(() => {
    // Carregar configurações do localStorage
    const savedConfig = localStorage.getItem('dashboard_config');
    if (savedConfig) {
      try {
        setConfiguracoes(JSON.parse(savedConfig));
      } catch (error) {
        console.error('Erro ao carregar configurações salvas:', error);
      }
    }
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'geral':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Configurações Gerais</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Atualização Automática</label>
                    <p className="text-xs text-gray-500">Atualizar dados automaticamente</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={configuracoes.autoRefresh}
                      onChange={(e) => handleConfigChange('', 'autoRefresh', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {configuracoes.autoRefresh && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Intervalo de Atualização (segundos)
                    </label>
                    <select
                      value={configuracoes.refreshInterval}
                      onChange={(e) => handleConfigChange('', 'refreshInterval', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={15}>15 segundos</option>
                      <option value={30}>30 segundos</option>
                      <option value={60}>1 minuto</option>
                      <option value={300}>5 minutos</option>
                    </select>
                  </div>
                )}
              </div>
            </div>
          </div>
        );

      case 'aparencia':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Aparência</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tema</label>
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={() => handleConfigChange('', 'tema', 'light')}
                      className={`p-4 border-2 rounded-lg flex flex-col items-center space-y-2 ${
                        configuracoes.tema === 'light' 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <Sun className="w-6 h-6" />
                      <span className="text-sm">Claro</span>
                    </button>
                    <button
                      onClick={() => handleConfigChange('', 'tema', 'dark')}
                      className={`p-4 border-2 rounded-lg flex flex-col items-center space-y-2 ${
                        configuracoes.tema === 'dark' 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <Moon className="w-6 h-6" />
                      <span className="text-sm">Escuro</span>
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Mostrar Gráficos</label>
                      <p className="text-xs text-gray-500">Exibir gráficos no dashboard</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={configuracoes.dashboard.mostrarGraficos}
                        onChange={(e) => handleConfigChange('dashboard', 'mostrarGraficos', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Animações</label>
                      <p className="text-xs text-gray-500">Habilitar animações de transição</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={configuracoes.dashboard.animacoes}
                        onChange={(e) => handleConfigChange('dashboard', 'animacoes', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Predições</label>
                      <p className="text-xs text-gray-500">Mostrar análises preditivas</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={configuracoes.dashboard.mostrarPredicoes}
                        onChange={(e) => handleConfigChange('dashboard', 'mostrarPredicoes', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'notificacoes':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Notificações</h3>
              
              <div className="space-y-4">
                {Object.entries(configuracoes.notifications).map(([key, value]) => {
                  const labels = {
                    metasAlcancadas: { title: 'Metas Alcançadas', desc: 'Notificar quando uma meta for atingida' },
                    corridasAtraso: { title: 'Corridas em Atraso', desc: 'Alertar sobre corridas com atraso' },
                    motoristaInativo: { title: 'Motorista Inativo', desc: 'Avisar sobre motoristas inativos' },
                    receitaBaixa: { title: 'Receita Baixa', desc: 'Alertar sobre queda na receita' }
                  };

                  return (
                    <div key={key} className="flex items-center justify-between">
                      <div>
                        <label className="text-sm font-medium text-gray-700">{labels[key].title}</label>
                        <p className="text-xs text-gray-500">{labels[key].desc}</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={(e) => handleConfigChange('notifications', key, e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        );

      case 'dados':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Gerenciamento de Dados</h3>
              
              <div className="space-y-4">
                <div className="flex space-x-4">
                  <button
                    onClick={handleExportData}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Exportar Configurações</span>
                  </button>
                  
                  <label className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer">
                    <Upload className="w-4 h-4" />
                    <span>Importar Configurações</span>
                    <input
                      type="file"
                      accept=".json"
                      onChange={handleImportData}
                      className="hidden"
                    />
                  </label>
                </div>
                
                <div className="border-t pt-4">
                  <button
                    onClick={() => window.location.reload()}
                    className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Recarregar Dashboard</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      case 'backup':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Backup e Recuperação</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Backup Automático</label>
                    <p className="text-xs text-gray-500">Criar backup das configurações automaticamente</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={configuracoes.backup.autoBackup}
                      onChange={(e) => handleConfigChange('backup', 'autoBackup', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {configuracoes.backup.autoBackup && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Frequência do Backup
                    </label>
                    <select
                      value={configuracoes.backup.backupInterval}
                      onChange={(e) => handleConfigChange('backup', 'backupInterval', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="daily">Diário</option>
                      <option value="weekly">Semanal</option>
                      <option value="monthly">Mensal</option>
                    </select>
                  </div>
                )}

                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">
                    <strong>Último backup:</strong> {configuracoes.backup.ultimoBackup || 'Nunca'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-3"
      >
        <Settings className="w-6 h-6 text-gray-700" />
        <h2 className="text-2xl font-bold text-gray-900">Configurações Avançadas</h2>
      </motion.div>

      {/* Message */}
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-4 rounded-lg flex items-center space-x-2 ${
            message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' :
            message.type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' :
            'bg-blue-50 text-blue-700 border border-blue-200'
          }`}
        >
          {message.type === 'success' && <Check className="w-5 h-5" />}
          {message.type === 'error' && <AlertTriangle className="w-5 h-5" />}
          {message.type === 'info' && <Info className="w-5 h-5" />}
          <span>{message.text}</span>
        </motion.div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="p-6">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
          >
            {renderContent()}
          </motion.div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 rounded-b-lg">
          <div className="flex justify-between">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Resetar para Padrão
            </button>
            <div className="flex space-x-3">
              <button
                onClick={handleSave}
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              >
                {isLoading && <RefreshCw className="w-4 h-4 animate-spin" />}
                <span>{isLoading ? 'Salvando...' : 'Salvar Configurações'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
