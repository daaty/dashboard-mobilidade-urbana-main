import React from 'react';
import { motion } from 'framer-motion';

/**
 * Componente de filtro de período para a aba Performance
 * Permite selecionar entre: Hoje, 7 dias, 30 dias, 90 dias
 */
export function PerformanceFilter({ period, onPeriodChange, loading }) {
  const periods = [
    { value: 'today', label: 'Hoje', shortLabel: 'Hoje' },
    { value: '7_days', label: 'Últimos 7 dias', shortLabel: '7d' },
    { value: '30_days', label: 'Últimos 30 dias', shortLabel: '30d' },
    { value: '90_days', label: 'Últimos 90 dias', shortLabel: '90d' }
  ];

  return (
    <div className="flex items-center space-x-2">
      <label className="text-sm font-medium text-gray-700 dark:text-gray-300 hidden sm:block">
        Período:
      </label>
      
      {/* Desktop: Dropdown */}
      <select
        value={period}
        onChange={(e) => onPeriodChange(e.target.value)}
        disabled={loading}
        className="hidden sm:block px-4 py-2 border border-gray-300 dark:border-gray-600 
                   rounded-lg bg-white dark:bg-gray-800 
                   text-gray-900 dark:text-gray-100 
                   focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all duration-200"
      >
        {periods.map((p) => (
          <option key={p.value} value={p.value}>
            {p.label}
          </option>
        ))}
      </select>

      {/* Mobile: Botões */}
      <div className="flex sm:hidden space-x-1">
        {periods.map((p) => (
          <motion.button
            key={p.value}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onPeriodChange(p.value)}
            disabled={loading}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
              ${period === p.value
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
          >
            {p.shortLabel}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
