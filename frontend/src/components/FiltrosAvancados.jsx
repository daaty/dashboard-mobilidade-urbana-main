import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Filter, 
  Calendar, 
  MapPin, 
  Users, 
  Car, 
  X, 
  Search,
  RotateCcw,
  Download,
  Eye,
  EyeOff
} from 'lucide-react';

export function FiltrosAvancados({ onFilterChange, data }) {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState({
    dateRange: {
      start: '',
      end: '',
      preset: 'last7days'
    },
    cities: [],
    drivers: [],
    status: [],
    revenue: {
      min: '',
      max: ''
    },
    rating: {
      min: '',
      max: ''
    }
  });

  const [availableOptions, setAvailableOptions] = useState({
    cities: ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'],
    drivers: ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Lima'],
    status: ['Concluída', 'Cancelada', 'Perdida', 'Em Andamento']
  });

  const datePresets = [
    { value: 'today', label: 'Hoje' },
    { value: 'yesterday', label: 'Ontem' },
    { value: 'last7days', label: 'Últimos 7 dias' },
    { value: 'last30days', label: 'Últimos 30 dias' },
    { value: 'thisMonth', label: 'Este mês' },
    { value: 'lastMonth', label: 'Mês passado' },
    { value: 'custom', label: 'Personalizado' }
  ];

  const handleFilterChange = (category, key, value) => {
    const newFilters = {
      ...filters,
      [category]: {
        ...filters[category],
        [key]: value
      }
    };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleArrayFilterChange = (category, value, checked) => {
    const currentValues = filters[category] || [];
    const newValues = checked 
      ? [...currentValues, value]
      : currentValues.filter(v => v !== value);
    
    const newFilters = { ...filters, [category]: newValues };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handlePresetDateChange = (preset) => {
    let start = '';
    let end = '';
    const now = new Date();
    
    switch (preset) {
      case 'today':
        start = end = now.toISOString().split('T')[0];
        break;
      case 'yesterday':
        const yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        start = end = yesterday.toISOString().split('T')[0];
        break;
      case 'last7days':
        const last7 = new Date(now);
        last7.setDate(last7.getDate() - 7);
        start = last7.toISOString().split('T')[0];
        end = now.toISOString().split('T')[0];
        break;
      case 'last30days':
        const last30 = new Date(now);
        last30.setDate(last30.getDate() - 30);
        start = last30.toISOString().split('T')[0];
        end = now.toISOString().split('T')[0];
        break;
      case 'thisMonth':
        start = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
        end = now.toISOString().split('T')[0];
        break;
      case 'lastMonth':
        const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        const lastMonthEnd = new Date(now.getFullYear(), now.getMonth(), 0);
        start = lastMonth.toISOString().split('T')[0];
        end = lastMonthEnd.toISOString().split('T')[0];
        break;
      default:
        break;
    }

    const newFilters = {
      ...filters,
      dateRange: { start, end, preset }
    };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const clearAllFilters = () => {
    const emptyFilters = {
      dateRange: { start: '', end: '', preset: 'last7days' },
      cities: [],
      drivers: [],
      status: [],
      revenue: { min: '', max: '' },
      rating: { min: '', max: '' }
    };
    setFilters(emptyFilters);
    onFilterChange?.(emptyFilters);
  };

  const exportFilteredData = () => {
    // Simular exportação dos dados filtrados
    const exportData = {
      filters,
      timestamp: new Date().toISOString(),
      totalRecords: Math.floor(Math.random() * 1000) + 100
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `filtered-data-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.cities.length > 0) count++;
    if (filters.drivers.length > 0) count++;
    if (filters.status.length > 0) count++;
    if (filters.revenue.min || filters.revenue.max) count++;
    if (filters.rating.min || filters.rating.max) count++;
    if (filters.dateRange.preset !== 'last7days') count++;
    return count;
  };

  return (
    <div className="relative">
      {/* Filter Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-all ${
          isOpen || getActiveFiltersCount() > 0
            ? 'bg-blue-50 border-blue-300 text-blue-700'
            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
        }`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Filter className="w-4 h-4" />
        <span>Filtros</span>
        {getActiveFiltersCount() > 0 && (
          <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
            {getActiveFiltersCount()}
          </span>
        )}
      </motion.button>

      {/* Filter Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-xl z-50"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Filtros Avançados</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 space-y-6 max-h-96 overflow-y-auto">
              {/* Date Range */}
              <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
                  <Calendar className="w-4 h-4" />
                  <span>Período</span>
                </label>
                
                <div className="space-y-3">
                  <select
                    value={filters.dateRange.preset}
                    onChange={(e) => handlePresetDateChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    {datePresets.map(preset => (
                      <option key={preset.value} value={preset.value}>
                        {preset.label}
                      </option>
                    ))}
                  </select>

                  {filters.dateRange.preset === 'custom' && (
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="date"
                        value={filters.dateRange.start}
                        onChange={(e) => handleFilterChange('dateRange', 'start', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                      />
                      <input
                        type="date"
                        value={filters.dateRange.end}
                        onChange={(e) => handleFilterChange('dateRange', 'end', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Cities */}
              <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
                  <MapPin className="w-4 h-4" />
                  <span>Cidades</span>
                </label>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {availableOptions.cities.map(city => (
                    <label key={city} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.cities.includes(city)}
                        onChange={(e) => handleArrayFilterChange('cities', city, e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span>{city}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Drivers */}
              <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
                  <Users className="w-4 h-4" />
                  <span>Motoristas</span>
                </label>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {availableOptions.drivers.map(driver => (
                    <label key={driver} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.drivers.includes(driver)}
                        onChange={(e) => handleArrayFilterChange('drivers', driver, e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span>{driver}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Status */}
              <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
                  <Car className="w-4 h-4" />
                  <span>Status</span>
                </label>
                <div className="space-y-2">
                  {availableOptions.status.map(status => (
                    <label key={status} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.status.includes(status)}
                        onChange={(e) => handleArrayFilterChange('status', status, e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span>{status}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Revenue Range */}
              <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
                  <span>Faixa de Receita (R$)</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="Mín"
                    value={filters.revenue.min}
                    onChange={(e) => handleFilterChange('revenue', 'min', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                  <input
                    type="number"
                    placeholder="Máx"
                    value={filters.revenue.max}
                    onChange={(e) => handleFilterChange('revenue', 'max', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>
              </div>

              {/* Rating Range */}
              <div>
                <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-3">
                  <span>Faixa de Avaliação</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="Mín"
                    min="1"
                    max="5"
                    step="0.1"
                    value={filters.rating.min}
                    onChange={(e) => handleFilterChange('rating', 'min', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                  <input
                    type="number"
                    placeholder="Máx"
                    min="1"
                    max="5"
                    step="0.1"
                    value={filters.rating.max}
                    onChange={(e) => handleFilterChange('rating', 'max', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 p-4 flex justify-between">
              <button
                onClick={clearAllFilters}
                className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Limpar</span>
              </button>

              <div className="flex space-x-2">
                <button
                  onClick={exportFilteredData}
                  className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  <Download className="w-4 h-4" />
                  <span>Exportar</span>
                </button>
                
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Aplicar
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Active Filters Display */}
      {getActiveFiltersCount() > 0 && !isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute top-full left-0 mt-2 flex flex-wrap gap-2"
        >
          {filters.cities.map(city => (
            <span
              key={`city-${city}`}
              className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
            >
              <MapPin className="w-3 h-3 mr-1" />
              {city}
              <button
                onClick={() => handleArrayFilterChange('cities', city, false)}
                className="ml-1 hover:text-blue-600"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          
          {filters.status.map(status => (
            <span
              key={`status-${status}`}
              className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
            >
              <Car className="w-3 h-3 mr-1" />
              {status}
              <button
                onClick={() => handleArrayFilterChange('status', status, false)}
                className="ml-1 hover:text-green-600"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </motion.div>
      )}
    </div>
  );
}
