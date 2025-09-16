import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { DollarSign, TrendingUp, TrendingDown, FileText, Building, Receipt, CreditCard, PieChart, Calendar, AlertTriangle, ExternalLink, Filter, Edit, Trash2 } from 'lucide-react'

// Simulação dos componentes de UI, já que não temos acesso a eles.
const Card = ({ children, className }) => <div className={`border rounded-lg shadow-sm ${className}`}>{children}</div>;
const CardContent = ({ children, className }) => <div className={`p-6 ${className}`}>{children}</div>;
const CardHeader = ({ children, className }) => <div className={`p-6 ${className}`}>{children}</div>;
const CardTitle = ({ children, className }) => <h3 className={`font-semibold ${className}`}>{children}</h3>;

// Simulação de componentes Select (mesma implementação dos outros componentes)
const Select = ({ value, onChange, children, className }) => {
  return (
    <select 
      value={value} 
      onChange={(e) => onChange(e.target.value)}
      className={className}
    >
      {children}
    </select>
  );
};

const SelectOption = ({ value, children }) => {
  return <option value={value}>{children}</option>;
};

const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: '7 dias', value: '7d' },
  { label: '30 dias', value: '30d' },
  { label: '3 meses', value: '3m' },
  { label: '6 meses', value: '6m' },
  { label: '12 meses', value: '12m' }
];

const categoryOptions = [
  { label: 'Todas as categorias', value: '' },
  { label: 'Operacional', value: 'operacional' },
  { label: 'Administrativo', value: 'administrativo' },
  { label: 'Marketing', value: 'marketing' },
  { label: 'Tecnologia', value: 'tecnologia' },
  { label: 'RH', value: 'rh' }
];

const supplierOptions = [
  { label: 'Todos os fornecedores', value: '' },
  { label: 'Top 10', value: 'top10' },
  { label: 'Novos fornecedores', value: 'novos' },
  { label: 'Recorrentes', value: 'recorrentes' }
];

