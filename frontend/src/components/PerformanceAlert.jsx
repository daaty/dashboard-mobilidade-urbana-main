import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Info, XCircle } from 'lucide-react';

/**
 * Componente para exibir alertas de performance
 */
export function PerformanceAlert({ alert, onAction }) {
  const getSeverityConfig = () => {
    switch (alert.severity) {
      case 'warning':
        return {
          icon: AlertTriangle,
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
          borderColor: 'border-yellow-400 dark:border-yellow-600',
          textColor: 'text-yellow-900 dark:text-yellow-200',
          descColor: 'text-yellow-700 dark:text-yellow-300',
          buttonColor: 'bg-yellow-200 dark:bg-yellow-700 text-yellow-800 dark:text-yellow-100 hover:bg-yellow-300 dark:hover:bg-yellow-600'
        };
      case 'error':
        return {
          icon: XCircle,
          bgColor: 'bg-red-50 dark:bg-red-900/20',
          borderColor: 'border-red-400 dark:border-red-600',
          textColor: 'text-red-900 dark:text-red-200',
          descColor: 'text-red-700 dark:text-red-300',
          buttonColor: 'bg-red-200 dark:bg-red-700 text-red-800 dark:text-red-100 hover:bg-red-300 dark:hover:bg-red-600'
        };
      case 'info':
      default:
        return {
          icon: Info,
          bgColor: 'bg-blue-50 dark:bg-blue-900/20',
          borderColor: 'border-blue-400 dark:border-blue-600',
          textColor: 'text-blue-900 dark:text-blue-200',
          descColor: 'text-blue-700 dark:text-blue-300',
          buttonColor: 'bg-blue-200 dark:bg-blue-700 text-blue-800 dark:text-blue-100 hover:bg-blue-300 dark:hover:bg-blue-600'
        };
    }
  };

  const config = getSeverityConfig();
  const IconComponent = config.icon;

  const getPriorityBadge = () => {
    if (!alert.priority) return null;

    const badges = {
      high: { text: 'Alta', color: 'bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-200' },
      medium: { text: 'Média', color: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-200' },
      low: { text: 'Baixa', color: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200' }
    };

    const badge = badges[alert.priority];
    if (!badge) return null;

    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${badge.color}`}>
        {badge.text}
      </span>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className={`p-4 rounded-lg border-l-4 ${config.bgColor} ${config.borderColor}`}
    >
      <div className="flex items-start space-x-3">
        <IconComponent className={`w-5 h-5 mt-0.5 ${config.textColor}`} />
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <p className={`text-sm font-medium ${config.textColor}`}>
              {alert.title}
            </p>
            {getPriorityBadge()}
          </div>
          
          <p className={`text-sm ${config.descColor} mb-3`}>
            {alert.description}
          </p>

          {alert.action && (
            <button
              onClick={() => onAction && onAction(alert)}
              className={`text-xs font-medium px-3 py-1.5 rounded-md transition-colors duration-200 ${config.buttonColor}`}
            >
              {alert.action}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
