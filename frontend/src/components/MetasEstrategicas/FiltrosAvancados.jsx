import React, { useState, useEffect } from 'react';
import { Filter, X, Calendar, MapPin, BarChart3, RefreshCw } from 'lucide-react';

/**
 * 📊 FILTROS AVANÇADOS - DASHBOARD METAS ESTRATÉGICAS
 * 
 * Componente para filtros globais do dashboard executivo
 * 
 * Props:
 * @param {function} onFilterChange - Callback quando filtros mudarem
 * @param {object} initialFilters - Filtros iniciais
 */
const FiltrosAvancados = ({ onFilterChange, initialFilters = {} }) => {
  // ========== ESTADOS ==========
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeFilters, setActiveFilters] = useState({
    cidades: initialFilters.cidades || [],
    periodos: initialFilters.periodos || [],
    dataInicio: initialFilters.dataInicio || '',
    dataFim: initialFilters.dataFim || '',
    metricas: initialFilters.metricas || ['corridas', 'receita', 'motoristas'],
    atingimentoMin: initialFilters.atingimentoMin || 0,
  });

  // Lista de cidades disponíveis
  const cidadesDisponiveis = [
    { id: 1, nome: 'Peixoto de Azevedo', sigla: 'PXT' },
    { id: 2, nome: 'Nova Monte Verde', sigla: 'NMV' },
    { id: 3, nome: 'Matupá', sigla: 'MTP' },
    { id: 4, nome: 'Guarantã do Norte', sigla: 'GTN' },
    { id: 5, nome: 'Nova Bandeirantes', sigla: 'NBD' },
  ];

  // Períodos disponíveis
  const periodosDisponiveis = [
    { value: 2, label: '2 meses' },
    { value: 3, label: '3 meses' },
    { value: 6, label: '6 meses' },
    { value: 12, label: '12 meses' },
  ];

  // Métricas disponíveis
  const metricasDisponiveis = [
    { value: 'corridas', label: 'Corridas', color: 'blue' },
    { value: 'receita', label: 'Receita', color: 'green' },
    { value: 'motoristas', label: 'Motoristas', color: 'purple' },
  ];

  // ========== HANDLERS ==========
  
  // Toggle cidade
  const toggleCidade = (cidadeId) => {
    setActiveFilters(prev => {
      const cidades = prev.cidades.includes(cidadeId)
        ? prev.cidades.filter(id => id !== cidadeId)
        : [...prev.cidades, cidadeId];
      return { ...prev, cidades };
    });
  };

  // Toggle período
  const togglePeriodo = (periodo) => {
    setActiveFilters(prev => {
      const periodos = prev.periodos.includes(periodo)
        ? prev.periodos.filter(p => p !== periodo)
        : [...prev.periodos, periodo];
      return { ...prev, periodos };
    });
  };

  // Toggle métrica
  const toggleMetrica = (metrica) => {
    setActiveFilters(prev => {
      const metricas = prev.metricas.includes(metrica)
        ? prev.metricas.filter(m => m !== metrica)
        : [...prev.metricas, metrica];
      return { ...prev, metricas };
    });
  };

  // Atualizar data início
  const handleDataInicioChange = (e) => {
    setActiveFilters(prev => ({ ...prev, dataInicio: e.target.value }));
  };

  // Atualizar data fim
  const handleDataFimChange = (e) => {
    setActiveFilters(prev => ({ ...prev, dataFim: e.target.value }));
  };

  // Atualizar atingimento mínimo
  const handleAtingimentoChange = (e) => {
    setActiveFilters(prev => ({ ...prev, atingimentoMin: parseInt(e.target.value) }));
  };

  // Limpar todos os filtros
  const limparFiltros = () => {
    const defaultFilters = {
      cidades: [],
      periodos: [],
      dataInicio: '',
      dataFim: '',
      metricas: ['corridas', 'receita', 'motoristas'],
      atingimentoMin: 0,
    };
    setActiveFilters(defaultFilters);
  };

  // Aplicar filtros (notificar componente pai)
  useEffect(() => {
    if (onFilterChange) {
      onFilterChange(activeFilters);
    }
  }, [activeFilters]);

  // ========== CONTADOR DE FILTROS ATIVOS ==========
  const contarFiltrosAtivos = () => {
    let count = 0;
    if (activeFilters.cidades.length > 0) count++;
    if (activeFilters.periodos.length > 0) count++;
    if (activeFilters.dataInicio || activeFilters.dataFim) count++;
    if (activeFilters.metricas.length !== 3) count++; // Se não tiver todas
    if (activeFilters.atingimentoMin > 0) count++;
    return count;
  };

  const filtrosAtivos = contarFiltrosAtivos();

  // ========== RENDER ==========
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 mb-6">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <Filter className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Filtros Avançados
          </h3>
          {filtrosAtivos > 0 && (
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
              {filtrosAtivos} {filtrosAtivos === 1 ? 'filtro' : 'filtros'} ativo{filtrosAtivos !== 1 && 's'}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {filtrosAtivos > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                limparFiltros();
              }}
              className="flex items-center gap-1 px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors"
            >
              <X className="w-4 h-4" />
              Limpar
            </button>
          )}
          <span className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </div>
      </div>

      {/* Conteúdo dos Filtros */}
      {isExpanded && (
        <div className="p-6 pt-2 border-t border-gray-100 space-y-6">
          
          {/* 1. FILTRO POR CIDADES */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-4 h-4 text-gray-600" />
              <label className="text-sm font-medium text-gray-700">
                Cidades
              </label>
              <span className="text-xs text-gray-500">
                ({activeFilters.cidades.length} selecionada{activeFilters.cidades.length !== 1 && 's'})
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {cidadesDisponiveis.map(cidade => (
                <button
                  key={cidade.id}
                  onClick={() => toggleCidade(cidade.id)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    activeFilters.cidades.includes(cidade.id)
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cidade.sigla}
                </button>
              ))}
              <button
                onClick={() => {
                  const todasIds = cidadesDisponiveis.map(c => c.id);
                  setActiveFilters(prev => ({
                    ...prev,
                    cidades: activeFilters.cidades.length === todasIds.length ? [] : todasIds
                  }));
                }}
                className="px-3 py-2 rounded-md text-sm font-medium bg-purple-100 text-purple-700 hover:bg-purple-200 transition-colors"
              >
                {activeFilters.cidades.length === cidadesDisponiveis.length ? 'Desmarcar' : 'Todas'}
              </button>
            </div>
          </div>

          {/* 2. FILTRO POR PERÍODOS */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Calendar className="w-4 h-4 text-gray-600" />
              <label className="text-sm font-medium text-gray-700">
                Períodos
              </label>
              <span className="text-xs text-gray-500">
                ({activeFilters.periodos.length} selecionado{activeFilters.periodos.length !== 1 && 's'})
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {periodosDisponiveis.map(periodo => (
                <button
                  key={periodo.value}
                  onClick={() => togglePeriodo(periodo.value)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    activeFilters.periodos.includes(periodo.value)
                      ? 'bg-green-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {periodo.label}
                </button>
              ))}
            </div>
          </div>

          {/* 3. FILTRO POR FAIXA DE DATAS */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Calendar className="w-4 h-4 text-gray-600" />
              <label className="text-sm font-medium text-gray-700">
                Faixa de Datas
              </label>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-600 mb-1 block">Data Início</label>
                <input
                  type="date"
                  value={activeFilters.dataInicio}
                  onChange={handleDataInicioChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-600 mb-1 block">Data Fim</label>
                <input
                  type="date"
                  value={activeFilters.dataFim}
                  onChange={handleDataFimChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* 4. FILTRO POR MÉTRICAS */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="w-4 h-4 text-gray-600" />
              <label className="text-sm font-medium text-gray-700">
                Métricas Exibidas
              </label>
            </div>
            <div className="flex flex-wrap gap-2">
              {metricasDisponiveis.map(metrica => {
                const colorClasses = {
                  blue: activeFilters.metricas.includes(metrica.value) 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200',
                  green: activeFilters.metricas.includes(metrica.value)
                    ? 'bg-green-600 text-white'
                    : 'bg-green-100 text-green-700 hover:bg-green-200',
                  purple: activeFilters.metricas.includes(metrica.value)
                    ? 'bg-purple-600 text-white'
                    : 'bg-purple-100 text-purple-700 hover:bg-purple-200',
                };
                
                return (
                  <button
                    key={metrica.value}
                    onClick={() => toggleMetrica(metrica.value)}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                      colorClasses[metrica.color]
                    }`}
                  >
                    {metrica.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 5. FILTRO POR ATINGIMENTO MÍNIMO */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="w-4 h-4 text-gray-600" />
              <label className="text-sm font-medium text-gray-700">
                Atingimento Mínimo: {activeFilters.atingimentoMin}%
              </label>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="100"
                step="10"
                value={activeFilters.atingimentoMin}
                onChange={handleAtingimentoChange}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <input
                type="number"
                min="0"
                max="100"
                value={activeFilters.atingimentoMin}
                onChange={handleAtingimentoChange}
                className="w-20 px-3 py-2 border border-gray-300 rounded-md text-sm text-center focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

        </div>
      )}

      {/* Footer com Resumo dos Filtros Ativos */}
      {!isExpanded && filtrosAtivos > 0 && (
        <div className="px-4 pb-4 flex flex-wrap gap-2">
          {activeFilters.cidades.length > 0 && (
            <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
              {activeFilters.cidades.length} cidade{activeFilters.cidades.length !== 1 && 's'}
            </span>
          )}
          {activeFilters.periodos.length > 0 && (
            <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded">
              {activeFilters.periodos.length} período{activeFilters.periodos.length !== 1 && 's'}
            </span>
          )}
          {(activeFilters.dataInicio || activeFilters.dataFim) && (
            <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded">
              Faixa de datas
            </span>
          )}
          {activeFilters.atingimentoMin > 0 && (
            <span className="text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded">
              Atingimento ≥ {activeFilters.atingimentoMin}%
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default FiltrosAvancados;