export function FinanceiroOverview({ data, loading = false, onPeriodChange }) {
  // Garante que data nunca será null/undefined
  const safeData = data || {};
  const [period, setPeriod] = useState('6m'); // Padronizado para 6 meses
  const [filters, setFilters] = useState({
    periodo: '6m',
    categoria: '',
    fornecedor: '',
    documentacao: ''
  });
  const [editingGasto, setEditingGasto] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Função para lidar com mudanças de filtro
  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({ ...prev, [filterType]: value }));
    if (filterType === 'periodo') {
      setPeriod(value);
      if (onPeriodChange) onPeriodChange(value);
    }
  };

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

  // Dispara callback para buscar dados ao trocar período (removida pois agora está em handleFilterChange)

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

  // Funções para editar e deletar gastos
  const handleEditGasto = (gasto) => {
    setEditingGasto(gasto);
    setIsModalOpen(true);
  };

  const handleDeleteGasto = async (gastoId) => {
    if (window.confirm('Tem certeza que deseja deletar este gasto?')) {
      try {
        // Chamar API de delete
        const response = await fetch(`/api/financeiro/gastos/${gastoId}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          // Recarregar dados ou atualizar estado
          alert('Gasto deletado com sucesso!');
          // Aqui você pode chamar uma função para recarregar os dados
        } else {
          alert('Erro ao deletar gasto');
        }
      } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao deletar gasto');
      }
    }
  };

  const handleSaveEdit = async (updatedGasto) => {
    try {
      // Preparar apenas os campos que serão atualizados
      const updateData = {
        descricao_item: updatedGasto.descricao_item,
        fornecedor: updatedGasto.fornecedor,
        valor_total: updatedGasto.valor_total, // Já é number
        data_despesa: updatedGasto.data_despesa,
        possui_nota_fiscal: updatedGasto.possui_nota_fiscal, // Já é boolean
        tipo_documento: updatedGasto.tipo_documento,
      };

      const response = await fetch(`/api/financeiro/gastos/${updatedGasto.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        setIsModalOpen(false);
        setEditingGasto(null);
        alert('Gasto atualizado com sucesso!');
        // Recarregar dados
      } else {
        const errorData = await response.json();
        console.error('Erro na resposta:', errorData);
        alert(`Erro ao atualizar gasto: ${errorData.detail || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao atualizar gasto');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header - Executive Style */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-2">
            DASHBOARD FINANCEIRO
          </h1>
          <p className="text-gray-600 text-lg">
            Controle de gastos e análise financeira empresarial. Monitore custos e otimize recursos.
          </p>
        </motion.div>

        {/* Filtros - Executive Style */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
              <div className="flex items-center gap-3 text-lg font-semibold">
                <div className="bg-green-500/20 p-2 rounded-lg">
                  <Filter className="w-5 h-5 text-green-400" />
                </div>
                Filtros de Análise Financeira
              </div>
            </div>
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Período</label>
                  <Select
                    value={filters.periodo}
                    onChange={(value) => handleFilterChange('periodo', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
                  >
                    <SelectOption value="">Selecione o período</SelectOption>
                    {periodOptions.map(option => (
                      <SelectOption key={option.value} value={option.value}>
                        {option.label}
                      </SelectOption>
                    ))}
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Categoria</label>
                  <Select
                    value={filters.categoria}
                    onChange={(value) => handleFilterChange('categoria', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
                  >
                    {categoryOptions.map(option => (
                      <SelectOption key={option.value} value={option.value}>
                        {option.label}
                      </SelectOption>
                    ))}
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Fornecedor</label>
                  <Select
                    value={filters.fornecedor}
                    onChange={(value) => handleFilterChange('fornecedor', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
                  >
                    {supplierOptions.map(option => (
                      <SelectOption key={option.value} value={option.value}>
                        {option.label}
                      </SelectOption>
                    ))}
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Documentação</label>
                  <Select
                    value={filters.documentacao}
                    onChange={(value) => handleFilterChange('documentacao', value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
                  >
                    <SelectOption value="">Todos</SelectOption>
                    <SelectOption value="com_nf">Com Nota Fiscal</SelectOption>
                    <SelectOption value="sem_nf">Sem Nota Fiscal</SelectOption>
                    <SelectOption value="pendente">Pendente</SelectOption>
                  </Select>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

      {loading ? (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
              <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-24 mb-4"></div>
              <div className="h-10 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-20 mb-3"></div>
              <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-32"></div>
            </div>
          ))}
        </motion.div>
      ) : (
        <>
          {/* KPI Cards - Executive Style */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            {/* Total de Gastos */}
            <div className="bg-gradient-to-br from-green-600 via-green-700 to-green-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-200 text-sm font-medium tracking-wide uppercase">Total de Gastos</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-green-300 to-emerald-300 bg-clip-text text-transparent mt-2">
                    {formatCurrency(financeiroData.total_gastos)}
                  </p>
                  <p className="text-green-300 text-sm mt-2">{financeiroData.total_despesas} despesas registradas</p>
                </div>
                <div className="bg-green-500/20 p-4 rounded-xl">
                  <DollarSign className="w-8 h-8 text-green-400" />
                </div>
              </div>
            </div>

            {/* Média por Dia */}
            <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-200 text-sm font-medium tracking-wide uppercase">Média por Dia</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-blue-300 to-cyan-300 bg-clip-text text-transparent mt-2">
                    {formatCurrency(financeiroData.media_gastos_dia)}
                  </p>
                  <p className="text-blue-300 text-sm mt-2">Gasto médio diário</p>
                </div>
                <div className="bg-blue-500/20 p-4 rounded-xl">
                  <Calendar className="w-8 h-8 text-blue-400" />
                </div>
              </div>
            </div>

            {/* Taxa de Documentação */}
            <div className="bg-gradient-to-br from-yellow-600 via-orange-700 to-orange-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-200 text-sm font-medium tracking-wide uppercase">Taxa de Documentação</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent mt-2">
                    {formatPercentage(financeiroData.taxa_documentacao)}
                  </p>
                  <p className="text-orange-300 text-sm mt-2">{financeiroData.resumo_kpis.gastos_com_nf} com nota fiscal</p>
                </div>
                <div className="bg-orange-500/20 p-4 rounded-xl">
                  <FileText className="w-8 h-8 text-orange-400" />
                </div>
              </div>
            </div>

            {/* Variação do Período */}
            <div className="bg-gradient-to-br from-purple-600 via-purple-700 to-purple-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-200 text-sm font-medium tracking-wide uppercase">Variação</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent mt-2">
                    {financeiroData.variacao_percentual > 0 ? '+' : ''}{formatPercentage(financeiroData.variacao_percentual)}
                  </p>
                  <p className="text-purple-300 text-sm mt-2">vs período anterior</p>
                </div>
                <div className="bg-purple-500/20 p-4 rounded-xl">
                  {financeiroData.variacao_percentual > 0 ? 
                    <TrendingUp className="w-8 h-8 text-purple-400" /> : 
                    <TrendingDown className="w-8 h-8 text-purple-400" />
                  }
                </div>
              </div>
            </div>
          </motion.div>

          {/* Seção de análises detalhadas */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Top Gastos */}
            <div className="bg-gradient-to-br from-red-50 to-pink-100 border border-red-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-red-600 rounded-xl">
                  <Receipt className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-red-800">
                  Maiores Gastos
                </h3>
              </div>
              <div className="space-y-4 bg-white/60 backdrop-blur-sm rounded-xl border border-red-200 p-4 max-h-96 overflow-y-auto">
                {financeiroData.top_gastos?.length > 0 ? financeiroData.top_gastos.map((gasto, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-white to-red-50 rounded-xl shadow-md border border-red-100 hover:shadow-lg transition-all duration-300">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="relative">
                        <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center text-white text-lg font-bold shadow-lg">
                          {index + 1}
                        </div>
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-gray-900 text-sm">
                          {gasto.descricao_item || 'Despesa'}
                        </p>
                        <p className="text-xs text-gray-600">
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
                      <div className="text-xl font-bold text-red-600">
                        {formatCurrency(gasto.valor_total)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {gasto.tipo_documento}
                      </div>
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => handleEditGasto(gasto)}
                          className="p-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                          title="Editar gasto"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteGasto(gasto.id)}
                          className="p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
                          title="Deletar gasto"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-12 text-gray-500">
                    <Receipt className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Nenhum gasto encontrado</p>
                    <p className="text-sm">Ajuste o período de análise para ver dados</p>
                  </div>
                )}
              </div>
            </div>

            {/* Top Fornecedores */}
            <div className="bg-gradient-to-br from-indigo-50 to-purple-100 border border-indigo-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-indigo-600 rounded-xl">
                  <Building className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-indigo-800">
                  Top Fornecedores
                </h3>
              </div>
              <div className="space-y-4 bg-white/60 backdrop-blur-sm rounded-xl border border-indigo-200 p-4">
                {Object.entries(financeiroData.gastos_por_fornecedor || {}).length > 0 ? 
                  Object.entries(financeiroData.gastos_por_fornecedor).slice(0, 5).map(([fornecedor, valor], index) => (
                    <div key={index} className="flex justify-between items-center p-4 bg-gradient-to-r from-white to-indigo-50 rounded-xl shadow-md border border-indigo-100">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full shadow-lg"></div>
                        <span className="font-semibold text-gray-700 text-sm">
                          {fornecedor}
                        </span>
                      </div>
                      <span className="text-lg font-bold text-indigo-600">
                        {formatCurrency(valor)}
                      </span>
                    </div>
                  )) : (
                    <div className="text-center py-8 text-gray-500">
                      <Building className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                      <p>Nenhum fornecedor encontrado</p>
                    </div>
                  )}
              </div>
            </div>
          </div>

          {/* Resumo de KPIs Financeiros */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-slate-50 to-gray-100 border border-slate-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-4 bg-gradient-to-r from-slate-600 to-slate-700 rounded-xl shadow-lg">
                <PieChart className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-slate-800">
                Resumo Financeiro Detalhado
              </h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-2xl shadow-lg border border-green-200">
                <div className="text-3xl font-bold text-green-700 mb-2">
                  {formatCurrency(financeiroData.resumo_kpis.maior_gasto)}
                </div>
                <div className="text-sm font-semibold text-gray-600">
                  Maior Gasto
                </div>
              </div>
              
              <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl shadow-lg border border-blue-200">
                <div className="text-3xl font-bold text-blue-700 mb-2">
                  {formatCurrency(financeiroData.resumo_kpis.menor_gasto)}
                </div>
                <div className="text-sm font-semibold text-gray-600">
                  Menor Gasto
                </div>
              </div>
              
              <div className="text-center p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl shadow-lg border border-yellow-200">
                <div className="text-3xl font-bold text-yellow-700 mb-2">
                  {financeiroData.resumo_kpis.gastos_com_nf}
                </div>
                <div className="text-sm font-semibold text-gray-600">
                  Com Nota Fiscal
                </div>
              </div>
              
              <div className="text-center p-6 bg-gradient-to-br from-red-50 to-red-100 rounded-2xl shadow-lg border border-red-200">
                <div className="text-3xl font-bold text-red-700 mb-2">
                  {financeiroData.resumo_kpis.gastos_sem_nf}
                </div>
                <div className="text-sm font-semibold text-gray-600">
                  Sem Nota Fiscal
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}

      {/* Modal de Edição */}
      {isModalOpen && editingGasto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-bold mb-4">Editar Gasto</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const updatedGasto = {
                id: editingGasto.id,
                descricao_item: formData.get('descricao'),
                fornecedor: formData.get('fornecedor'),
                valor_total: parseFloat(formData.get('valor')),
                data_despesa: formData.get('data'),
                possui_nota_fiscal: formData.get('notaFiscal') === 'true',
                tipo_documento: formData.get('tipoDocumento'),
              };
              handleSaveEdit(updatedGasto);
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Descrição</label>
                  <input
                    name="descricao"
                    defaultValue={editingGasto.descricao_item}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fornecedor</label>
                  <input
                    name="fornecedor"
                    defaultValue={editingGasto.fornecedor}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Valor</label>
                  <input
                    name="valor"
                    type="number"
                    step="0.01"
                    defaultValue={editingGasto.valor_total}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Data</label>
                  <input
                    name="data"
                    type="date"
                    defaultValue={editingGasto.data_despesa}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Possui Nota Fiscal</label>
                  <select
                    name="notaFiscal"
                    defaultValue={editingGasto.possui_nota_fiscal ? 'true' : 'false'}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                  >
                    <option value="true">Sim</option>
                    <option value="false">Não</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tipo de Documento</label>
                  <input
                    name="tipoDocumento"
                    defaultValue={editingGasto.tipo_documento}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                  />
                </div>
              </div>
              <div className="flex gap-4 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}
