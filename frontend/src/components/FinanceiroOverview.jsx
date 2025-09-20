import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { DollarSign, TrendingUp, TrendingDown, FileText, Building, Receipt, CreditCard, PieChart, Calendar, AlertTriangle, ExternalLink, Filter, Edit, Trash2, X, Save, Loader, CheckCircle, User, Phone, Mail, MapPin, Tag } from 'lucide-react'

// Configuração da API
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

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
        const response = await fetch(`${API_URL}/api/financeiro/gastos/${gastoId}`, {
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
      setSaving(true);
      setSuccessMessage('');
      
      // Preparar apenas os campos que serão atualizados
      const updateData = {
        descricao_item: updatedGasto.descricao_item,
        fornecedor: updatedGasto.fornecedor,
        valor_total: updatedGasto.valor_total, // Já é number
        data_despesa: updatedGasto.data_despesa,
        possui_nota_fiscal: updatedGasto.possui_nota_fiscal, // Já é boolean
        tipo_documento: updatedGasto.tipo_documento,
        natureza_do_gasto: updatedGasto.natureza_do_gasto,
      };

      const response = await fetch(`${API_URL}/api/financeiro/gastos/${updatedGasto.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        setSuccessMessage('Gasto atualizado com sucesso!');
        setTimeout(() => {
          setIsModalOpen(false);
          setEditingGasto(null);
          setSuccessMessage('');
          // Recarregar dados
          window.location.reload();
        }, 1500);
      } else {
        const errorData = await response.json();
        console.error('Erro na resposta:', errorData);
        alert(`Erro ao atualizar gasto: ${errorData.detail || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao atualizar gasto');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
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
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl backdrop-blur-lg">
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
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Período</label>
                  <Select
                    value={filters.periodo}
                    onChange={(value) => handleFilterChange('periodo', value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
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
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Categoria</label>
                  <Select
                    value={filters.categoria}
                    onChange={(value) => handleFilterChange('categoria', value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
                  >
                    {categoryOptions.map(option => (
                      <SelectOption key={option.value} value={option.value}>
                        {option.label}
                      </SelectOption>
                    ))}
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Fornecedor</label>
                  <Select
                    value={filters.fornecedor}
                    onChange={(value) => handleFilterChange('fornecedor', value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
                  >
                    {supplierOptions.map(option => (
                      <SelectOption key={option.value} value={option.value}>
                        {option.label}
                      </SelectOption>
                    ))}
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Documentação</label>
                  <Select
                    value={filters.documentacao}
                    onChange={(value) => handleFilterChange('documentacao', value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-lg shadow-sm hover:border-green-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 transition-all duration-200 p-2"
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
            <div key={i} className="animate-pulse bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
              <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-24 mb-4"></div>
              <div className="h-10 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-20 mb-3"></div>
              <div className="h-3 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg w-32"></div>
            </div>
          ))}
        </motion.div>
      ) : (
        <>
          {/* KPI Cards - Mobile Optimized */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8"
          >
            {/* Total de Gastos */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700 min-h-[120px] sm:min-h-[140px]">
              <div className="flex items-center justify-between h-full">
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">Total de Gastos</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-green-600 dark:text-green-400 mt-1 truncate">
                    {formatCurrency(financeiroData.total_gastos)}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1 sm:mt-2 truncate">{financeiroData.total_despesas} despesas</p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center ml-2 flex-shrink-0">
                  <DollarSign className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 dark:text-green-400" />
                </div>
              </div>
            </div>

            {/* Média por Dia */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700 min-h-[120px] sm:min-h-[140px]">
              <div className="flex items-center justify-between h-full">
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">Média por Dia</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1 truncate">
                    {formatCurrency(financeiroData.media_gastos_dia)}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1 sm:mt-2 truncate">Gasto médio diário</p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center ml-2 flex-shrink-0">
                  <Calendar className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
            </div>

            {/* Taxa de Documentação */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700 min-h-[120px] sm:min-h-[140px]">
              <div className="flex items-center justify-between h-full">
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">Taxa de Documentação</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-orange-600 dark:text-orange-400 mt-1 truncate">
                    {formatPercentage(financeiroData.taxa_documentacao)}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1 sm:mt-2 truncate">{financeiroData.resumo_kpis.gastos_com_nf} com NF</p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center ml-2 flex-shrink-0">
                  <FileText className="w-5 h-5 sm:w-6 sm:h-6 text-orange-600 dark:text-orange-400" />
                </div>
              </div>
            </div>

            {/* Variação do Período */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700 min-h-[120px] sm:min-h-[140px]">
              <div className="flex items-center justify-between h-full">
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">Variação</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-purple-600 dark:text-purple-400 mt-1 truncate">
                    {financeiroData.variacao_percentual > 0 ? '+' : ''}{formatPercentage(financeiroData.variacao_percentual)}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1 sm:mt-2 truncate">vs período anterior</p>
                </div>
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center ml-2 flex-shrink-0">
                  {financeiroData.variacao_percentual > 0 ? 
                    <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600 dark:text-purple-400" /> : 
                    <TrendingDown className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600 dark:text-purple-400" />
                  }
                </div>
              </div>
            </div>
          </motion.div>

          {/* Seção de análises detalhadas */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-8">
            {/* Top Gastos */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-4 sm:p-6 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-red-600 rounded-xl">
                  <Receipt className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <h3 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-200">
                  Maiores Gastos
                </h3>
              </div>
              <div className="space-y-3 sm:space-y-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-2 sm:p-4 max-h-80 sm:max-h-96 overflow-y-auto">
                {financeiroData.top_gastos?.length > 0 ? financeiroData.top_gastos.map((gasto, index) => (
                  <div key={index} className="p-3 sm:p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-md hover:shadow-lg transition-all duration-300">
                    {/* Mobile: Layout Stacked, Desktop: Layout Side by Side */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
                      <div className="flex items-start sm:items-center gap-3 sm:gap-4 flex-1 min-w-0">
                        <div className="relative flex-shrink-0">
                          <div className="w-8 h-8 sm:w-12 sm:h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center text-white text-sm sm:text-lg font-bold shadow-lg">
                            {index + 1}
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-bold text-gray-900 dark:text-white text-sm sm:text-base truncate">
                            {gasto.descricao_item || 'Despesa'}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                            {gasto.fornecedor || 'Não informado'} • {gasto.data_despesa}
                          </p>
                          {/* Mostrar natureza do gasto (categoria) */}
                          <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                            📂 {gasto.natureza_do_gasto || 'Não categorizado'}
                          </p>
                          {/* Mobile: Stack badges and buttons vertically */}
                          <div className="flex flex-wrap items-center gap-1 sm:gap-2 mt-1 sm:mt-2">
                            <span className={`text-xs px-2 py-1 rounded-full font-semibold whitespace-nowrap ${
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
                                    className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors duration-200 border border-blue-300 whitespace-nowrap"
                                    title={`Ver ${doc.tipo}`}
                                  >
                                    <ExternalLink className="h-3 w-3 flex-shrink-0" />
                                    <span className="hidden sm:inline">{doc.tipo === 'Nota Fiscal' ? 'NF' : doc.tipo === 'Comprovante de Pagamento' ? 'Comprovante' : doc.tipo}</span>
                                    <span className="sm:hidden">{doc.tipo === 'Nota Fiscal' ? 'NF' : 'Doc'}</span>
                                  </button>
                                )
                              ))
                            ) : (
                              // Fallback para estrutura antiga
                              gasto.documento_url && (
                                <button
                                  onClick={() => window.open(gasto.documento_url, '_blank')}
                                  className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors duration-200 border border-blue-300 whitespace-nowrap"
                                  title="Ver documento"
                                >
                                  <ExternalLink className="h-3 w-3 flex-shrink-0" />
                                  <span className="hidden sm:inline">Ver Documento</span>
                                  <span className="sm:hidden">Doc</span>
                                </button>
                              )
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {/* Mobile: Move to separate row, Desktop: Keep on right */}
                      <div className="flex items-center justify-between sm:flex-col sm:text-right sm:ml-4 sm:min-w-0">
                        <div>
                          <div className="text-lg sm:text-xl font-bold text-red-600 dark:text-red-400">
                            {formatCurrency(gasto.valor_total)}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-0 sm:mt-1">
                            {gasto.tipo_documento}
                          </div>
                        </div>
                        <div className="flex gap-1 sm:gap-2 sm:mt-2">
                          <button
                            onClick={() => handleEditGasto(gasto)}
                            className="p-2 text-blue-600 hover:text-blue-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors touch-manipulation"
                            title="Editar gasto"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteGasto(gasto.id)}
                            className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 dark:hover:bg-red-900 rounded transition-colors touch-manipulation"
                            title="Deletar gasto"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
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
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-indigo-600 rounded-xl">
                  <Building className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                  Top Fornecedores
                </h3>
              </div>
              <div className="space-y-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
                {Object.entries(financeiroData.gastos_por_fornecedor || {}).length > 0 ? 
                  Object.entries(financeiroData.gastos_por_fornecedor).slice(0, 5).map(([fornecedor, valor], index) => (
                    <div key={index} className="flex justify-between items-center p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-md">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full shadow-lg"></div>
                        <span className="font-semibold text-gray-700 dark:text-gray-300 text-sm">
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
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-4 bg-gradient-to-r from-slate-600 to-slate-700 rounded-xl shadow-lg">
                <PieChart className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                Resumo Financeiro Detalhado
              </h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-lg">
                <div className="text-3xl font-bold text-green-700 mb-2">
                  {formatCurrency(financeiroData.resumo_kpis.maior_gasto)}
                </div>
                <div className="text-sm font-semibold text-gray-600">
                  Maior Gasto
                </div>
              </div>
              
              <div className="text-center p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-lg">
                <div className="text-3xl font-bold text-blue-700 mb-2">
                  {formatCurrency(financeiroData.resumo_kpis.menor_gasto)}
                </div>
                <div className="text-sm font-semibold text-gray-600">
                  Menor Gasto
                </div>
              </div>
              
              <div className="text-center p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-lg">
                <div className="text-3xl font-bold text-yellow-700 mb-2">
                  {financeiroData.resumo_kpis.gastos_com_nf}
                </div>
                <div className="text-sm font-semibold text-gray-600">
                  Com Nota Fiscal
                </div>
              </div>
              
              <div className="text-center p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-lg">
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-in slide-in-from-bottom-4 duration-300">
            
            {/* Notificação de sucesso */}
            {successMessage && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-t-xl flex items-center animate-in slide-in-from-top-2 duration-300">
                <CheckCircle className="w-5 h-5 mr-2" />
                <span>{successMessage}</span>
              </div>
            )}
            
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <Receipt className="w-8 h-8 text-green-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Editar Gasto
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Edite os dados do gasto selecionado
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
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
                  natureza_do_gasto: formData.get('naturezaGasto'),
                };
                handleSaveEdit(updatedGasto);
              }}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* Descrição */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-blue-500" />
                      Descrição
                    </label>
                    <input
                      name="descricao"
                      defaultValue={editingGasto.descricao_item}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                      required
                    />
                  </div>

                  {/* Fornecedor */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                      <Building className="w-4 h-4 mr-2 text-purple-500" />
                      Fornecedor
                    </label>
                    <input
                      name="fornecedor"
                      defaultValue={editingGasto.fornecedor}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                      required
                    />
                  </div>

                  {/* Valor */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                      <DollarSign className="w-4 h-4 mr-2 text-green-500" />
                      Valor
                    </label>
                    <input
                      name="valor"
                      type="number"
                      step="0.01"
                      defaultValue={editingGasto.valor_total}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                      required
                    />
                  </div>

                  {/* Data */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                      <Calendar className="w-4 h-4 mr-2 text-orange-500" />
                      Data
                    </label>
                    <input
                      name="data"
                      type="date"
                      defaultValue={editingGasto.data_despesa}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                      required
                    />
                  </div>

                  {/* Nota Fiscal */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                      <Receipt className="w-4 h-4 mr-2 text-red-500" />
                      Possui Nota Fiscal
                    </label>
                    <select
                      name="notaFiscal"
                      defaultValue={editingGasto.possui_nota_fiscal ? 'true' : 'false'}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                    >
                      <option value="true">Sim</option>
                      <option value="false">Não</option>
                    </select>
                  </div>

                  {/* Tipo de Documento */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-indigo-500" />
                      Tipo de Documento
                    </label>
                    <input
                      name="tipoDocumento"
                      defaultValue={editingGasto.tipo_documento}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                    />
                  </div>

                  {/* Natureza do Gasto */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                      <Tag className="w-4 h-4 mr-2 text-yellow-500" />
                      Categoria
                    </label>
                    <select
                      name="naturezaGasto"
                      defaultValue={editingGasto.natureza_do_gasto || "Não categorizado"}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                    >
                      <option value="Não categorizado">Não categorizado</option>
                      <option value="Alimentação">Alimentação</option>
                      <option value="Transporte">Transporte</option>
                      <option value="Combustível">Combustível</option>
                      <option value="Manutenção">Manutenção</option>
                      <option value="Marketing">Marketing</option>
                      <option value="Tecnologia">Tecnologia</option>
                      <option value="Administrativo">Administrativo</option>
                      <option value="RH">Recursos Humanos</option>
                      <option value="Jurídico">Jurídico</option>
                      <option value="Contabilidade">Contabilidade</option>
                      <option value="Segurança">Segurança</option>
                      <option value="Limpeza">Limpeza</option>
                      <option value="Material de Escritório">Material de Escritório</option>
                      <option value="Outros">Outros</option>
                    </select>
                  </div>
                </div>

                {/* Footer com botões */}
                <div className="flex space-x-3 mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-6 py-3 border border-gray-300 text-gray-700 dark:text-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex-1 font-medium"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex items-center justify-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed transition-colors flex-1 font-medium"
                  >
                    {saving ? (
                      <Loader className="w-5 h-5 mr-2 animate-spin" />
                    ) : (
                      <Save className="w-5 h-5 mr-2" />
                    )}
                    {saving ? 'Salvando...' : 'Salvar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}
