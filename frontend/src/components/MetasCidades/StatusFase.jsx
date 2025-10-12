/**
 * 📊 STATUS FASE - Card de Status de Fase Estratégica
 * 
 * Componente visual para exibir informações de uma fase do planejamento.
 * Mostra status, período, cidades, progresso orçamentário e metas das parts.
 * INTEGRADO com APIs reais via useMetasProgress
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  Calendar,
  MapPin,
  Users,
  Activity,
  DollarSign,
  PlayCircle,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp
} from 'lucide-react';
import { STATUS_FASE_CORES, STATUS_FASE_LABELS } from '../../constants/cidadesConstants.js';
import { useMetasProgress } from './hooks';

/**
 * Card de status de fase COM DADOS REAIS
 * @param {Object} props
 * @param {string} props.fase - Nome da fase (ex: "Fase 1")
 * @param {Function} props.onVerDetalhes - Callback ao clicar em "Ver detalhes"
 */
const StatusFase = ({ fase, onVerDetalhes }) => {
  // Hook master que busca dados reais das APIs
  const { data: dadosFase, loading } = useMetasProgress(fase, true) // true = auto-refresh
  
  // 🔥 USANDO CONSTANTES IMPORTADAS
  const getStatusColor = (status) => STATUS_FASE_CORES[status]?.bg || 'bg-gray-400';
  
  const getStatusIcon = (status) => {
    switch(status) {
      case 'em_execucao': return <PlayCircle className="w-4 h-4" />
      case 'concluida': return <CheckCircle className="w-4 h-4" />
      case 'pausada': return <AlertCircle className="w-4 h-4" />
      case 'planejada': return <Clock className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  };

  const getStatusText = (status) => STATUS_FASE_LABELS[status] || 'Indefinido';

  // Loading state
  if (loading) {
    return (
      <motion.div 
        className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-gray-300"
      >
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </motion.div>
    )
  }
  
  if (!dadosFase) return null

  // Calcular progresso REAL baseado em dados das APIs
  const progressoMotoristas = Number(dadosFase.estatisticas?.progresso_medio_motoristas || 0)
  const progressoCorridas = Number(dadosFase.estatisticas?.progresso_medio_corridas || 0)
  const progressoOrcamento = Number(dadosFase.orcamento?.percentual_utilizado || 0)
  const progressoGeral = (progressoMotoristas + progressoCorridas) / 2

  const getProgressoColor = (valor) => {
    if (valor >= 75) return 'from-green-400 to-green-600';
    if (valor >= 50) return 'from-blue-400 to-blue-600';
    if (valor >= 25) return 'from-yellow-400 to-yellow-600';
    return 'from-red-400 to-red-600';
  };
  
  // Contar alertas críticos
  const alertasCriticos = dadosFase.alertas?.filter(a => a.nivel === 'danger').length || 0
  const cidadesNomes = dadosFase.cidades?.map(c => c.nome) || []

  return (
    <motion.div 
      whileHover={{ scale: 1.02, y: -4 }}
      className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500 hover:shadow-xl transition-all duration-300 relative"
    >
      {/* Badge de alertas críticos */}
      {alertasCriticos > 0 && (
        <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center animate-pulse">
          {alertasCriticos}
        </div>
      )}
      
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800">{fase}</h3>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-white text-sm ${getStatusColor(dadosFase.status)}`}>
          {getStatusIcon(dadosFase.status)}
          {getStatusText(dadosFase.status)}
        </div>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-gray-600">
          <Calendar className="w-4 h-4" />
          <span className="text-sm">{dadosFase.periodo}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-600">
          <MapPin className="w-4 h-4" />
          <span className="text-sm">
            {cidadesNomes.length > 3 
              ? `${cidadesNomes.slice(0, 3).join(", ")} e mais ${cidadesNomes.length - 3}...`
              : cidadesNomes.join(", ")
            }
          </span>
        </div>

        {/* Progresso REAL baseado em dados das APIs */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Progresso Geral
            </span>
            <span className="font-bold text-gray-800">{progressoGeral.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 bg-gradient-to-r ${getProgressoColor(progressoGeral)}`}
              style={{ width: `${Math.min(progressoGeral, 100)}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>Motoristas: {progressoMotoristas.toFixed(1)}%</span>
            <span>Corridas: {progressoCorridas.toFixed(1)}%</span>
          </div>
        </div>

        {/* Status das Parts com DADOS REAIS */}
        <div className="grid grid-cols-2 gap-3 mt-4">
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-medium text-blue-800">Motoristas</span>
            </div>
            <div className="text-lg font-bold text-blue-700">
              {dadosFase.estatisticas?.total_motoristas_real || 0}
            </div>
            <div className="text-xs text-gray-500">
              Meta: {dadosFase.estatisticas?.total_motoristas_meta || 0}
            </div>
            <div className={`text-xs font-medium mt-1 ${
              progressoMotoristas >= 70 ? 'text-green-600' :
              progressoMotoristas >= 40 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {progressoMotoristas >= 100 ? '✅ Meta atingida!' :
               progressoMotoristas >= 70 ? '🔵 No prazo' :
               progressoMotoristas >= 40 ? '⚠️ Atenção' :
               '🔴 Atrasado'}
            </div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-3 border border-green-200">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-green-600" />
              <span className="text-xs font-medium text-green-800">Corridas</span>
            </div>
            <div className="text-lg font-bold text-green-700">
              {dadosFase.estatisticas?.total_corridas_real || 0}
            </div>
            <div className="text-xs text-gray-500">
              Meta: {dadosFase.estatisticas?.total_corridas_meta || 0}
            </div>
            <div className={`text-xs font-medium mt-1 ${
              progressoCorridas >= 70 ? 'text-green-600' :
              progressoCorridas >= 40 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {progressoCorridas >= 100 ? '✅ Meta atingida!' :
               progressoCorridas >= 70 ? '🔵 No prazo' :
               progressoCorridas >= 40 ? '⚠️ Atenção' :
               '🔴 Atrasado'}
            </div>
          </div>
        </div>

        {/* Orçamento melhorado com DADOS REAIS */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
          <div className="flex items-center gap-2 mb-3">
            <DollarSign className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-medium text-purple-800">Controle Orçamentário</span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Previsto:</span>
                <span className="font-bold text-gray-700">R$ {dadosFase.orcamento?.previsto?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Empenhado:</span>
                <span className="font-bold text-purple-700">R$ {dadosFase.orcamento?.empenhado?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Pago:</span>
                <span className="font-bold text-green-700">R$ {dadosFase.orcamento?.pago?.toLocaleString() || '0'}</span>
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Liquidado:</span>
                <span className="font-bold text-blue-700">R$ {dadosFase.orcamento?.liquidado?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Saldo:</span>
                <span className="font-bold text-green-700">
                  R$ {dadosFase.orcamento?.saldo?.toLocaleString() || '0'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Utilizado:</span>
                <span className={`font-bold ${
                  progressoOrcamento >= 90 ? 'text-red-700' :
                  progressoOrcamento >= 75 ? 'text-yellow-700' : 'text-green-700'
                }`}>
                  {progressoOrcamento.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Ações rápidas com contador de alertas */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div className="flex items-center gap-2">
            <span className={`text-xs px-2 py-1 rounded-full ${
              dadosFase.status === 'em_execucao' ? 'bg-green-100 text-green-700' :
              dadosFase.status === 'concluida' ? 'bg-gray-100 text-gray-700' :
              'bg-blue-100 text-blue-700'
            }`}>
              {cidadesNomes.length} cidade{cidadesNomes.length !== 1 ? 's' : ''}
            </span>
            {alertasCriticos > 0 && (
              <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700 font-medium">
                🚨 {alertasCriticos} alerta{alertasCriticos !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          <button 
            onClick={() => onVerDetalhes && onVerDetalhes(fase, dadosFase)}
            className="text-blue-600 hover:text-blue-800 text-xs font-medium transition-colors"
          >
            Ver detalhes →
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default StatusFase;
