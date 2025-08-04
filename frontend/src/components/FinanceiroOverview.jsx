import { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, TrendingDown, FileText, Building, Receipt, CreditCard, PieChart, Calendar, AlertTriangle, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: '7 dias', value: '7d' },
  { label: '30 dias', value: '30d' },
  { label: '90 dias', value: '90d' },
  { label: '365 dias', value: '365d' },
]

export function FinanceiroOverview({ data, loading = false, onPeriodChange }) {
  // Garante que data nunca será null/undefined
  const safeData = data || {};
  const [period, setPeriod] = useState('30d')

  // Dados padrão caso não venha da API
  const financeiroData = safeData || {
    total_gastos: 0.0,
    total_despesas: 0,
    media_gastos_dia: 0.0,
    taxa_documentacao: 0.0,
    variacao_percentual: 0.0,
    gastos_por_categoria: {},
    gastos_por_fornecedor: {},
    gastos_por_tipo_documento: {},
    resumo_mensal: {},
    top_gastos: [],
    periodo_dias: 30,
    resumo_kpis: {
      gastos_com_nf: 0,
      gastos_sem_nf: 0,
      maior_gasto: 0,
      menor_gasto: 0
    }
  }

  // Calcular KPIs avançados
  const kpis = {
    eficienciaGastos: financeiroData.taxa_documentacao || 0,
    crescimentoGastos: financeiroData.variacao_percentual || 0,
    ticketMedio: financeiroData.total_despesas > 0 ? financeiroData.total_gastos / financeiroData.total_despesas : 0,
    tendenciaGastos: financeiroData.variacao_percentual >= 5 ? 'alta' : 
                     financeiroData.variacao_percentual <= -5 ? 'baixa' : 'estavel'
  }

  // Dispara callback para buscar dados ao trocar período
  const handlePeriodChange = (e) => {
    const newPeriod = e.target.value
    setPeriod(newPeriod)
    if (onPeriodChange) onPeriodChange(newPeriod)
  }

  // Função para determinar cor baseada na tendência financeira
  const getFinancialColor = (value, type = 'gastos') => {
    if (type === 'documentacao') {
      if (value >= 90) return 'text-green-700 dark:text-green-400'
      if (value >= 70) return 'text-yellow-700 dark:text-yellow-400'
      return 'text-red-700 dark:text-red-400'
    }
    if (type === 'variacao') {
      if (value > 10) return 'text-red-700 dark:text-red-400'
      if (value > 0) return 'text-yellow-700 dark:text-yellow-400'
      return 'text-green-700 dark:text-green-400'
    }
    return 'text-blue-700 dark:text-blue-400'
  }

  // Função para formatar valores monetários
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0)
  }

  // Função para formatar porcentagem
  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(1)}%`
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-8 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
      {/* Header com filtro de período e resumo executivo */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-200 dark:border-gray-700">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-gradient-to-r from-green-500 to-green-600 rounded-xl">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              Dashboard Financeiro
            </h1>
          </div>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
            Controle de gastos e análise financeira empresarial
          </p>
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2 px-3 py-2 bg-green-50 dark:bg-green-900/30 rounded-lg">
              <Calendar className="h-4 w-4 text-green-600 dark:text-green-400" />
              <span className="font-medium text-green-700 dark:text-green-300">
                Período: {period === 'hoje' ? '24 horas' : 
                         period === '7d' ? '7 dias' : 
                         period === '30d' ? '30 dias' :
                         period === '90d' ? '90 dias' : '1 ano'}
              </span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="font-medium text-blue-700 dark:text-blue-300">
                Atualizado: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex gap-3 flex-wrap">
          {periodOptions.map(opt => (
            <button
              key={opt.value}
              type="button"
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg
                ${period === opt.value 
                  ? 'bg-gradient-to-r from-green-600 to-green-700 text-white border-2 border-green-500 shadow-green-200 dark:shadow-green-800' 
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                }`}
              onClick={() => handlePeriodChange({ target: { value: opt.value } })}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700">
              <CardContent className="p-8">
                <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg w-24 mb-4"></div>
                <div className="h-10 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg w-20 mb-3"></div>
                <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg w-32"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <>
          {/* KPIs principais financeiros */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Total de Gastos */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-green-50 dark:from-gray-800 dark:to-green-900/20 rounded-2xl shadow-xl border border-green-100 dark:border-green-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Total de Gastos</CardTitle>
                <div className="p-3 bg-gradient-to-r from-green-500 to-green-600 rounded-xl shadow-lg">
                  <DollarSign className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-700 dark:text-green-400 mb-2">
                  {formatCurrency(financeiroData.total_gastos)}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  {financeiroData.total_despesas} despesas registradas
                </p>
              </CardContent>
            </Card>

            {/* Média por Dia */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-2xl shadow-xl border border-blue-100 dark:border-blue-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Média por Dia</CardTitle>
                <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg">
                  <Calendar className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-700 dark:text-blue-400 mb-2">
                  {formatCurrency(financeiroData.media_gastos_dia)}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  Gasto médio diário
                </p>
              </CardContent>
            </Card>

            {/* Taxa de Documentação */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-yellow-50 dark:from-gray-800 dark:to-yellow-900/20 rounded-2xl shadow-xl border border-yellow-100 dark:border-yellow-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Taxa de Documentação</CardTitle>
                <div className="flex items-center gap-1">
                  <div className="p-3 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-xl shadow-lg">
                    <FileText className="h-5 w-5 text-white" />
                  </div>
                  {financeiroData.taxa_documentacao >= 90 && <TrendingUp className="h-4 w-4 text-green-500" />}
                  {financeiroData.taxa_documentacao < 70 && <AlertTriangle className="h-4 w-4 text-red-500" />}
                </div>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold mb-2 ${getFinancialColor(financeiroData.taxa_documentacao, 'documentacao')}`}>
                  {formatPercentage(financeiroData.taxa_documentacao)}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  {financeiroData.resumo_kpis.gastos_com_nf} com nota fiscal
                </p>
              </CardContent>
            </Card>

            {/* Variação do Período */}
            <Card className="group hover:shadow-2xl transition-all duration-300 transform hover:scale-105 bg-gradient-to-br from-white to-purple-50 dark:from-gray-800 dark:to-purple-900/20 rounded-2xl shadow-xl border border-purple-100 dark:border-purple-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Variação</CardTitle>
                <div className="flex items-center gap-1">
                  <div className="p-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl shadow-lg">
                    <TrendingUp className="h-5 w-5 text-white" />
                  </div>
                  {financeiroData.variacao_percentual > 0 ? 
                    <TrendingUp className="h-4 w-4 text-red-500" /> : 
                    <TrendingDown className="h-4 w-4 text-green-500" />
                  }
                </div>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold mb-2 ${getFinancialColor(financeiroData.variacao_percentual, 'variacao')}`}>
                  {financeiroData.variacao_percentual > 0 ? '+' : ''}{formatPercentage(financeiroData.variacao_percentual)}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  vs período anterior
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Seção de análises detalhadas */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Top Gastos */}
            <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-red-50 dark:from-gray-800 dark:to-red-900/20 rounded-2xl shadow-xl border border-red-100 dark:border-red-800">
              <CardHeader className="border-b border-red-100 dark:border-red-800 pb-4">
                <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                  <div className="p-3 bg-gradient-to-r from-red-500 to-red-600 rounded-xl shadow-lg">
                    <Receipt className="h-6 w-6 text-white" />
                  </div>
                  Maiores Gastos
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {financeiroData.top_gastos?.length > 0 ? financeiroData.top_gastos.slice(0, 5).map((gasto, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-white to-red-50 dark:from-gray-700 dark:to-red-900/20 rounded-xl shadow-md border border-red-100 dark:border-red-800 hover:shadow-lg transition-all duration-300">
                      <div className="flex items-center gap-4 flex-1">
                        <div className="relative">
                          <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center text-white text-lg font-bold shadow-lg">
                            {index + 1}
                          </div>
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-gray-900 dark:text-white text-sm">
                            {gasto.descricao_item || 'Despesa'}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {gasto.fornecedor || 'Não informado'} • {gasto.data_despesa}
                          </p>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                              gasto.possui_nota_fiscal 
                                ? 'bg-green-100 text-green-800 border border-green-300' 
                                : 'bg-yellow-100 text-yellow-800 border border-yellow-300'
                            }`}>
                              {gasto.possui_nota_fiscal ? '✓ Com NF' : '⚠ Sem NF'}
                            </span>
                            {/* Mostrar múltiplos documentos */}
                            {gasto.documentos && gasto.documentos.length > 0 ? (
                              gasto.documentos.map((doc, docIndex) => (
                                doc.url && (
                                  <button
                                    key={docIndex}
                                    onClick={() => window.open(doc.url, '_blank')}
                                    className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors duration-200 border border-blue-300"
                                    title={`Ver ${doc.tipo}`}
                                  >
                                    <ExternalLink className="h-3 w-3" />
                                    <span>{doc.tipo === 'Nota Fiscal' ? 'NF' : doc.tipo === 'Comprovante de Pagamento' ? 'Comprovante' : doc.tipo}</span>
                                  </button>
                                )
                              ))
                            ) : (
                              // Fallback para estrutura antiga
                              gasto.documento_url && (
                                <button
                                  onClick={() => window.open(gasto.documento_url, '_blank')}
                                  className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors duration-200 border border-blue-300"
                                  title="Ver documento"
                                >
                                  <ExternalLink className="h-3 w-3" />
                                  <span>Ver Documento</span>
                                </button>
                              )
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <div className="text-xl font-bold text-red-600 dark:text-red-400">
                          {formatCurrency(gasto.valor_total)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {gasto.documentos && gasto.documentos.length > 1 
                            ? `${gasto.documentos.length} documentos`
                            : gasto.tipo_documento
                          }
                        </div>
                      </div>
                    </div>
                  )) : (
                    <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                      <Receipt className="h-12 w-12 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                      <p className="text-lg font-medium">Nenhum gasto encontrado</p>
                      <p className="text-sm">Ajuste o período de análise para ver dados</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Gastos por Fornecedor */}
            <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-indigo-50 dark:from-gray-800 dark:to-indigo-900/20 rounded-2xl shadow-xl border border-indigo-100 dark:border-indigo-800">
              <CardHeader className="border-b border-indigo-100 dark:border-indigo-800 pb-4">
                <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                  <div className="p-3 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-xl shadow-lg">
                    <Building className="h-6 w-6 text-white" />
                  </div>
                  Top Fornecedores
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {Object.entries(financeiroData.gastos_por_fornecedor || {}).length > 0 ? 
                    Object.entries(financeiroData.gastos_por_fornecedor).slice(0, 5).map(([fornecedor, valor], index) => (
                      <div key={index} className="flex justify-between items-center p-4 bg-gradient-to-r from-white to-indigo-50 dark:from-gray-700 dark:to-indigo-900/20 rounded-xl shadow-md border border-indigo-100 dark:border-indigo-800">
                        <div className="flex items-center gap-3">
                          <div className="w-3 h-3 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full shadow-lg"></div>
                          <span className="font-semibold text-gray-700 dark:text-gray-300 text-sm">
                            {fornecedor}
                          </span>
                        </div>
                        <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                          {formatCurrency(valor)}
                        </span>
                      </div>
                    )) : (
                      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                        <Building className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                        <p>Nenhum fornecedor encontrado</p>
                      </div>
                    )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Resumo de KPIs Financeiros */}
          <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700">
            <CardHeader className="border-b border-gray-200 dark:border-gray-700 pb-6">
              <CardTitle className="text-2xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                <div className="p-4 bg-gradient-to-r from-gray-600 to-gray-700 rounded-xl shadow-lg">
                  <PieChart className="h-7 w-7 text-white" />
                </div>
                Resumo Financeiro Detalhado
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-2xl shadow-lg border border-green-200 dark:border-green-700">
                  <div className="text-3xl font-bold text-green-700 dark:text-green-400 mb-2">
                    {formatCurrency(financeiroData.resumo_kpis.maior_gasto)}
                  </div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                    Maior Gasto
                  </div>
                </div>
                
                <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-2xl shadow-lg border border-blue-200 dark:border-blue-700">
                  <div className="text-3xl font-bold text-blue-700 dark:text-blue-400 mb-2">
                    {formatCurrency(financeiroData.resumo_kpis.menor_gasto)}
                  </div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                    Menor Gasto
                  </div>
                </div>
                
                <div className="text-center p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 rounded-2xl shadow-lg border border-yellow-200 dark:border-yellow-700">
                  <div className="text-3xl font-bold text-yellow-700 dark:text-yellow-400 mb-2">
                    {financeiroData.resumo_kpis.gastos_com_nf}
                  </div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                    Com Nota Fiscal
                  </div>
                </div>
                
                <div className="text-center p-6 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-2xl shadow-lg border border-red-200 dark:border-red-700">
                  <div className="text-3xl font-bold text-red-700 dark:text-red-400 mb-2">
                    {financeiroData.resumo_kpis.gastos_sem_nf}
                  </div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                    Sem Nota Fiscal
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
