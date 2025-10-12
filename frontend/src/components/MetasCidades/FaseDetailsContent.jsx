import React, { useState } from 'react'
import {
  Calendar,
  DollarSign,
  MapPin,
  Users,
  Activity,
  BarChart3,
  Download,
  Edit,
  FileText,
  AlertTriangle
} from 'lucide-react'
import { useMetasProgress } from './hooks'
import { BudgetTracker, AlertsPanel, ExpenseDocumentation, ProgressIndicator } from './Documentation'

/**
 * Componente de conteúdo detalhado de uma fase
 * Exibe informações completas: status, período, orçamento, cidades, parts
 * INTEGRADO com APIs reais via useMetasProgress
 * 
 * Props:
 * - faseNome: string - Nome da fase ('Fase 1', 'Fase 2', 'Fase 3')
 * - onEditFase: function - Callback para editar a fase
 */
const FaseDetailsContent = ({ faseNome, onEditFase }) => {
  const [activeTab, setActiveTab] = useState('visao-geral')
  
  // Hook master que busca todos os dados reais
  const { data: fase, loading, error } = useMetasProgress(faseNome, true) // true = auto-refresh
  
  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Carregando detalhes da fase...</p>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-4" />
        <p className="text-red-800 text-center">Erro ao carregar dados da fase</p>
        <p className="text-red-600 text-sm text-center mt-2">{error.message}</p>
      </div>
    )
  }
  
  if (!fase) {
    return (
      <div className="p-6 text-center text-gray-500">
        Nenhum dado disponível para {faseNome}
      </div>
    )
  }
  const getStatusColor = (status) => {
    switch(status) {
      case 'em_execucao': return 'bg-green-500'
      case 'concluida': return 'bg-gray-500'
      case 'pausada': return 'bg-yellow-500'
      case 'planejada': return 'bg-blue-500'
      default: return 'bg-gray-400'
    }
  }

  const progressoOrcamento = fase.orcamento?.empenhado > 0 
    ? (fase.orcamento.pago / fase.orcamento.empenhado) * 100 
    : 0
  
  // Tabs disponíveis
  const tabs = [
    { id: 'visao-geral', label: 'Visão Geral', icon: BarChart3 },
    { id: 'detalhes', label: 'Detalhes & Alertas', icon: AlertTriangle },
    { id: 'documentos', label: 'Documentos', icon: FileText },
    { id: 'financeiro', label: 'Orçamento', icon: DollarSign },
  ]

  return (
    <div className="space-y-6">
      {/* Tabs Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>
      
      {/* Tab Content */}
      {activeTab === 'visao-geral' && (
        <div className="space-y-6">
          {/* Status e Período */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-50 rounded-xl p-4">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Informações Gerais
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`px-2 py-1 rounded-full text-white text-xs ${getStatusColor(fase.status)}`}>
                    {fase.status === 'em_execucao' ? 'Em Execução' :
                     fase.status === 'concluida' ? 'Concluída' :
                     fase.status === 'pausada' ? 'Pausada' : 'Planejada'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Período:</span>
                  <span className="font-medium">{fase.periodo}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Cidades Envolvidas:</span>
                  <span className="font-medium">{fase.cidades?.length || 0}</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                Resumo Financeiro
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Previsto:</span>
                  <span className="font-medium text-gray-600">R$ {fase.orcamento?.previsto?.toLocaleString() || '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Empenhado:</span>
                  <span className="font-medium text-blue-600">R$ {fase.orcamento?.empenhado?.toLocaleString() || '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Pago:</span>
                  <span className="font-medium text-green-600">R$ {fase.orcamento?.pago?.toLocaleString() || '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Execução:</span>
                  <span className="font-bold text-purple-600">{progressoOrcamento.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Progresso por Cidade */}
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              Progresso por Cidade ({fase.cidades?.length || 0})
            </h4>
            {fase.cidades && fase.cidades.length > 0 ? (
              <div className="space-y-4">
                {fase.cidades.map((cidade, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
                    <h5 className="font-medium text-gray-800 mb-3">{cidade.nome}</h5>
                    
                    <div className="space-y-3">
                      {/* Motoristas */}
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-600">Motoristas</span>
                          <span className="text-xs text-gray-500">
                            {cidade.part1.realizado} de {cidade.part1.meta}
                          </span>
                        </div>
                        <ProgressIndicator
                          meta={cidade.part1.meta}
                          realizado={cidade.part1.realizado}
                          status={cidade.part1.status}
                          mode="bar"
                          size="sm"
                          showPercentage={true}
                          showValues={false}
                          showStatus={true}
                        />
                      </div>
                      
                      {/* Corridas */}
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-600">Corridas</span>
                          <span className="text-xs text-gray-500">
                            {cidade.part2.realizado} de {cidade.part2.meta}
                          </span>
                        </div>
                        <ProgressIndicator
                          meta={cidade.part2.meta}
                          realizado={cidade.part2.realizado}
                          status={cidade.part2.status}
                          mode="bar"
                          size="sm"
                          showPercentage={true}
                          showValues={false}
                          showStatus={true}
                        />
                      </div>
                      
                      {/* Orçamento */}
                      {cidade.financeiro && (
                        <div className="pt-2 border-t border-gray-100">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-500">Orçamento:</span>
                            <span className="font-medium text-blue-600">
                              R$ {cidade.financeiro.orcamento?.toLocaleString() || 0}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-500">Gasto:</span>
                            <span className="font-medium text-red-600">
                              R$ {cidade.financeiro.gasto?.toLocaleString() || 0}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-500">Saldo:</span>
                            <span className="font-medium text-green-600">
                              R$ {cidade.financeiro.saldo?.toLocaleString() || 0}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">Nenhuma cidade definida para esta fase</p>
            )}
          </div>
        </div>
      )}
      
      {activeTab === 'detalhes' && (
        <div className="space-y-6">{/* Detalhes das Parts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Part 1 - Motoristas */}
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
              <h4 className="font-semibold text-blue-800 mb-4 flex items-center gap-2">
                <Users className="w-4 h-4" />
                Part 1 - Motoristas
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-blue-600">Período:</span>
                  <span className="font-medium text-blue-800">{fase.periodo || 'A definir'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-600">Meta Total:</span>
                  <span className="font-medium text-blue-800">{fase.estatisticas?.total_motoristas_meta || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-600">Realizado:</span>
                  <span className="font-bold text-green-700">{fase.estatisticas?.total_motoristas_real || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-600">Progresso:</span>
                  <span className="font-bold text-purple-700">{fase.estatisticas?.progresso_medio_motoristas?.toFixed(1) || 0}%</span>
                </div>
              </div>
            </div>

            {/* Part 2 - Corridas */}
            <div className="bg-green-50 rounded-xl p-4 border border-green-200">
              <h4 className="font-semibold text-green-800 mb-4 flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Part 2 - Corridas
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-green-600">Período:</span>
                  <span className="font-medium text-green-800">{fase.periodo || 'A definir'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-600">Meta Total:</span>
                  <span className="font-medium text-green-800">{fase.estatisticas?.total_corridas_meta || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-600">Realizado:</span>
                  <span className="font-bold text-green-700">{fase.estatisticas?.total_corridas_real || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-600">Progresso:</span>
                  <span className="font-bold text-purple-700">{fase.estatisticas?.progresso_medio_corridas?.toFixed(1) || 0}%</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Alertas */}
          <AlertsPanel
            alertas={fase.alertas || []}
            dismissible={true}
            showFilters={true}
            size="md"
          />
        </div>
      )}
      
      {activeTab === 'documentos' && (
        <ExpenseDocumentation
          fase={faseNome}
          onDocumentAdded={(docs) => console.log('Documentos adicionados:', docs)}
        />
      )}
      
      {activeTab === 'financeiro' && (
        <BudgetTracker
          orcamento={fase.orcamento}
          alertas={fase.alertas?.filter(a => a.tipo === 'orcamento' || a.tipo === 'documentacao') || []}
          fase={faseNome}
          showDetails={true}
        />
      )}

      {/* Ações */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button 
          onClick={() => console.log('Exportar relatório da fase:', faseNome)}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
        >
          <Download className="w-4 h-4" />
          Exportar Relatório
        </button>
        <button 
          onClick={() => onEditFase && onEditFase(fase)}
          className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors flex items-center justify-center gap-2"
        >
          <Edit className="w-4 h-4" />
          Editar Fase
        </button>
      </div>
    </div>
  )
}

export default FaseDetailsContent
