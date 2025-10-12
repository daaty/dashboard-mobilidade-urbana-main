import React, { useState } from 'react';
import { 
  AlertTriangle, 
  AlertCircle, 
  Info, 
  CheckCircle,
  X,
  Filter,
  TrendingDown,
  DollarSign,
  FileText,
  Star,
  Users
} from 'lucide-react';

/**
 * Painel de Alertas
 * Exibe alertas gerados pelo sistema de forma organizada
 * 
 * Tipos de alertas:
 * - progresso: Motoristas/corridas atrasados
 * - orcamento: Orçamento crítico/em atenção
 * - documentacao: Baixa taxa de documentação
 * - performance: Cancelamentos altos, rating baixo
 * - rating: Problemas com avaliações
 * 
 * Níveis:
 * - danger: Crítico (vermelho)
 * - warning: Atenção (amarelo)
 * - info: Informativo (azul)
 * - success: Sucesso (verde)
 * 
 * @param {Array} alertas - Lista de alertas
 * @param {boolean} dismissible - Permitir dispensar alertas
 * @param {boolean} showFilters - Mostrar filtros
 * @param {Function} onDismiss - Callback ao dispensar alerta
 * @param {string} size - Tamanho (sm/md/lg)
 */
const AlertsPanel = ({
  alertas = [],
  dismissible = true,
  showFilters = true,
  onDismiss,
  size = 'md',
}) => {
  const [filtroTipo, setFiltroTipo] = useState('todos');
  const [filtroNivel, setFiltroNivel] = useState('todos');
  const [alertasDismissed, setAlertasDismissed] = useState(new Set());
  
  // Configurações de nível
  const nivelConfig = {
    danger: {
      bgColor: 'bg-red-50',
      borderColor: 'border-red-300',
      textColor: 'text-red-800',
      iconColor: 'text-red-600',
      icon: AlertCircle,
      label: 'Crítico',
      emoji: '🚨',
    },
    warning: {
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-300',
      textColor: 'text-yellow-800',
      iconColor: 'text-yellow-600',
      icon: AlertTriangle,
      label: 'Atenção',
      emoji: '⚠️',
    },
    info: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-300',
      textColor: 'text-blue-800',
      iconColor: 'text-blue-600',
      icon: Info,
      label: 'Info',
      emoji: 'ℹ️',
    },
    success: {
      bgColor: 'bg-green-50',
      borderColor: 'border-green-300',
      textColor: 'text-green-800',
      iconColor: 'text-green-600',
      icon: CheckCircle,
      label: 'Sucesso',
      emoji: '✅',
    },
  };
  
  // Configurações de tipo
  const tipoConfig = {
    progresso: {
      icon: TrendingDown,
      label: 'Progresso',
      color: 'red',
    },
    orcamento: {
      icon: DollarSign,
      label: 'Orçamento',
      color: 'yellow',
    },
    documentacao: {
      icon: FileText,
      label: 'Documentação',
      color: 'blue',
    },
    performance: {
      icon: Star,
      label: 'Performance',
      color: 'orange',
    },
    rating: {
      icon: Star,
      label: 'Avaliações',
      color: 'purple',
    },
  };
  
  // Configurações de tamanho
  const sizeConfig = {
    sm: {
      padding: 'p-2',
      fontSize: 'text-xs',
      iconSize: 'h-4 w-4',
      gap: 'gap-2',
    },
    md: {
      padding: 'p-4',
      fontSize: 'text-sm',
      iconSize: 'h-5 w-5',
      gap: 'gap-3',
    },
    lg: {
      padding: 'p-6',
      fontSize: 'text-base',
      iconSize: 'h-6 w-6',
      gap: 'gap-4',
    },
  };
  
  const sizeSettings = sizeConfig[size] || sizeConfig.md;
  
  // Filtrar alertas
  const alertasFiltrados = alertas.filter(alerta => {
    // Filtro dismissed
    if (alertasDismissed.has(alerta.id || `${alerta.tipo}_${alerta.mensagem}`)) {
      return false;
    }
    
    // Filtro tipo
    if (filtroTipo !== 'todos' && alerta.tipo !== filtroTipo) {
      return false;
    }
    
    // Filtro nível
    if (filtroNivel !== 'todos' && alerta.nivel !== filtroNivel) {
      return false;
    }
    
    return true;
  });
  
  // Contar por tipo e nível
  const contagemTipo = alertas.reduce((acc, alerta) => {
    acc[alerta.tipo] = (acc[alerta.tipo] || 0) + 1;
    return acc;
  }, {});
  
  const contagemNivel = alertas.reduce((acc, alerta) => {
    acc[alerta.nivel] = (acc[alerta.nivel] || 0) + 1;
    return acc;
  }, {});
  
  // Handler para dismissar alerta
  const handleDismiss = (alerta) => {
    const alertaId = alerta.id || `${alerta.tipo}_${alerta.mensagem}`;
    setAlertasDismissed(prev => new Set([...prev, alertaId]));
    
    if (onDismiss) {
      onDismiss(alerta);
    }
  };
  
  // Renderizar dados do alerta (se existirem)
  const renderAlertaData = (dados) => {
    if (!dados || Object.keys(dados).length === 0) return null;
    
    return (
      <div className="mt-3 pt-3 border-t border-gray-300 grid grid-cols-2 gap-2">
        {dados.cidade && (
          <div className="text-xs">
            <span className="text-gray-500">Cidade:</span>{' '}
            <span className="font-medium">{dados.cidade}</span>
          </div>
        )}
        {dados.meta !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Meta:</span>{' '}
            <span className="font-medium">{dados.meta}</span>
          </div>
        )}
        {dados.realizado !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Realizado:</span>{' '}
            <span className="font-medium">{dados.realizado}</span>
          </div>
        )}
        {dados.progresso !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Progresso:</span>{' '}
            <span className="font-medium">{dados.progresso.toFixed(1)}%</span>
          </div>
        )}
        {dados.percentual !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Percentual:</span>{' '}
            <span className="font-medium">{dados.percentual.toFixed(1)}%</span>
          </div>
        )}
        {dados.previsto !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Previsto:</span>{' '}
            <span className="font-medium">R$ {dados.previsto.toLocaleString('pt-BR')}</span>
          </div>
        )}
        {dados.gasto !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Gasto:</span>{' '}
            <span className="font-medium">R$ {dados.gasto.toLocaleString('pt-BR')}</span>
          </div>
        )}
        {dados.saldo !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Saldo:</span>{' '}
            <span className="font-medium">R$ {dados.saldo.toLocaleString('pt-BR')}</span>
          </div>
        )}
        {dados.taxa !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Taxa:</span>{' '}
            <span className="font-medium">{dados.taxa.toFixed(1)}%</span>
          </div>
        )}
        {dados.rating !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">Rating:</span>{' '}
            <span className="font-medium">⭐ {dados.rating.toFixed(1)}</span>
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-orange-600" />
            Alertas do Sistema
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {alertasFiltrados.length} de {alertas.length} alertas
            {alertasDismissed.size > 0 && ` (${alertasDismissed.size} dispensados)`}
          </p>
        </div>
        
        {/* Resumo por nível */}
        <div className="flex items-center gap-2">
          {contagemNivel.danger > 0 && (
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
              🚨 {contagemNivel.danger} Críticos
            </span>
          )}
          {contagemNivel.warning > 0 && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
              ⚠️ {contagemNivel.warning} Atenção
            </span>
          )}
          {contagemNivel.info > 0 && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              ℹ️ {contagemNivel.info} Info
            </span>
          )}
        </div>
      </div>
      
      {/* Filtros */}
      {showFilters && alertas.length > 3 && (
        <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <Filter className="h-5 w-5 text-gray-600" />
          
          {/* Filtro por Tipo */}
          <div className="flex-1">
            <label className="text-xs text-gray-600 mb-1 block">Tipo de Alerta</label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className="w-full px-3 py-1.5 border border-gray-300 rounded text-sm"
            >
              <option value="todos">Todos os tipos ({alertas.length})</option>
              {Object.keys(contagemTipo).map(tipo => (
                <option key={tipo} value={tipo}>
                  {tipoConfig[tipo]?.label || tipo} ({contagemTipo[tipo]})
                </option>
              ))}
            </select>
          </div>
          
          {/* Filtro por Nível */}
          <div className="flex-1">
            <label className="text-xs text-gray-600 mb-1 block">Nível de Severidade</label>
            <select
              value={filtroNivel}
              onChange={(e) => setFiltroNivel(e.target.value)}
              className="w-full px-3 py-1.5 border border-gray-300 rounded text-sm"
            >
              <option value="todos">Todos os níveis ({alertas.length})</option>
              {Object.keys(contagemNivel).map(nivel => (
                <option key={nivel} value={nivel}>
                  {nivelConfig[nivel]?.emoji} {nivelConfig[nivel]?.label} ({contagemNivel[nivel]})
                </option>
              ))}
            </select>
          </div>
          
          {/* Limpar filtros */}
          {(filtroTipo !== 'todos' || filtroNivel !== 'todos') && (
            <button
              onClick={() => {
                setFiltroTipo('todos');
                setFiltroNivel('todos');
              }}
              className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
            >
              Limpar Filtros
            </button>
          )}
        </div>
      )}
      
      {/* Lista de Alertas */}
      {alertasFiltrados.length === 0 ? (
        <div className="text-center py-12 bg-green-50 rounded-lg border border-green-200">
          <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
          <p className="text-green-800 font-medium">
            {alertas.length === 0 
              ? '✨ Nenhum alerta no momento!'
              : '🎯 Nenhum alerta corresponde aos filtros'}
          </p>
          <p className="text-green-600 text-sm mt-2">
            {alertas.length === 0
              ? 'Todas as metas e processos estão em dia'
              : 'Ajuste os filtros acima para ver outros alertas'}
          </p>
        </div>
      ) : (
        <div className={`space-y-${size === 'sm' ? '2' : '3'}`}>
          {alertasFiltrados.map((alerta, index) => {
            const nivelConf = nivelConfig[alerta.nivel] || nivelConfig.warning;
            const tipoConf = tipoConfig[alerta.tipo] || tipoConfig.progresso;
            const NivelIcon = nivelConf.icon;
            const TipoIcon = tipoConf.icon;
            
            return (
              <div
                key={index}
                className={`
                  ${nivelConf.bgColor} 
                  border-2 ${nivelConf.borderColor} 
                  rounded-lg 
                  ${sizeSettings.padding}
                  hover:shadow-md 
                  transition-all
                  animate-fadeIn
                `}
              >
                <div className={`flex items-start ${sizeSettings.gap}`}>
                  {/* Ícone */}
                  <div className="flex-shrink-0">
                    <div className={`p-2 rounded-full bg-white border-2 ${nivelConf.borderColor}`}>
                      <NivelIcon className={`${sizeSettings.iconSize} ${nivelConf.iconColor}`} />
                    </div>
                  </div>
                  
                  {/* Conteúdo */}
                  <div className="flex-1 min-w-0">
                    {/* Header do alerta */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <TipoIcon className={`h-4 w-4 ${nivelConf.iconColor}`} />
                          <span className={`${sizeSettings.fontSize} font-medium ${nivelConf.textColor}`}>
                            {tipoConf.label}
                            {alerta.subtipo && ` - ${alerta.subtipo}`}
                          </span>
                          <span className={`px-2 py-0.5 rounded-full text-xs bg-white ${nivelConf.textColor} border ${nivelConf.borderColor}`}>
                            {nivelConf.emoji} {nivelConf.label}
                          </span>
                        </div>
                        
                        {/* Mensagem */}
                        <p className={`${sizeSettings.fontSize} ${nivelConf.textColor} font-medium`}>
                          {alerta.icone && `${alerta.icone} `}
                          {alerta.mensagem}
                        </p>
                      </div>
                      
                      {/* Botão de dismiss */}
                      {dismissible && (
                        <button
                          onClick={() => handleDismiss(alerta)}
                          className={`p-1 rounded hover:bg-white/50 transition-colors`}
                          title="Dispensar alerta"
                        >
                          <X className={`h-4 w-4 ${nivelConf.iconColor}`} />
                        </button>
                      )}
                    </div>
                    
                    {/* Cidade (se aplicável) */}
                    {alerta.cidade && (
                      <p className="text-xs text-gray-600 mb-2">
                        📍 Cidade: <span className="font-medium">{alerta.cidade}</span>
                      </p>
                    )}
                    
                    {/* Dados detalhados */}
                    {alerta.dados && renderAlertaData(alerta.dados)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {/* Footer com estatísticas */}
      {alertasFiltrados.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">📊 Resumo por Categoria</h4>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {Object.entries(contagemTipo).map(([tipo, count]) => {
              const conf = tipoConfig[tipo];
              const Icon = conf?.icon || AlertCircle;
              
              return (
                <div key={tipo} className="flex items-center gap-2">
                  <Icon className={`h-4 w-4 text-${conf?.color || 'gray'}-600`} />
                  <div>
                    <p className="text-xs text-gray-600">{conf?.label || tipo}</p>
                    <p className="text-sm font-bold text-gray-900">{count}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;
