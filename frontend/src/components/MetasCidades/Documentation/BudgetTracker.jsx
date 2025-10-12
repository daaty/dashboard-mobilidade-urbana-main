import React from 'react';
import { DollarSign, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, FileCheck } from 'lucide-react';

/**
 * Componente de Acompanhamento de Orçamento
 * Visualiza o fluxo financeiro: Previsto → Empenhado → Pago → Liquidado
 * 
 * @param {Object} orcamento - Dados de orçamento
 * @param {number} orcamento.previsto - Valor previsto (meta)
 * @param {number} orcamento.empenhado - Valor empenhado (comprometido)
 * @param {number} orcamento.pago - Valor pago (transferido)
 * @param {number} orcamento.liquidado - Valor liquidado (finalizado)
 * @param {number} orcamento.gasto_real - Gasto real acumulado
 * @param {number} orcamento.saldo - Saldo disponível
 * @param {number} orcamento.percentual_utilizado - % do orçamento utilizado
 * @param {Array} alertas - Alertas financeiros
 * @param {string} fase - Fase atual
 * @param {string} cidade - Cidade (opcional)
 * @param {boolean} showDetails - Mostrar detalhes expandidos
 */
const BudgetTracker = ({ 
  orcamento = {}, 
  alertas = [], 
  fase, 
  cidade,
  showDetails = true 
}) => {
  // Valores com fallback
  const {
    previsto = 0,
    empenhado = 0,
    pago = 0,
    liquidado = 0,
    gasto_real = 0,
    saldo = 0,
    percentual_utilizado = 0,
  } = orcamento;
  
  // Calcular percentuais de cada etapa em relação ao previsto
  const percentualEmpenhado = previsto > 0 ? (empenhado / previsto) * 100 : 0;
  const percentualPago = previsto > 0 ? (pago / previsto) * 100 : 0;
  const percentualLiquidado = previsto > 0 ? (liquidado / previsto) * 100 : 0;
  
  // Determinar nível de alerta
  const getNivelAlerta = (percentual) => {
    if (percentual >= 90) return { nivel: 'critico', color: 'red', icon: AlertTriangle };
    if (percentual >= 75) return { nivel: 'atencao', color: 'yellow', icon: AlertTriangle };
    if (percentual >= 50) return { nivel: 'normal', color: 'blue', icon: TrendingUp };
    return { nivel: 'ok', color: 'green', icon: CheckCircle };
  };
  
  const alerta = getNivelAlerta(percentual_utilizado);
  const AlertIcon = alerta.icon;
  
  // Formatar moeda
  const formatCurrency = (value) => {
    const numValue = parseFloat(value) || 0;
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numValue);
  };
  
  // Formatar percentual
  const formatPercentage = (value) => {
    const numValue = parseFloat(value) || 0;
    return `${numValue.toFixed(1)}%`;
  };
  
  // Estágios do fluxo financeiro
  const stages = [
    {
      id: 'previsto',
      label: 'Previsto',
      value: previsto,
      percentual: 100,
      icon: DollarSign,
      color: 'gray',
      description: 'Orçamento total planejado',
    },
    {
      id: 'empenhado',
      label: 'Empenhado',
      value: empenhado,
      percentual: percentualEmpenhado,
      icon: Clock,
      color: 'blue',
      description: 'Valores comprometidos',
    },
    {
      id: 'pago',
      label: 'Pago',
      value: pago,
      percentual: percentualPago,
      icon: TrendingUp,
      color: 'indigo',
      description: 'Valores transferidos',
    },
    {
      id: 'liquidado',
      label: 'Liquidado',
      value: liquidado,
      percentual: percentualLiquidado,
      icon: CheckCircle,
      color: 'green',
      description: 'Processos finalizados',
    },
  ];
  
  // Filtrar alertas financeiros
  const alertasFinanceiros = alertas.filter(a => 
    a.tipo === 'orcamento' || a.tipo === 'documentacao'
  );
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <DollarSign className="h-6 w-6" />
            Acompanhamento de Orçamento
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {fase && `${fase}`}
            {cidade && ` • ${cidade}`}
          </p>
        </div>
        
        {/* Status Badge */}
        <div className={`px-4 py-2 rounded-lg bg-${alerta.color}-100 border-2 border-${alerta.color}-200 flex items-center gap-2`}>
          <AlertIcon className={`h-5 w-5 text-${alerta.color}-600`} />
          <div>
            <p className={`text-sm font-bold text-${alerta.color}-800`}>
              {formatPercentage(percentual_utilizado)} utilizado
            </p>
            <p className="text-xs text-gray-600">
              {alerta.nivel === 'critico' && 'Orçamento Crítico!'}
              {alerta.nivel === 'atencao' && 'Atenção necessária'}
              {alerta.nivel === 'normal' && 'Execução normal'}
              {alerta.nivel === 'ok' && 'Dentro do esperado'}
            </p>
          </div>
        </div>
      </div>
      
      {/* Barra de Progresso Principal */}
      <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
        <div className="mb-4 flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Execução Orçamentária</span>
          <span className="text-sm text-gray-500">
            {formatCurrency(gasto_real)} de {formatCurrency(previsto)}
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-8 relative overflow-hidden">
          {/* Barra de progresso */}
          <div
            className={`h-full transition-all duration-500 flex items-center justify-center text-white text-sm font-bold ${
              percentual_utilizado >= 90 ? 'bg-gradient-to-r from-red-500 to-red-600' :
              percentual_utilizado >= 75 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
              'bg-gradient-to-r from-blue-500 to-blue-600'
            }`}
            style={{ width: `${Math.min(percentual_utilizado, 100)}%` }}
          >
            {percentual_utilizado > 10 && formatPercentage(percentual_utilizado)}
          </div>
          
          {/* Marcadores de threshold */}
          <div className="absolute top-0 left-[50%] w-0.5 h-full bg-gray-400 opacity-50" />
          <div className="absolute top-0 left-[75%] w-0.5 h-full bg-yellow-500 opacity-70" />
          <div className="absolute top-0 left-[90%] w-0.5 h-full bg-red-500 opacity-70" />
        </div>
        
        {/* Labels dos thresholds */}
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>0%</span>
          <span className="text-gray-400">50%</span>
          <span className="text-yellow-600">75% ⚠️</span>
          <span className="text-red-600">90% 🚨</span>
          <span>100%</span>
        </div>
      </div>
      
      {/* Cards de Estágios */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stages.map((stage, index) => {
          const StageIcon = stage.icon;
          const isActive = stage.value > 0;
          
          return (
            <div
              key={stage.id}
              className={`relative p-5 rounded-lg border-2 transition-all ${
                isActive
                  ? `bg-${stage.color}-50 border-${stage.color}-200 shadow-md`
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              {/* Seta de conexão */}
              {index < stages.length - 1 && (
                <div className="hidden lg:block absolute -right-6 top-1/2 transform -translate-y-1/2 z-10">
                  <div className={`w-12 h-0.5 ${isActive ? `bg-${stage.color}-300` : 'bg-gray-300'}`}>
                    <div className="absolute right-0 top-1/2 transform -translate-y-1/2 rotate-45 w-2 h-2 border-r-2 border-t-2 border-current" />
                  </div>
                </div>
              )}
              
              {/* Ícone */}
              <div className={`mb-3 flex items-center justify-between`}>
                <StageIcon className={`h-8 w-8 ${isActive ? `text-${stage.color}-600` : 'text-gray-400'}`} />
                <span className={`text-2xl font-bold ${isActive ? `text-${stage.color}-700` : 'text-gray-400'}`}>
                  {formatPercentage(stage.percentual)}
                </span>
              </div>
              
              {/* Label */}
              <p className={`font-semibold mb-1 ${isActive ? `text-${stage.color}-900` : 'text-gray-600'}`}>
                {stage.label}
              </p>
              
              {/* Valor */}
              <p className={`text-xl font-bold mb-2 ${isActive ? `text-${stage.color}-700` : 'text-gray-500'}`}>
                {formatCurrency(stage.value)}
              </p>
              
              {/* Descrição */}
              {showDetails && (
                <p className="text-xs text-gray-600">
                  {stage.description}
                </p>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Resumo Financeiro */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Disponível */}
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-800">💰 Disponível</span>
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-green-700">{formatCurrency(saldo)}</p>
          <p className="text-xs text-gray-600 mt-1">
            {formatPercentage(previsto > 0 ? (saldo / previsto) * 100 : 0)} do orçamento
          </p>
        </div>
        
        {/* Em Execução */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-800">⚡ Em Execução</span>
            <Clock className="h-5 w-5 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-blue-700">
            {formatCurrency(empenhado - liquidado)}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            Empenhado mas não liquidado
          </p>
        </div>
        
        {/* Finalizado */}
        <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-purple-800">✅ Finalizado</span>
            <FileCheck className="h-5 w-5 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-purple-700">
            {formatCurrency(liquidado)}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            {formatPercentage(previsto > 0 ? (liquidado / previsto) * 100 : 0)} do orçamento
          </p>
        </div>
      </div>
      
      {/* Alertas Financeiros */}
      {alertasFinanceiros.length > 0 && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-5">
          <h4 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Alertas Financeiros ({alertasFinanceiros.length})
          </h4>
          
          <div className="space-y-2">
            {alertasFinanceiros.map((alerta, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${
                  alerta.nivel === 'danger' ? 'bg-red-50 border-red-300' :
                  alerta.nivel === 'warning' ? 'bg-yellow-50 border-yellow-300' :
                  'bg-blue-50 border-blue-300'
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{alerta.icone || '⚠️'}</span>
                  <div className="flex-1">
                    <p className={`font-medium ${
                      alerta.nivel === 'danger' ? 'text-red-800' :
                      alerta.nivel === 'warning' ? 'text-yellow-800' :
                      'text-blue-800'
                    }`}>
                      {alerta.mensagem}
                    </p>
                    
                    {alerta.dados && (
                      <div className="mt-2 text-xs text-gray-600 grid grid-cols-2 gap-2">
                        {alerta.dados.percentual !== undefined && (
                          <span>📊 {formatPercentage(alerta.dados.percentual)} utilizado</span>
                        )}
                        {alerta.dados.previsto !== undefined && (
                          <span>💼 Previsto: {formatCurrency(alerta.dados.previsto)}</span>
                        )}
                        {alerta.dados.gasto !== undefined && (
                          <span>💸 Gasto: {formatCurrency(alerta.dados.gasto)}</span>
                        )}
                        {alerta.dados.saldo !== undefined && (
                          <span>💰 Saldo: {formatCurrency(alerta.dados.saldo)}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Detalhes Expandidos */}
      {showDetails && (
        <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
          <h4 className="font-semibold text-gray-800 mb-4">📊 Detalhamento do Fluxo</h4>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center pb-2 border-b border-gray-300">
              <span className="text-sm text-gray-700 font-medium">Orçamento Previsto</span>
              <span className="text-sm font-bold text-gray-900">{formatCurrency(previsto)}</span>
            </div>
            
            <div className="flex justify-between items-center text-blue-700 pl-4">
              <span className="text-sm">↳ Empenhado (comprometido)</span>
              <span className="text-sm font-semibold">{formatCurrency(empenhado)}</span>
            </div>
            
            <div className="flex justify-between items-center text-indigo-700 pl-8">
              <span className="text-sm">↳ Pago (transferido)</span>
              <span className="text-sm font-semibold">{formatCurrency(pago)}</span>
            </div>
            
            <div className="flex justify-between items-center text-green-700 pl-12">
              <span className="text-sm">↳ Liquidado (finalizado)</span>
              <span className="text-sm font-semibold">{formatCurrency(liquidado)}</span>
            </div>
            
            <div className="flex justify-between items-center pt-2 border-t-2 border-gray-400 font-bold">
              <span className="text-sm text-gray-900">Saldo Disponível</span>
              <span className={`text-sm ${saldo < previsto * 0.1 ? 'text-red-600' : 'text-green-600'}`}>
                {formatCurrency(saldo)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BudgetTracker;
