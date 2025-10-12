import React from 'react';
import { TrendingUp, TrendingDown, CheckCircle, AlertTriangle, Clock, Target } from 'lucide-react';

/**
 * Componente de Indicador de Progresso
 * Visualiza o progresso de uma meta (realizado vs meta)
 * 
 * Modos de exibição:
 * - 'bar': Barra de progresso horizontal
 * - 'circle': Círculo de progresso
 * - 'card': Card completo com detalhes
 * - 'inline': Versão compacta inline
 * 
 * @param {number} meta - Valor da meta/objetivo
 * @param {number} realizado - Valor realizado
 * @param {string} label - Rótulo (ex: "Motoristas", "Corridas")
 * @param {string} status - Status calculado (concluido/no_prazo/atencao/atrasado)
 * @param {string} mode - Modo de exibição (bar/circle/card/inline)
 * @param {boolean} showPercentage - Mostrar percentual
 * @param {boolean} showValues - Mostrar valores numéricos
 * @param {boolean} showStatus - Mostrar badge de status
 * @param {string} size - Tamanho (sm/md/lg)
 */
const ProgressIndicator = ({
  meta = 0,
  realizado = 0,
  label = '',
  status = 'atrasado',
  mode = 'bar',
  showPercentage = true,
  showValues = true,
  showStatus = true,
  size = 'md',
}) => {
  // Calcular progresso
  const progresso = meta > 0 ? (realizado / meta) * 100 : 0;
  const progressoClamped = Math.min(progresso, 100);
  
  // Configurações de status
  const statusConfig = {
    concluido: {
      color: 'green',
      bgColor: 'bg-green-500',
      textColor: 'text-green-700',
      borderColor: 'border-green-500',
      label: 'Concluído',
      icon: CheckCircle,
      emoji: '✅',
    },
    no_prazo: {
      color: 'blue',
      bgColor: 'bg-blue-500',
      textColor: 'text-blue-700',
      borderColor: 'border-blue-500',
      label: 'No Prazo',
      icon: TrendingUp,
      emoji: '🔵',
    },
    atencao: {
      color: 'yellow',
      bgColor: 'bg-yellow-500',
      textColor: 'text-yellow-700',
      borderColor: 'border-yellow-500',
      label: 'Atenção',
      icon: AlertTriangle,
      emoji: '⚠️',
    },
    atrasado: {
      color: 'red',
      bgColor: 'bg-red-500',
      textColor: 'text-red-700',
      borderColor: 'border-red-500',
      label: 'Atrasado',
      icon: Clock,
      emoji: '🔴',
    },
  };
  
  const config = statusConfig[status] || statusConfig.atrasado;
  const StatusIcon = config.icon;
  
  // Configurações de tamanho
  const sizeConfig = {
    sm: {
      barHeight: 'h-2',
      fontSize: 'text-xs',
      iconSize: 'h-3 w-3',
      padding: 'p-2',
    },
    md: {
      barHeight: 'h-4',
      fontSize: 'text-sm',
      iconSize: 'h-4 w-4',
      padding: 'p-3',
    },
    lg: {
      barHeight: 'h-6',
      fontSize: 'text-base',
      iconSize: 'h-5 w-5',
      padding: 'p-4',
    },
  };
  
  const sizeSettings = sizeConfig[size] || sizeConfig.md;
  
  // Formatar número
  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value || 0);
  };
  
  // Formatar percentual
  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(1)}%`;
  };
  
  // ========== MODO: BAR (Barra Horizontal) ==========
  if (mode === 'bar') {
    return (
      <div className="w-full">
        {/* Header */}
        {(label || showValues || showStatus) && (
          <div className="flex items-center justify-between mb-2">
            {/* Label */}
            {label && (
              <span className={`font-medium text-gray-700 ${sizeSettings.fontSize}`}>
                {label}
              </span>
            )}
            
            {/* Values e Status */}
            <div className="flex items-center gap-3">
              {showValues && (
                <span className={`text-gray-600 ${sizeSettings.fontSize}`}>
                  <span className="font-bold text-gray-900">{formatNumber(realizado)}</span>
                  <span className="text-gray-400 mx-1">/</span>
                  <span>{formatNumber(meta)}</span>
                </span>
              )}
              
              {showStatus && (
                <span className={`px-2 py-0.5 rounded-full ${sizeSettings.fontSize} font-medium bg-${config.color}-100 ${config.textColor} flex items-center gap-1`}>
                  <StatusIcon className={sizeSettings.iconSize} />
                  {config.label}
                </span>
              )}
            </div>
          </div>
        )}
        
        {/* Progress Bar */}
        <div className="relative">
          <div className={`w-full bg-gray-200 rounded-full ${sizeSettings.barHeight} overflow-hidden`}>
            <div
              className={`${config.bgColor} ${sizeSettings.barHeight} rounded-full transition-all duration-500 flex items-center justify-center`}
              style={{ width: `${progressoClamped}%` }}
            >
              {showPercentage && size !== 'sm' && progressoClamped > 15 && (
                <span className="text-white text-xs font-bold">
                  {formatPercentage(progresso)}
                </span>
              )}
            </div>
          </div>
          
          {/* Percentage label outside bar for small bars */}
          {showPercentage && (size === 'sm' || progressoClamped <= 15) && (
            <span className={`absolute -top-1 -right-1 ${sizeSettings.fontSize} font-bold ${config.textColor}`}>
              {formatPercentage(progresso)}
            </span>
          )}
        </div>
      </div>
    );
  }
  
  // ========== MODO: CIRCLE (Círculo de Progresso) ==========
  if (mode === 'circle') {
    const radius = size === 'sm' ? 30 : size === 'lg' ? 50 : 40;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (progressoClamped / 100) * circumference;
    
    return (
      <div className="flex flex-col items-center">
        <div className="relative">
          <svg
            width={radius * 2.5}
            height={radius * 2.5}
            viewBox={`0 0 ${radius * 2.5} ${radius * 2.5}`}
            className="transform -rotate-90"
          >
            {/* Background circle */}
            <circle
              cx={radius * 1.25}
              cy={radius * 1.25}
              r={radius}
              fill="none"
              stroke="#E5E7EB"
              strokeWidth={size === 'sm' ? 4 : size === 'lg' ? 8 : 6}
            />
            
            {/* Progress circle */}
            <circle
              cx={radius * 1.25}
              cy={radius * 1.25}
              r={radius}
              fill="none"
              stroke={`var(--${config.color}-500, ${config.bgColor.replace('bg-', '')})`}
              strokeWidth={size === 'sm' ? 4 : size === 'lg' ? 8 : 6}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-500"
              style={{
                stroke: config.color === 'green' ? '#10b981' :
                        config.color === 'blue' ? '#3b82f6' :
                        config.color === 'yellow' ? '#f59e0b' : '#ef4444'
              }}
            />
          </svg>
          
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {showPercentage && (
              <span className={`font-bold ${config.textColor} ${size === 'sm' ? 'text-lg' : size === 'lg' ? 'text-3xl' : 'text-2xl'}`}>
                {formatPercentage(progresso)}
              </span>
            )}
            {showStatus && size !== 'sm' && (
              <span className={`text-xs text-gray-600 mt-1`}>
                {config.emoji} {config.label}
              </span>
            )}
          </div>
        </div>
        
        {/* Label and values below circle */}
        {(label || showValues) && (
          <div className="mt-3 text-center">
            {label && (
              <p className={`font-medium text-gray-700 ${sizeSettings.fontSize}`}>
                {label}
              </p>
            )}
            {showValues && (
              <p className={`text-gray-600 ${sizeSettings.fontSize} mt-1`}>
                <span className="font-bold text-gray-900">{formatNumber(realizado)}</span>
                <span className="text-gray-400"> / </span>
                <span>{formatNumber(meta)}</span>
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
  
  // ========== MODO: CARD (Card Completo) ==========
  if (mode === 'card') {
    return (
      <div className={`bg-white rounded-lg border-2 ${config.borderColor} ${sizeSettings.padding} hover:shadow-lg transition-shadow`}>
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <Target className={`${sizeSettings.iconSize} ${config.textColor}`} />
            <h4 className={`font-bold text-gray-900 ${sizeSettings.fontSize}`}>
              {label || 'Meta'}
            </h4>
          </div>
          
          {showStatus && (
            <span className={`px-3 py-1 rounded-full text-xs font-medium bg-${config.color}-100 ${config.textColor} flex items-center gap-1`}>
              <StatusIcon className="h-3 w-3" />
              {config.label}
            </span>
          )}
        </div>
        
        {/* Values */}
        {showValues && (
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div>
              <p className="text-xs text-gray-500">Meta</p>
              <p className="text-lg font-bold text-gray-900">{formatNumber(meta)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Realizado</p>
              <p className={`text-lg font-bold ${config.textColor}`}>
                {formatNumber(realizado)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Progresso</p>
              <p className={`text-lg font-bold ${config.textColor}`}>
                {formatPercentage(progresso)}
              </p>
            </div>
          </div>
        )}
        
        {/* Progress Bar */}
        <div className={`w-full bg-gray-200 rounded-full ${sizeSettings.barHeight} overflow-hidden`}>
          <div
            className={`${config.bgColor} ${sizeSettings.barHeight} rounded-full transition-all duration-500`}
            style={{ width: `${progressoClamped}%` }}
          />
        </div>
        
        {/* Footer */}
        <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
          <span>{config.emoji} {config.label}</span>
          <span>
            {progresso >= 100 ? '🎉 Meta atingida!' :
             progresso >= 70 ? '👍 Bom andamento' :
             progresso >= 40 ? '⚠️ Precisa atenção' :
             '🚨 Requer ação'}
          </span>
        </div>
      </div>
    );
  }
  
  // ========== MODO: INLINE (Compacto) ==========
  if (mode === 'inline') {
    return (
      <div className="flex items-center gap-2">
        {/* Icon */}
        <StatusIcon className={`${sizeSettings.iconSize} ${config.textColor} flex-shrink-0`} />
        
        {/* Label */}
        {label && (
          <span className={`font-medium text-gray-700 ${sizeSettings.fontSize} flex-shrink-0`}>
            {label}:
          </span>
        )}
        
        {/* Mini progress bar */}
        <div className="flex-1 min-w-[60px] max-w-[120px]">
          <div className={`w-full bg-gray-200 rounded-full ${sizeSettings.barHeight}`}>
            <div
              className={`${config.bgColor} ${sizeSettings.barHeight} rounded-full transition-all duration-500`}
              style={{ width: `${progressoClamped}%` }}
            />
          </div>
        </div>
        
        {/* Percentage */}
        {showPercentage && (
          <span className={`${sizeSettings.fontSize} font-bold ${config.textColor} flex-shrink-0`}>
            {formatPercentage(progresso)}
          </span>
        )}
        
        {/* Values */}
        {showValues && (
          <span className={`${sizeSettings.fontSize} text-gray-600 flex-shrink-0`}>
            ({formatNumber(realizado)}/{formatNumber(meta)})
          </span>
        )}
      </div>
    );
  }
  
  // Fallback para mode desconhecido
  return (
    <div className="text-red-600 text-sm">
      ⚠️ Modo inválido: {mode}
    </div>
  );
};

/**
 * Componente de Múltiplos Indicadores
 * Exibe vários indicadores de progresso lado a lado
 */
export const MultiProgressIndicator = ({ items = [], mode = 'bar', size = 'md' }) => {
  if (!items || items.length === 0) {
    return (
      <div className="text-gray-500 text-sm italic">
        Nenhum indicador disponível
      </div>
    );
  }
  
  return (
    <div className={`space-y-${size === 'sm' ? '2' : size === 'lg' ? '6' : '4'}`}>
      {items.map((item, index) => (
        <ProgressIndicator
          key={index}
          meta={item.meta}
          realizado={item.realizado}
          label={item.label}
          status={item.status}
          mode={mode}
          size={size}
          showPercentage={item.showPercentage !== false}
          showValues={item.showValues !== false}
          showStatus={item.showStatus !== false}
        />
      ))}
    </div>
  );
};

export default ProgressIndicator;
