import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * Componente para exibir previsões de performance
 */
export function PerformancePrediction({ prediction, delay = 0 }) {
  const getTrendIcon = () => {
    if (prediction.trend === 'up') return <TrendingUp className="w-4 h-4" />;
    if (prediction.trend === 'down') return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  const getTrendColor = () => {
    if (prediction.trend === 'up') return 'text-green-600 dark:text-green-400';
    if (prediction.trend === 'down') return 'text-red-600 dark:text-red-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  const getConfidenceColor = () => {
    if (prediction.confidence >= 85) return 'bg-green-500';
    if (prediction.confidence >= 70) return 'bg-blue-500';
    if (prediction.confidence >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-2">
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {prediction.metric}
        </p>
        <div className={`flex items-center space-x-1 ${getTrendColor()}`}>
          {getTrendIcon()}
          <span className="text-sm font-medium">{prediction.change}</span>
        </div>
      </div>

      {/* Valor Previsto */}
      <p className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        {prediction.predicted}
      </p>

      {/* Descrição (se houver) */}
      {prediction.description && (
        <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
          {prediction.description}
        </p>
      )}

      {/* Barra de Confiança */}
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
          Confiança: {prediction.confidence}%
        </span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${prediction.confidence}%` }}
          transition={{ delay: delay + 0.2, duration: 0.8, ease: 'easeOut' }}
          className={`h-2 rounded-full ${getConfidenceColor()}`}
        />
      </div>
    </motion.div>
  );
}
