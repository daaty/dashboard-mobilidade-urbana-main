import React from 'react'
import { Target, AlertTriangle } from 'lucide-react'
import { useMetasProgress } from './hooks'
import { ProgressIndicator } from './Documentation'

/**
 * Tabela de acompanhamento por cidade com dados REAIS de execução
 * Integrada com APIs via useMetasProgress hook
 * 
 * Props:
 * - fase: string - Nome da fase ('Fase 1', 'Fase 2', 'Fase 3')
 * - autoRefresh: boolean - Auto-refresh a cada 5 minutos (default: true)
 */
const TabelaExecucao = ({ fase = 'Fase 1', autoRefresh = true }) => {
  // Hook master que busca TODOS os dados reais das APIs
  const { data, loading, error, lastUpdate } = useMetasProgress(fase, autoRefresh)
  
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-12 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Carregando dados de execução...</p>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-4" />
        <p className="text-red-800 font-medium">Erro ao carregar dados</p>
        <p className="text-red-600 text-sm mt-2">{error.message}</p>
      </div>
    )
  }
  
  if (!data || !data.cidades || data.cidades.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
        <p className="text-yellow-800">Nenhum dado disponível para {fase}</p>
      </div>
    )
  }
  
  // Dados reais das APIs
  const dadosExecucao = data.cidades

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-blue-800 to-blue-900 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold flex items-center gap-2">
              <Target className="w-5 h-5" />
              {data.fase} - Execução Real-Time
            </h3>
            <p className="text-blue-200 text-sm mt-1">
              APIs integradas: Drivers + Rides + Campanhas + Financeiro
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-blue-200">Última atualização:</p>
            <p className="text-sm font-medium">{new Date(lastUpdate).toLocaleTimeString('pt-BR')}</p>
            {autoRefresh && (
              <p className="text-xs text-blue-300 mt-1">🔄 Auto-refresh ativo</p>
            )}
          </div>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Cidade</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Motoristas</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Corridas</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Orçamento</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Status</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Alertas</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {dadosExecucao.map((cidade, index) => {
              // Contar alertas dessa cidade
              const alertasCidade = data.alertas?.filter(a => a.cidade === cidade.nome) || []
              const temAlertaCritico = alertasCidade.some(a => a.nivel === 'danger')
              
              return (
                <tr key={index} className={`hover:bg-gray-50 transition-colors ${temAlertaCritico ? 'bg-red-50' : ''}`}>
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-semibold text-gray-900">{cidade.nome}</div>
                      {cidade.financeiro?.campanhas > 0 && (
                        <div className="text-xs text-blue-600 mt-1">
                          📊 {cidade.financeiro.campanhas} campanhas ativas
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <ProgressIndicator
                      meta={cidade.part1.meta}
                      realizado={cidade.part1.realizado}
                      status={cidade.part1.status}
                      mode="inline"
                      size="sm"
                      showPercentage={true}
                      showValues={true}
                      showStatus={false}
                    />
                    {cidade.part1.ativos !== undefined && (
                      <div className="text-xs text-gray-500 mt-1">
                        ✅ {cidade.part1.ativos} ativos • ⭐ {cidade.part1.rating_medio?.toFixed(1) || 'N/A'}
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4">
                    <ProgressIndicator
                      meta={cidade.part2.meta}
                      realizado={cidade.part2.realizado}
                      status={cidade.part2.status}
                      mode="inline"
                      size="sm"
                      showPercentage={true}
                      showValues={true}
                      showStatus={false}
                    />
                    {cidade.part2.canceladas !== undefined && (
                      <div className="text-xs text-gray-500 mt-1">
                        ❌ {cidade.part2.canceladas} canceladas • 💰 R$ {cidade.part2.receita?.toLocaleString() || 0}
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <div className="font-medium text-blue-600">
                        R$ {cidade.financeiro?.orcamento?.toLocaleString() || 0}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Gasto: R$ {cidade.financeiro?.gasto?.toLocaleString() || 0}
                      </div>
                      <div className="text-xs text-green-600">
                        Saldo: R$ {cidade.financeiro?.saldo?.toLocaleString() || 0}
                      </div>
                      {cidade.financeiro?.percentual !== undefined && (
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                          <div 
                            className={`h-1.5 rounded-full ${
                              cidade.financeiro.percentual >= 90 ? 'bg-red-500' :
                              cidade.financeiro.percentual >= 75 ? 'bg-yellow-500' :
                              'bg-green-500'
                            }`}
                            style={{ width: `${Math.min(cidade.financeiro.percentual, 100)}%` }}
                          ></div>
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        cidade.part1.status === 'concluido' ? 'bg-green-100 text-green-800' :
                        cidade.part1.status === 'no_prazo' ? 'bg-blue-100 text-blue-800' :
                        cidade.part1.status === 'atencao' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {cidade.part1.status === 'concluido' ? '✅ Motoristas OK' :
                         cidade.part1.status === 'no_prazo' ? '🔵 No Prazo' :
                         cidade.part1.status === 'atencao' ? '⚠️ Atenção' :
                         '🔴 Atrasado'}
                      </span>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        cidade.part2.status === 'concluido' ? 'bg-green-100 text-green-800' :
                        cidade.part2.status === 'no_prazo' ? 'bg-blue-100 text-blue-800' :
                        cidade.part2.status === 'atencao' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {cidade.part2.status === 'concluido' ? '✅ Corridas OK' :
                         cidade.part2.status === 'no_prazo' ? '🔵 No Prazo' :
                         cidade.part2.status === 'atencao' ? '⚠️ Atenção' :
                         '🔴 Atrasado'}
                      </span>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    {alertasCidade.length > 0 ? (
                      <div className="space-y-1">
                        {alertasCidade.slice(0, 2).map((alerta, idx) => (
                          <div 
                            key={idx}
                            className={`text-xs px-2 py-1 rounded ${
                              alerta.nivel === 'danger' ? 'bg-red-100 text-red-800' :
                              alerta.nivel === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {alerta.icone} {alerta.tipo}
                          </div>
                        ))}
                        {alertasCidade.length > 2 && (
                          <div className="text-xs text-gray-500">
                            +{alertasCidade.length - 2} mais
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-green-600">✓ Sem alertas</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      
      {/* Footer com estatísticas */}
      {data.estatisticas && (
        <div className="bg-gray-50 border-t border-gray-200 p-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">
                {data.estatisticas.total_motoristas_real}
              </p>
              <p className="text-xs text-gray-600">Motoristas Reais</p>
              <p className="text-xs text-gray-500">
                Meta: {data.estatisticas.total_motoristas_meta}
              </p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">
                {data.estatisticas.total_corridas_real}
              </p>
              <p className="text-xs text-gray-600">Corridas Reais</p>
              <p className="text-xs text-gray-500">
                Meta: {data.estatisticas.total_corridas_meta}
              </p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">
                {data.estatisticas.progresso_medio_motoristas?.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-600">Progresso Motoristas</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">
                {data.estatisticas.progresso_medio_corridas?.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-600">Progresso Corridas</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">
                {data.estatisticas.cidades_atrasadas || 0}
              </p>
              <p className="text-xs text-gray-600">Cidades Atrasadas</p>
              <p className="text-xs text-green-500">
                {data.estatisticas.cidades_concluidas || 0} concluídas
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TabelaExecucao
