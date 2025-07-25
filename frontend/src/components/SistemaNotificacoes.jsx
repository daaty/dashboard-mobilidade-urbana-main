import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell, 
  X, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  Clock, 
  Target,
  TrendingDown,
  Users,
  Settings
} from 'lucide-react';

export function SistemaNotificacoes() {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Simular recebimento de notificações
  useEffect(() => {
    const initialNotifications = [
      {
        id: 1,
        type: 'success',
        title: 'Meta Alcançada!',
        message: 'São Paulo atingiu 105% da meta mensal de corridas',
        timestamp: new Date(Date.now() - 10 * 60 * 1000), // 10 minutos atrás
        read: false,
        icon: Target,
        action: 'Visualizar Relatório'
      },
      {
        id: 2,
        type: 'warning',
        title: 'Motorista Inativo',
        message: 'João Silva está inativo há mais de 3 dias',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 horas atrás
        read: false,
        icon: Users,
        action: 'Entrar em Contato'
      },
      {
        id: 3,
        type: 'info',
        title: 'Relatório Semanal',
        message: 'Relatório de performance da semana está disponível',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 horas atrás
        read: true,
        icon: Info,
        action: 'Baixar Relatório'
      },
      {
        id: 4,
        type: 'error',
        title: 'Queda na Receita',
        message: 'Receita diária 15% abaixo da média dos últimos 30 dias',
        timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000), // 12 horas atrás
        read: false,
        icon: TrendingDown,
        action: 'Analisar Dados'
      }
    ];

    setNotifications(initialNotifications);
    setUnreadCount(initialNotifications.filter(n => !n.read).length);

    // Simular novas notificações periodicamente
    const interval = setInterval(() => {
      const randomNotifications = [
        {
          type: 'info',
          title: 'Nova Corrida Completada',
          message: 'Corrida em Brasília foi completada com sucesso',
          icon: CheckCircle
        },
        {
          type: 'warning',
          title: 'Tempo de Resposta Alto',
          message: 'Tempo médio de aceitação de corridas aumentou 20%',
          icon: Clock
        },
        {
          type: 'success',
          title: 'Avaliação Excelente',
          message: 'Maria Santos recebeu avaliação 5 estrelas',
          icon: CheckCircle
        }
      ];

      const randomNotification = randomNotifications[Math.floor(Math.random() * randomNotifications.length)];
      
      if (Math.random() < 0.3) { // 30% de chance a cada minuto
        const newNotification = {
          id: Date.now(),
          ...randomNotification,
          timestamp: new Date(),
          read: false,
          action: 'Ver Detalhes'
        };

        setNotifications(prev => [newNotification, ...prev.slice(0, 9)]); // Manter apenas 10 notificações
        setUnreadCount(prev => prev + 1);
      }
    }, 60000); // A cada minuto

    return () => clearInterval(interval);
  }, []);

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, read: true }
          : notification
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
    setUnreadCount(0);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    const notification = notifications.find(n => n.id === id);
    if (notification && !notification.read) {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return CheckCircle;
      case 'warning':
        return AlertTriangle;
      case 'error':
        return TrendingDown;
      default:
        return Info;
    }
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Agora';
    if (minutes < 60) return `${minutes}m`;
    if (hours < 24) return `${hours}h`;
    return `${days}d`;
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </motion.span>
        )}
      </button>

      {/* Notification Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className="absolute top-full right-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-xl z-50 max-h-96 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Notificações</h3>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Marcar todas como lidas
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Notifications List */}
            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <Bell className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Nenhuma notificação</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {notifications.map((notification) => {
                    const Icon = notification.icon || getNotificationIcon(notification.type);
                    
                    return (
                      <motion.div
                        key={notification.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className={`p-4 hover:bg-gray-50 transition-colors ${
                          !notification.read ? 'bg-blue-50' : ''
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <div className={`p-2 rounded-lg ${getNotificationColor(notification.type)}`}>
                            <Icon className="w-4 h-4" />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className={`text-sm font-medium ${
                                !notification.read ? 'text-gray-900' : 'text-gray-700'
                              }`}>
                                {notification.title}
                              </p>
                              <div className="flex items-center space-x-2">
                                <span className="text-xs text-gray-500">
                                  {formatTimestamp(notification.timestamp)}
                                </span>
                                <button
                                  onClick={() => removeNotification(notification.id)}
                                  className="text-gray-400 hover:text-gray-600"
                                >
                                  <X className="w-3 h-3" />
                                </button>
                              </div>
                            </div>
                            
                            <p className="text-sm text-gray-600 mt-1">
                              {notification.message}
                            </p>
                            
                            <div className="flex items-center justify-between mt-3">
                              {notification.action && (
                                <button
                                  onClick={() => markAsRead(notification.id)}
                                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                                >
                                  {notification.action}
                                </button>
                              )}
                              
                              {!notification.read && (
                                <button
                                  onClick={() => markAsRead(notification.id)}
                                  className="text-xs text-gray-500 hover:text-gray-700"
                                >
                                  Marcar como lida
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="border-t border-gray-200 p-3">
                <button
                  onClick={() => {
                    // Implementar visualização de todas as notificações
                    console.log('Ver todas as notificações');
                  }}
                  className="w-full text-center text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  Ver todas as notificações
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toast Notifications para novas notificações */}
      <AnimatePresence>
        {notifications
          .filter(n => !n.read && (new Date() - n.timestamp) < 5000) // Mostrar apenas por 5 segundos
          .slice(0, 1) // Mostrar apenas a mais recente
          .map(notification => {
            const Icon = notification.icon || getNotificationIcon(notification.type);
            
            return (
              <motion.div
                key={`toast-${notification.id}`}
                initial={{ opacity: 0, y: -50, x: 100 }}
                animate={{ opacity: 1, y: 0, x: 0 }}
                exit={{ opacity: 0, y: -50, x: 100 }}
                className="fixed top-4 right-4 z-50 max-w-sm bg-white border border-gray-200 rounded-lg shadow-lg p-4"
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${getNotificationColor(notification.type)}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {notification.title}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {notification.message}
                    </p>
                  </div>
                  <button
                    onClick={() => removeNotification(notification.id)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            );
          })}
      </AnimatePresence>
    </div>
  );
}
