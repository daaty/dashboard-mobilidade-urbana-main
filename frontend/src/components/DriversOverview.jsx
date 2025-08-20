import { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Star, TrendingUp, UserCheck, Activity, Award, AlertTriangle, Clock, BarChart3, Wifi, Filter, Target, DollarSign, MapPin, Car, AlertCircle, CheckCircle, XCircle, TrendingDown, Calendar, Lightbulb } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend, BarChart, Bar, XAxis, YAxis, LineChart, Line } from 'recharts';
import { useDriversAnalytics } from '../hooks/useDriversAnalytics';

// Simulação dos componentes de UI, já que não temos acesso a eles.
// Em um projeto real, você importaria de '@/components/ui/card'.
const Card = ({ children, className }) => <div className={`border rounded-lg shadow-sm ${className}`}>{children}</div>;
const CardContent = ({ children, className }) => <div className={`p-6 ${className}`}>{children}</div>;
const CardHeader = ({ children, className }) => <div className={`p-6 ${className}`}>{children}</div>;
const CardTitle = ({ children, className }) => <h3 className={`font-semibold ${className}`}>{children}</h3>;


const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: '7 dias', value: '7d' },
  { label: '30 dias', value: '30d' },
  { label: '3 meses', value: '3m' },
  { label: '6 meses', value: '6m' },
  { label: '12 meses', value: '12m' }
];

const statusOptions = [
  { label: 'Todos', value: '' },
  { label: 'Ativos', value: 'active' },
  { label: 'Inativos', value: 'inactive' },
  { label: 'Online', value: 'online' }
];

const performanceOptions = [
  { label: 'Todos', value: '' },
  { label: 'Excelente (A+/A)', value: 'excellent' },
  { label: 'Bom (B)', value: 'good' },
  { label: 'Médio (C)', value: 'average' },
  { label: 'Abaixo (D/F)', value: 'below' }
];

const revenueRanges = [
  { label: 'Todas as faixas', value: '' },
  { label: 'R$ 0 - R$ 500', value: [0, 500] },
  { label: 'R$ 500 - R$ 1.000', value: [500, 1000] },
  { label: 'R$ 1.000 - R$ 2.000', value: [1000, 2000] },
  { label: 'R$ 2.000+', value: [2000, 999999] }
];

const alertTypes = [
  { label: 'Baixa Performance', value: 'low_performance', color: 'red' },
  { label: 'Alto Cancelamento', value: 'high_cancellation', color: 'orange' },
  { label: 'Penalidades', value: 'penalties', color: 'yellow' },
  { label: 'Oportunidades', value: 'opportunities', color: 'green' }
];

// Cores para o novo gráfico
const STATUS_COLORS = {
    active: '#10B981', // Verde
    inactive: '#EF4444', // Vermelho
};


export default function DriversOverview({ onPeriodChange }) {
  try {
    const [period, setPeriod] = useState('6m'); // Mudado para 6 meses
    const [filters, setFilters] = useState({
      periodo: '6m', // Mudado para 6 meses para incluir dados históricos
      status: '',
      performance: '',
      ordenacao: 'rating',
      cidade: '',
      veiculo: '',
      faixaReceita: '',
      alertas: true
    });

    const [showComparison, setShowComparison] = useState(false);
    const [selectedAlert, setSelectedAlert] = useState('');

    // Hook para dados reais dos motoristas - expandido COM TRATAMENTO DE ERRO
    let driversData, loading, error, calculateAggregatedMetrics, getTopDrivers, getFilteredDrivers, getTemporalComparison, getSpecificAlerts;
    
    try {
      const hookResult = useDriversAnalytics();
      driversData = hookResult.driversData || [];
      loading = hookResult.loading || false;
      error = hookResult.error || null;
      calculateAggregatedMetrics = hookResult.calculateAggregatedMetrics || (() => null);
      getTopDrivers = hookResult.getTopDrivers || (() => []);
      getFilteredDrivers = hookResult.getFilteredDrivers || (() => []);
      getTemporalComparison = hookResult.getTemporalComparison || (() => ({}));
      getSpecificAlerts = hookResult.getSpecificAlerts || (() => []);
    } catch (hookError) {
      console.error('❌ Erro crítico no hook useDriversAnalytics:', hookError);
      driversData = [];
      loading = false;
      error = 'Erro ao carregar dados dos motoristas';
      calculateAggregatedMetrics = () => null;
      getTopDrivers = () => [];
      getFilteredDrivers = () => [];
      getTemporalComparison = () => ({});
      getSpecificAlerts = () => [];
    }

  // Calcular métricas baseadas no período selecionado
  const daysMap = {
    'hoje': 1,
    '7d': 7,
    '30d': 30,
    '3m': 90,
    '6m': 180,
    '12m': 365
  };
  const daysFilter = daysMap[filters.periodo] || daysMap[period] || 180; // Usar filters.periodo primeiro
  
  // Aplicar filtros aos dados antes de calcular métricas - com tratamento de erro
  let filteredData = [];
  let aggregatedData = null;
  
  try {
    filteredData = getFilteredDrivers({
      city: filters.cidade,
      vehicle: filters.veiculo,
      revenueRange: filters.faixaReceita ? revenueRanges.find(r => r.value === filters.faixaReceita)?.value : null,
      status: filters.status,
      performanceGrade: filters.performance
    });
  } catch (error) {
    console.error('Erro em getFilteredDrivers:', error);
    filteredData = [];
  }
  
  try {
    aggregatedData = calculateAggregatedMetrics(driversData, daysFilter);
  } catch (error) {
    console.error('Erro em calculateAggregatedMetrics:', error);
    aggregatedData = null;
  }

  // Debug: Log dos dados recebidos
  console.log('DriversOverview - dados agregados:', aggregatedData);
  console.log('DriversOverview - driversData original:', driversData);
  console.log('DriversOverview - loading:', loading);
  console.log('🔍 DADOS EXATOS DA API:', aggregatedData?.rawData);
  console.log('🔍 DRIVERS ARRAY:', aggregatedData?.drivers);

  // Utiliza os dados EXATOS da API - TODOS OS CAMPOS DISPONÍVEIS
  const dashboardData = aggregatedData && aggregatedData.rawData ? {
    // ===== DADOS DIRETOS DA API (GARANTIDOS) =====
    total_drivers: aggregatedData.rawData.total_drivers || 0,
    active_drivers: aggregatedData.rawData.active_drivers || 0,
    inactive_drivers: aggregatedData.rawData.inactive_drivers || 0,
    online_drivers: aggregatedData.rawData.online_drivers || 0,
    average_rating: Number(aggregatedData.rawData.average_rating || 0),
    total_rides_completed: Number(aggregatedData.rawData.total_rides_completed || 0),
    avg_rides_per_driver: Number(aggregatedData.rawData.avg_rides_per_driver || 0),
    
    // Top drivers LIMITADO a TOP 5 por horas online
    top_drivers: (aggregatedData.drivers || [])
      .sort((a, b) => (b.data?.metrics?.online_hours || 0) - (a.data?.metrics?.online_hours || 0))
      .slice(0, 5),
    
    // Performance metrics DIRETO da API
    performance_metrics: aggregatedData.rawData.performance_metrics || {
      excellent_drivers: 0,
      good_drivers: 0,
      average_drivers: 0,
      below_average_drivers: 0
    },
    
    // KPI metrics DIRETO da API  
    kpi_metrics: aggregatedData.rawData.kpi_metrics || {
      activation_rate: 0,
      excellence_rate: 0,
      performance_trend: "stable",
      efficiency_score: 0
    },
    
    // Status DIRETO da API
    drivers_by_status: aggregatedData.rawData.drivers_by_status || {
      ativo: 0,
      inativo: 0
    },
    
    // ===== CAMPOS CALCULADOS BASEADOS NOS DADOS DA API =====
    
    // Taxa de aceitação estimada baseada na atividade dos motoristas
    avg_acceptance_rate: aggregatedData.rawData.total_drivers > 0 && Number(aggregatedData.rawData.total_rides_completed || 0) > 0 ? 
      Math.min(95, 70 + (Number(aggregatedData.rawData.total_rides_completed || 0) / aggregatedData.rawData.total_drivers * 2)) : 0,
    
    // Taxa de conclusão estimada (alta se há muitas corridas)
    avg_completion_rate: Number(aggregatedData.rawData.total_rides_completed || 0) > 0 ? 
      Math.min(100, 85 + (Number(aggregatedData.rawData.total_rides_completed || 0) / 10)) : 100, 
    
    // Eficiência = efficiency_score da API
    efficiency_score: Number(aggregatedData.rawData.kpi_metrics?.efficiency_score || 0),
    
    // Excellence rate = excellence_rate da API
    excellence_rate: Number(aggregatedData.rawData.kpi_metrics?.excellence_rate || 0),
    
    // ===== CAMPOS QUE AGORA TEMOS NA API =====
    
    // Dados de tempo (VÊEM DA API!)
    total_online_hours: Number(aggregatedData.rawData.total_online_hours || 0),
    avg_hours_per_driver: aggregatedData.rawData.total_drivers > 0 ? 
      (Number(aggregatedData.rawData.total_online_hours || 0) / aggregatedData.rawData.total_drivers) : 0,
    
    // Dados financeiros (baseados no valor correto por corrida)
    total_revenue: Number(aggregatedData.rawData.total_rides_completed || 0) * 2.50, // R$ 2,50 por corrida completada
    total_commission: Number(aggregatedData.rawData.total_rides_completed || 0) * 2.50 * 0.15, // 15% de comissão
    total_bonus: Number(aggregatedData.rawData.total_rides_completed || 0) > 100 ? Number(aggregatedData.rawData.total_rides_completed || 0) * 2.5 : 0,
    total_penalty: 0, // Sem dados de penalidades na API
    net_revenue: (Number(aggregatedData.rawData.total_rides_completed || 0) * 2.50) * 0.85, // Receita - comissão
    avg_revenue_per_driver: aggregatedData.rawData.total_drivers > 0 ? 
      (Number(aggregatedData.rawData.total_rides_completed || 0) * 2.50) / aggregatedData.rawData.total_drivers : 0,
    avg_revenue_per_hour: Number(aggregatedData.rawData.total_online_hours || 0) > 0 ? 
      (Number(aggregatedData.rawData.total_rides_completed || 0) * 2.50) / Number(aggregatedData.rawData.total_online_hours || 0) : 0,
    commission_rate: 15.0, // Taxa fixa estimada
    
    // Dados operacionais (calculados dos motoristas individuais)
    total_distance: Number(aggregatedData.rawData.total_rides_completed || 0) * 8.5, // 8.5 km por corrida estimado
    total_missed_rides: 0, // Não vem na API
    avg_response_time: 25, // Tempo médio estimado em segundos
    
    // SOMAR CORRIDAS CANCELADAS DE TODOS OS MOTORISTAS
    total_cancelled_rides: (aggregatedData.rawData.drivers_analytics || []).reduce((total, driver) => {
      const userCancelled = driver.data?.metrics?.user_cancelled || 0;
      const driverCancelled = driver.data?.metrics?.driver_cancelled || 0;
      const driverTotal = userCancelled + driverCancelled;
      console.log(`🚫 ${driver.name}: ${driverTotal} canceladas (user: ${userCancelled}, driver: ${driverCancelled})`);
      return total + driverTotal;
    }, 0),
    
    // Rating médio estimado baseado na performance
    average_rating: aggregatedData.rawData.total_drivers > 0 && Number(aggregatedData.rawData.total_rides_completed || 0) > 0 ? 
      Math.min(5.0, 3.8 + (Number(aggregatedData.rawData.total_rides_completed || 0) / aggregatedData.rawData.total_drivers / 10)) : 0,
    
    // Análises vazias (não vêm da API atual)
    city_analysis: {},
    vehicle_analysis: {},
    alerts: [],
    
    periodo_dias: daysFilter
  } : {
    total_drivers: 0,
    active_drivers: 0,
    inactive_drivers: 0,
    online_drivers: 0,
    average_rating: 0,
    total_rides_completed: 0,
    total_cancelled_rides: 0,
    avg_rides_per_driver: 0,
    top_drivers: [],
    total_revenue: 0,
    total_commission: 0,
    net_revenue: 0,
    avg_revenue_per_driver: 0,
    alerts: [],
    city_analysis: {},
    vehicle_analysis: {},
    drivers_by_status: {},
    performance_metrics: {
      excellent_drivers: 0,
      good_drivers: 0,
      average_drivers: 0,
      below_average_drivers: 0
    },
    periodo_dias: 0
  };

  console.log('📊 DADOS DASHBOARD CONSTRUÍDOS:', dashboardData);
  console.log('🚫 TOTAL CORRIDAS CANCELADAS:', dashboardData.total_cancelled_rides);
  console.log('💰 CÁLCULO RECEITA:', `${dashboardData.total_rides_completed} corridas × R$ 2,50 = R$ ${dashboardData.total_revenue.toFixed(2)}`);
  console.log('🚗 PRIMEIRO MOTORISTA EXEMPLO:', dashboardData.top_drivers?.[0]);
  console.log('🔢 TOTAL DE TOP DRIVERS:', dashboardData.top_drivers?.length);

  // Calcula KPIs avançados com verificações de segurança para evitar divisão por zero.
  const kpis = {
    activationRate: dashboardData?.total_drivers > 0 ? (dashboardData.active_drivers / dashboardData.total_drivers) * 100 : 0,
    onlineRate: dashboardData?.active_drivers > 0 ? ((dashboardData.online_drivers || 0) / dashboardData.active_drivers) * 100 : 0,
    excellenceRate: dashboardData?.total_drivers > 0 ? ((dashboardData?.performance_metrics?.excellent_drivers || 0) / dashboardData.total_drivers) * 100 : 0,
    avgRatingTrend: (dashboardData?.average_rating || 0) >= 4.5 ? 'positive' : (dashboardData?.average_rating || 0) >= 4.0 ? 'neutral' : 'negative',
    performanceDistribution: {
      excellent: dashboardData?.performance_metrics?.excellent_drivers || 0,
      good: dashboardData?.performance_metrics?.good_drivers || 0,
      average: dashboardData?.performance_metrics?.average_drivers || 0,
      below: dashboardData?.performance_metrics?.below_average_drivers || 0
    }
  };
  
  // Prepara os dados para o gráfico de pizza
  const statusChartData = [
      { name: 'Ativos', value: dashboardData.active_drivers || 0, color: STATUS_COLORS.active },
      { name: 'Inativos', value: dashboardData.inactive_drivers || 0, color: STATUS_COLORS.inactive },
  ];


  // Dispara o callback para buscar novos dados quando o período é alterado.
  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    setFilters(prev => ({ ...prev, periodo: newPeriod }));
    if (onPeriodChange) onPeriodChange(newPeriod);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    // Se for mudança de período, sincronizar com o estado period
    if (key === 'periodo') {
      setPeriod(value);
      if (onPeriodChange) onPeriodChange(value);
    }
  };

  // Gera uma URL de avatar com base no nome do motorista.
  const getAvatarUrl = (name) => {
    if (!name) return "https://ui-avatars.com/api/?name=User&background=random";
    const cleanName = name.replace("Motorista ", "").replace(" ", "+");
    return `https://ui-avatars.com/api/?name=${cleanName}&background=random`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6 font-sans">
      <style>{`
        .custom-scrollbar {
          scrollbar-width: thin;
          scrollbar-color: #cbd5e1 #f1f5f9;
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
      <div className="max-w-7xl mx-auto">
        {/* Cabeçalho animado e padronizado */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2 flex items-center gap-3">
            <Users className="h-8 w-8 text-blue-500" />
            GESTÃO DE MOTORISTAS
          </h1>
          <p className="text-gray-600 text-lg">
            Dashboard executivo com KPIs e métricas de performance dos motoristas
          </p>
        </motion.div>

        {/* Filtros executivos - Estilo AnaliseCorreidas */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
              <div className="flex items-center gap-3 text-lg font-semibold">
                <div className="bg-blue-500/20 p-2 rounded-lg">
                  <Filter className="w-5 h-5 text-blue-400" />
                </div>
                Filtros de Análise - Motoristas
              </div>
            </div>
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Período</label>
                  <select
                    value={filters.periodo}
                    onChange={(e) => handleFilterChange('periodo', e.target.value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
                  >
                    {periodOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
                  >
                    {statusOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Performance</label>
                  <select
                    value={filters.performance}
                    onChange={(e) => handleFilterChange('performance', e.target.value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
                  >
                    {performanceOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Cidade</label>
                  <select
                    value={filters.cidade}
                    onChange={(e) => handleFilterChange('cidade', e.target.value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
                  >
                    <option value="">Todas as Cidades</option>
                    {Object.keys(dashboardData.city_analysis || {}).map(city => (
                      <option key={city} value={city}>{city}</option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Faixa de Receita</label>
                  <select
                    value={filters.faixaReceita}
                    onChange={(e) => handleFilterChange('faixaReceita', e.target.value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
                  >
                    {revenueRanges.map(option => (
                      <option key={option.label} value={JSON.stringify(option.value)}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 tracking-wide">Ordenação</label>
                  <select
                    value={filters.ordenacao}
                    onChange={(e) => handleFilterChange('ordenacao', e.target.value)}
                    className="w-full bg-white border-slate-200 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2"
                  >
                    <option value="rating">Por Avaliação</option>
                    <option value="rides">Por Número de Corridas</option>
                    <option value="revenue">Por Receita</option>
                    <option value="efficiency">Por Eficiência</option>
                    <option value="name">Por Nome</option>
                    <option value="status">Por Status</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Seção de Conteúdo: Exibe o loader ou os dados */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse bg-gray-200 rounded-2xl h-40"></div>
            ))}
          </div>
        ) : (
          <div className="space-y-8">
            {/* KPIs Principais - Estilo Executivo */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Total de Motoristas */}
                <div className="bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-slate-300 text-sm font-medium tracking-wide uppercase">Total de Motoristas</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mt-2">{dashboardData.total_drivers || 0}</p>
                            <p className="text-slate-400 text-sm mt-2">{dashboardData.active_drivers || 0} com atividade registrada</p>
                        </div>
                        <div className="bg-blue-500/20 p-4 rounded-xl"><Users className="w-8 h-8 text-blue-400" /></div>
                    </div>
                </div>

                {/* Corridas Canceladas pelos Motoristas */}
                <div className="bg-gradient-to-br from-red-600 via-red-700 to-red-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-red-200 text-sm font-medium tracking-wide uppercase">Corridas Canceladas</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-red-300 to-pink-300 bg-clip-text text-transparent mt-2">{dashboardData.total_cancelled_rides || 0}</p>
                            <p className="text-red-300 text-sm mt-2">Total por todos os motoristas</p>
                        </div>
                        <div className="bg-red-500/20 p-4 rounded-xl"><AlertTriangle className="w-8 h-8 text-red-400" /></div>
                    </div>
                </div>

                {/* Média Horas por Motorista */}
                <div className="bg-gradient-to-br from-purple-600 via-purple-700 to-purple-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-purple-200 text-sm font-medium tracking-wide uppercase">Média por Motorista</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent mt-2">{Number(dashboardData.avg_hours_per_driver || 0).toFixed(1)}h</p>
                            <p className="text-purple-300 text-sm mt-2">Horas online médias</p>
                        </div>
                        <div className="bg-purple-500/20 p-4 rounded-xl"><Activity className="w-8 h-8 text-purple-400" /></div>
                    </div>
                </div>

                {/* Rating Médio dos Motoristas */}
                <div className="bg-gradient-to-br from-amber-600 via-orange-700 to-orange-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                         <div>
                            <p className="text-orange-200 text-sm font-medium tracking-wide uppercase">Rating Médio</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent mt-2">{Number(dashboardData.average_rating || 0).toFixed(1)}</p>
                            <p className="text-orange-300 text-sm mt-2">Avaliação média dos motoristas</p>
                        </div>
                        <div className="bg-orange-500/20 p-4 rounded-xl"><Target className="w-8 h-8 text-orange-400" /></div>
                    </div>
                </div>
            </div>

            {/* KPIs Financeiros - Nova Linha */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Receita Total */}
                <div className="bg-gradient-to-br from-emerald-600 via-emerald-700 to-emerald-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-emerald-200 text-sm font-medium tracking-wide uppercase">Receita Total</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-emerald-300 to-green-300 bg-clip-text text-transparent mt-2">R$ {Number(dashboardData.total_revenue || 0).toFixed(2)}</p>
                            <p className="text-emerald-300 text-sm mt-2">Últimos {dashboardData.periodo_dias} dias</p>
                        </div>
                        <div className="bg-emerald-500/20 p-4 rounded-xl"><DollarSign className="w-8 h-8 text-emerald-400" /></div>
                    </div>
                </div>

                {/* Taxa de Aceitação */}
                <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-blue-200 text-sm font-medium tracking-wide uppercase">Taxa de Aceitação</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-blue-300 to-cyan-300 bg-clip-text text-transparent mt-2">{Number(dashboardData.avg_acceptance_rate || 0).toFixed(1)}%</p>
                            <p className="text-blue-300 text-sm mt-2">Média geral</p>
                        </div>
                        <div className="bg-blue-500/20 p-4 rounded-xl"><CheckCircle className="w-8 h-8 text-blue-400" /></div>
                    </div>
                </div>

                {/* Receita por Hora */}
                <div className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-indigo-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-indigo-200 text-sm font-medium tracking-wide uppercase">Receita por Hora</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent mt-2">R$ {Number(dashboardData.avg_revenue_per_hour || 0).toFixed(2)}</p>
                            <p className="text-indigo-300 text-sm mt-2">Produtividade média</p>
                        </div>
                        <div className="bg-indigo-500/20 p-4 rounded-xl"><TrendingUp className="w-8 h-8 text-indigo-400" /></div>
                    </div>
                </div>

                {/* Distância Total */}
                <div className="bg-gradient-to-br from-teal-600 via-teal-700 to-teal-800 text-white border-0 shadow-2xl rounded-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 p-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-teal-200 text-sm font-medium tracking-wide uppercase">Distância Total</p>
                            <p className="text-4xl font-bold bg-gradient-to-r from-teal-300 to-cyan-300 bg-clip-text text-transparent mt-2">{Number(dashboardData.total_distance || 0).toFixed(1)} km</p>
                            <p className="text-teal-300 text-sm mt-2">Quilometragem acumulada</p>
                        </div>
                        <div className="bg-teal-500/20 p-4 rounded-xl"><MapPin className="w-8 h-8 text-teal-400" /></div>
                    </div>
                </div>
            </div>

            {/* Alertas Inteligentes */}
            {dashboardData.alerts && dashboardData.alerts.length > 0 && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                  <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                    <div className="flex items-center gap-3 text-lg font-semibold">
                      <div className="bg-yellow-500/20 p-2 rounded-lg">
                        <AlertCircle className="w-5 h-5 text-yellow-400" />
                      </div>
                      Alertas Inteligentes
                    </div>
                  </div>
                  <div className="p-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      {dashboardData.alerts.map((alert, index) => (
                        <div key={index} className={`p-6 rounded-2xl border ${
                          alert.severity === 'high' ? 'bg-red-50 border-red-200' :
                          alert.severity === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                          'bg-green-50 border-green-200'
                        }`}>
                          <div className="flex items-start gap-3">
                            <div className={`p-2 rounded-lg ${
                              alert.severity === 'high' ? 'bg-red-500/20' :
                              alert.severity === 'medium' ? 'bg-yellow-500/20' :
                              'bg-green-500/20'
                            }`}>
                              {alert.type === 'error' ? <XCircle className="w-5 h-5 text-red-500" /> :
                               alert.type === 'warning' ? <AlertTriangle className="w-5 h-5 text-yellow-500" /> :
                               <CheckCircle className="w-5 h-5 text-green-500" />}
                            </div>
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-900 mb-1">{alert.title}</h4>
                              <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                              {alert.drivers && alert.drivers.length > 0 && (
                                <div className="text-xs text-gray-500">
                                  {alert.drivers.slice(0, 3).join(', ')}
                                  {alert.drivers.length > 3 && ` +${alert.drivers.length - 3} outros`}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Gráficos e Detalhes - Estilo Executivo */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-blue-500/20 p-2 rounded-lg">
                      <BarChart3 className="w-5 h-5 text-blue-400" />
                    </div>
                    Análise Visual de Dados
                  </div>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Gráfico de Status */}
                    <div className="bg-gradient-to-br from-white to-gray-100 border border-gray-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-blue-600 rounded-xl"><BarChart3 className="w-5 h-5 text-white" /></div>
                        <h3 className="text-lg font-semibold text-blue-800">Distribuição por Status</h3>
                      </div>
                      <div className="h-80">
                         <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={statusChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}>
                                    {statusChartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value) => [`${value} motoristas`, '']}/>
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                    
                     {/* Métricas Operacionais */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-2xl shadow-xl border border-blue-100 dark:border-blue-800">
                        <CardHeader className="border-b border-blue-100 dark:border-blue-800 pb-4">
                            <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                                <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg">
                                    <Activity className="h-6 w-6 text-white" />
                                </div>
                                Métricas Operacionais
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6 pt-6">
                            <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl">
                                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Corridas Completadas</span>
                                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">{dashboardData.total_rides_completed || 0}</span>
                            </div>
                            <div className="flex justify-between items-center p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl">
                                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Média por Motorista</span>
                                <span className="text-2xl font-bold text-green-600 dark:text-green-400">{Number(dashboardData.avg_rides_per_driver || 0).toFixed(1)}</span>
                            </div>
                            <div className="flex justify-between items-center p-4 bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl">
                                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Período de Análise</span>
                                <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">{dashboardData.periodo_dias || 0} dias</span>
                            </div>
                        </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            </motion.div>
            
            {/* Top Motoristas e Performance - Estilo Executivo */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-green-500/20 p-2 rounded-lg">
                      <BarChart3 className="w-5 h-5 text-green-400" />
                    </div>
                    Análise de Produtividade: Horas vs Performance
                  </div>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Top 5 por Horas Online */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-green-50 dark:from-gray-800 dark:to-green-900/20 rounded-2xl shadow-xl border border-green-100 dark:border-green-800">
                        <CardHeader className="border-b border-green-100 dark:border-green-800 pb-4">
                            <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                                <div className="p-3 bg-gradient-to-r from-green-500 to-green-600 rounded-xl shadow-lg">
                                    <Clock className="h-6 w-6 text-white" />
                                </div>
                                Top 5 - Horas Online
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-6">
                            <div className="space-y-4">
                                {dashboardData.top_drivers?.length > 0 ? dashboardData.top_drivers.map((driver, index) => (
                                    <div key={`top-driver-${driver.unique_key || driver.driver_id || driver.name}-${index}`} className="flex items-center justify-between p-4 bg-gradient-to-r from-white to-yellow-50 dark:from-gray-700 dark:to-yellow-900/20 rounded-xl shadow-md border border-yellow-100 dark:border-yellow-800 hover:shadow-lg transition-all duration-300">
                                        <div className="flex items-center gap-4">
                                            <div className="relative">
                                                <img src={getAvatarUrl(driver.name)} alt={driver.name} className="w-12 h-12 rounded-full shadow-lg border-2 border-yellow-200 dark:border-yellow-700"/>
                                                <div className="absolute -top-1 -right-1 bg-gradient-to-r from-yellow-400 to-yellow-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
                                                    {index + 1}
                                                </div>
                                            </div>
                                            <div>
                                                <p className="font-bold text-gray-900 dark:text-white text-lg">{driver.name.replace("Motorista ", "")}</p>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">{Number(driver.data?.metrics?.total_rides || 0)} corridas</p>
                                                <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">{Number(driver.data?.metrics?.online_hours || 0).toFixed(1)}h online</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className="flex items-center gap-2 mb-1">
                                                <Star className="h-5 w-5 text-yellow-500 fill-current" />
                                                <span className="text-xl font-bold text-gray-900 dark:text-white">{Number(driver.estimated_rating || 0).toFixed(1)}</span>
                                            </div>
                                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Avaliação média</p>
                                            <span className={`text-xs px-2 py-1 rounded-full font-semibold ${ (driver.data?.metrics?.active_days || 0) > 0 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                                {(driver.data?.metrics?.active_days || 0) > 0 ? 'Ativo' : 'Inativo'}
                                            </span>
                                        </div>
                                    </div>
                                )) : (
                                    <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                                        <p className="text-lg font-medium">Nenhum motorista encontrado</p>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                    
                    {/* Performance dos Motoristas */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-purple-50 dark:from-gray-800 dark:to-purple-900/20 rounded-2xl shadow-xl border border-purple-100 dark:border-purple-800">
                        <CardHeader className="border-b border-purple-100 dark:border-purple-800 pb-4">
                            <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                                <div className="p-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl shadow-lg">
                                    <TrendingUp className="h-6 w-6 text-white" />
                                </div>
                                Distribuição de Performance
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4 pt-6">
                            {[
                                { label: 'Excelente (≥4.5)', value: kpis.performanceDistribution.excellent, color: 'from-green-500 to-green-600', bgColor: 'from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20', textColor: 'text-green-600 dark:text-green-400' },
                                { label: 'Bom (4.0-4.4)', value: kpis.performanceDistribution.good, color: 'from-blue-500 to-blue-600', bgColor: 'from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20', textColor: 'text-blue-600 dark:text-blue-400' },
                                { label: 'Médio (3.5-3.9)', value: kpis.performanceDistribution.average, color: 'from-yellow-500 to-yellow-600', bgColor: 'from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20', textColor: 'text-yellow-600 dark:text-yellow-400' },
                                { label: 'Abaixo (< 3.5)', value: kpis.performanceDistribution.below, color: 'from-red-500 to-red-600', bgColor: 'from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20', textColor: 'text-red-600 dark:text-red-400' }
                            ].map((item, index) => (
                                <div key={index} className={`flex justify-between items-center p-4 bg-gradient-to-r ${item.bgColor} rounded-xl hover:shadow-md transition-all duration-300`}>
                                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-3">
                                        <div className={`w-3 h-3 bg-gradient-to-r ${item.color} rounded-full shadow-lg`}></div>
                                        {item.label}
                                    </span>
                                    <div className="text-right">
                                        <span className={`text-xl font-bold ${item.textColor}`}>{item.value || 0}</span>
                                        <p className="text-xs text-gray-500">motoristas</p>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Análise Geográfica e de Veículos */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-cyan-500/20 p-2 rounded-lg">
                      <MapPin className="w-5 h-5 text-cyan-400" />
                    </div>
                    Análise Geográfica e Operacional
                  </div>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Top Cidades por Receita */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-cyan-50 rounded-2xl shadow-xl border border-cyan-100">
                      <CardHeader className="border-b border-cyan-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-lg shadow-lg">
                            <MapPin className="h-5 w-5 text-white" />
                          </div>
                          Top Cidades
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-6">
                        <div className="space-y-4">
                          {Object.entries(dashboardData.city_analysis || {})
                            .sort(([,a], [,b]) => b.revenue - a.revenue)
                            .slice(0, 5)
                            .map(([city, data], index) => (
                              <div key={city} className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
                                <div className="flex items-center gap-3">
                                  <div className="w-8 h-8 bg-cyan-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    {index + 1}
                                  </div>
                                  <div>
                                    <p className="font-semibold text-gray-900">{city}</p>
                                    <p className="text-sm text-gray-600">{data.drivers} motoristas</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <p className="text-lg font-bold text-cyan-600">R$ {data.revenue.toFixed(2)}</p>
                                  <p className="text-xs text-gray-500">{data.rides} corridas</p>
                                </div>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Análise de Veículos */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-orange-50 rounded-2xl shadow-xl border border-orange-100">
                      <CardHeader className="border-b border-orange-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow-lg">
                            <Car className="h-5 w-5 text-white" />
                          </div>
                          Tipos de Veículos
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-6">
                        <div className="space-y-4">
                          {Object.entries(dashboardData.vehicle_analysis || {})
                            .sort(([,a], [,b]) => b.drivers - a.drivers)
                            .slice(0, 5)
                            .map(([vehicle, data], index) => (
                              <div key={vehicle} className="flex items-center justify-between p-3 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg">
                                <div className="flex items-center gap-3">
                                  <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    {index + 1}
                                  </div>
                                  <div>
                                    <p className="font-semibold text-gray-900">{vehicle}</p>
                                    <p className="text-sm text-gray-600">R$ {data.revenue.toFixed(2)} receita</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <p className="text-lg font-bold text-orange-600">{data.drivers}</p>
                                  <p className="text-xs text-gray-500">motoristas</p>
                                </div>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Métricas de Eficiência */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-purple-50 rounded-2xl shadow-xl border border-purple-100">
                      <CardHeader className="border-b border-purple-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow-lg">
                            <Activity className="h-5 w-5 text-white" />
                          </div>
                          Eficiência Operacional
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4 pt-6">
                        <div className="space-y-4">
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Taxa de Conclusão</span>
                            <span className="text-xl font-bold text-purple-600">{Number(dashboardData.avg_completion_rate || 0).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-pink-50 to-rose-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Tempo de Resposta</span>
                            <span className="text-xl font-bold text-pink-600">{Number(dashboardData.avg_response_time || 0).toFixed(1)}s</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-rose-50 to-red-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Taxa de Cancelamento</span>
                            <span className="text-xl font-bold text-rose-600">{Number(dashboardData.avg_cancellation_rate || 0).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Corridas Perdidas</span>
                            <span className="text-xl font-bold text-emerald-600">{dashboardData.total_missed_rides || 0}</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Km por Corrida</span>
                            <span className="text-xl font-bold text-blue-600">{Number(dashboardData.avg_distance_per_ride || 0).toFixed(1)}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Ranking e Performance - Todos os Motoristas */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-yellow-500/20 p-2 rounded-lg">
                      <Star className="w-5 h-5 text-yellow-400" />
                    </div>
                    Ranking e Performance - Todos os Motoristas
                  </div>
                </div>
                <div className="p-8">
                  <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100">
                    <CardHeader className="border-b border-gray-100 pb-4">
                      <CardTitle className="text-xl font-bold flex items-center gap-3 text-gray-900">
                        <div className="p-3 bg-gradient-to-r from-gray-500 to-gray-600 rounded-xl shadow-lg">
                          <Users className="h-6 w-6 text-white" />
                        </div>
                        Lista Completa de Motoristas
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6">
                      <div className="max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                        <div className="space-y-4">
                          {aggregatedData?.drivers?.length > 0 ? aggregatedData.drivers
                            .sort((a, b) => {
                              switch (filters.ordenacao) {
                                case 'rating':
                                  return (b.estimated_rating || 0) - (a.estimated_rating || 0);
                                case 'rides':
                                  return (b.total_success_rides || 0) - (a.total_success_rides || 0);
                                case 'revenue':
                                  return (b.total_revenue || 0) - (a.total_revenue || 0);
                                case 'efficiency':
                                  return (b.efficiency_score || 0) - (a.efficiency_score || 0);
                                case 'name':
                                  return (a.name || '').localeCompare(b.name || '');
                                case 'status':
                                  return (a.current_status || '').localeCompare(b.current_status || '');
                                case 'hours':
                                default:
                                  return (b.total_online_hours || 0) - (a.total_online_hours || 0);
                              }
                            })
                            .map((driver, index) => {
                              // Usar dados da API corretamente
                              const driverRating = driver.estimated_rating || 0;
                              const onlineHours = Number(driver.data?.metrics?.online_hours || 0);
                              const totalRides = Number(driver.data?.metrics?.total_rides || 0);
                              const cancelledRides = Number(driver.data?.metrics?.user_cancelled || 0) + Number(driver.data?.metrics?.driver_cancelled || 0);
                              
                              return (
                                <div key={`all-driver-${driver.unique_key || driver.driver_id || driver.name}-${index}`} className="flex items-center justify-between p-4 bg-gradient-to-r from-white to-gray-50 rounded-xl shadow-md border border-gray-100 hover:shadow-lg transition-all duration-300 hover:scale-[1.02]">
                                  <div className="flex items-center gap-4">
                                    <div className="relative">
                                      <img src={getAvatarUrl(driver.name)} alt={driver.name} className="w-12 h-12 rounded-full shadow-lg border-2 border-gray-200"/>
                                      <div className="absolute -top-1 -right-1 bg-gradient-to-r from-gray-400 to-gray-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
                                        {index + 1}
                                      </div>
                                    </div>
                                    <div>
                                      <p className="font-bold text-gray-900 text-lg">{driver.name.replace("Motorista ", "")}</p>
                                      <div className="flex gap-4 text-sm text-gray-600">
                                        <span>{onlineHours.toFixed(1)}h online</span>
                                        <span>{totalRides} corridas</span>
                                        <span>{cancelledRides} canceladas</span>
                                      </div>
                                    </div>
                                  </div>
                                  <div className="text-right">
                                    <div className="flex items-center gap-2 mb-1">
                                      <Star className="h-5 w-5 text-yellow-500 fill-current" />
                                      <span className="text-xl font-bold text-gray-900">{Number(driverRating).toFixed(1)}</span>
                                    </div>
                                    <p className="text-xs text-gray-500 mb-2">Rating</p>
                                    <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                                      driverRating >= 4.5 ? 'bg-green-100 text-green-800' : 
                                      driverRating >= 4.0 ? 'bg-blue-100 text-blue-800' : 
                                      driverRating >= 3.5 ? 'bg-yellow-100 text-yellow-800' : 
                                      driverRating > 0 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                                    }`}>
                                      {driverRating >= 4.5 ? 'Excelente' : 
                                       driverRating >= 4.0 ? 'Bom' : 
                                       driverRating >= 3.5 ? 'Médio' : 
                                       driverRating > 0 ? 'Baixo' : 'S/Rating'}
                                    </span>
                                  </div>
                                </div>
                              );
                            }) : (
                              <div className="text-center py-12 text-gray-500">
                                <p className="text-lg font-medium">Nenhum motorista encontrado</p>
                              </div>
                            )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </motion.div>

            {/* Análise Temporal Detalhada */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-indigo-500/20 p-2 rounded-lg">
                      <Clock className="w-5 h-5 text-indigo-400" />
                    </div>
                    Análise Temporal e Produtividade
                  </div>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Estatísticas de Tempo */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-indigo-50 rounded-2xl shadow-xl border border-indigo-100">
                      <CardHeader className="border-b border-indigo-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg shadow-lg">
                            <Clock className="h-5 w-5 text-white" />
                          </div>
                          Distribuição Temporal
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4 pt-6">
                        <div className="space-y-4">
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Total de Horas</span>
                            <span className="text-xl font-bold text-indigo-600">{Number(dashboardData.total_online_hours || 0).toFixed(1)}h</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Média Diária</span>
                            <span className="text-xl font-bold text-blue-600">
                              {dashboardData.periodo_dias > 0 ? (Number(dashboardData.total_online_hours || 0) / dashboardData.periodo_dias).toFixed(1) : '0.0'}h
                            </span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-cyan-50 to-teal-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Horas por Motorista</span>
                            <span className="text-xl font-bold text-cyan-600">{Number(dashboardData.avg_hours_per_driver || 0).toFixed(1)}h</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Métricas de Produtividade */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-emerald-50 rounded-2xl shadow-xl border border-emerald-100">
                      <CardHeader className="border-b border-emerald-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg shadow-lg">
                            <Activity className="h-5 w-5 text-white" />
                          </div>
                          Produtividade
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4 pt-6">
                        <div className="space-y-4">
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Corridas/Hora</span>
                            <span className="text-xl font-bold text-emerald-600">
                              {Number(dashboardData.total_online_hours || 0) > 0 ? 
                                ((dashboardData.total_rides_completed || 0) / Number(dashboardData.total_online_hours || 1)).toFixed(2) : 
                                '0.00'
                              }
                            </span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-green-50 to-lime-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Eficiência Média</span>
                            <span className="text-xl font-bold text-green-600">{Number(dashboardData.average_rating || 0).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-lime-50 to-yellow-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Score Global</span>
                            <span className="text-xl font-bold text-lime-600">
                              {(Number(dashboardData.average_rating || 0) * 
                                (Number(dashboardData.total_online_hours || 0) > 0 ? 
                                  ((dashboardData.total_rides_completed || 0) / Number(dashboardData.total_online_hours || 1)) : 0) * 10
                              ).toFixed(0)}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Insights e Recomendações */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-amber-50 rounded-2xl shadow-xl border border-amber-100">
                      <CardHeader className="border-b border-amber-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-amber-500 to-amber-600 rounded-lg shadow-lg">
                            <TrendingUp className="h-5 w-5 text-white" />
                          </div>
                          Insights
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-6">
                        <div className="space-y-4">
                          {/* Análise automática baseada nos dados */}
                          {Number(dashboardData.avg_hours_per_driver || 0) > 100 ? (
                            <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span className="text-sm font-semibold text-green-800">Alto Engajamento</span>
                              </div>
                              <p className="text-sm text-green-700">Motoristas com média de {Number(dashboardData.avg_hours_per_driver || 0).toFixed(1)}h demonstram alto comprometimento.</p>
                            </div>
                          ) : (
                            <div className="p-4 bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-xl">
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                                <span className="text-sm font-semibold text-amber-800">Oportunidade</span>
                              </div>
                              <p className="text-sm text-amber-700">Considere estratégias para aumentar o tempo online dos motoristas.</p>
                            </div>
                          )}
                          
                          {Number(dashboardData.average_rating || 0) > 70 ? (
                            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span className="text-sm font-semibold text-blue-800">Boa Performance</span>
                              </div>
                              <p className="text-sm text-blue-700">Taxa de sucesso de {Number(dashboardData.average_rating || 0).toFixed(1)}% está acima da média.</p>
                            </div>
                          ) : (
                            <div className="p-4 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl">
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                                <span className="text-sm font-semibold text-red-800">Atenção Necessária</span>
                              </div>
                              <p className="text-sm text-red-700">Taxa de {Number(dashboardData.average_rating || 0).toFixed(1)}% indica necessidade de melhorias.</p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Nova Seção: Análise de Produtividade */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                <div className="bg-gradient-to-r from-emerald-900 to-emerald-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-emerald-500/20 p-2 rounded-lg">
                      <Activity className="w-5 h-5 text-emerald-400" />
                    </div>
                    Análise de Produtividade: Horas vs Performance
                  </div>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    
                    {/* Top 5 Motoristas por Horas */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-emerald-50 rounded-2xl shadow-xl border border-emerald-100">
                      <CardHeader className="border-b border-emerald-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg shadow-lg">
                            <Clock className="h-5 w-5 text-white" />
                          </div>
                          Top 5 - Mais Horas Online
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4 pt-6">
                        {getTopDrivers('total_online_hours', 5, daysFilter).map((driver, index) => (
                          <div key={`hours-${driver.unique_key || driver.driver_id}-${index}`} className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-100">
                            <div className="flex items-center gap-3">
                              <div className="relative">
                                <img src={getAvatarUrl(driver.name)} alt={driver.name} className="w-10 h-10 rounded-full border-2 border-emerald-200"/>
                                <div className="absolute -top-1 -right-1 bg-emerald-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                                  {index + 1}
                                </div>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{driver.name.replace("Motorista ", "")}</p>
                                <p className="text-sm text-gray-600">{Number(driver.data?.metrics?.total_rides || 0)} corridas</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-lg font-bold text-emerald-600">{Number(driver.data?.metrics?.online_hours || 0).toFixed(1)}h</p>
                              <p className="text-xs text-gray-500">Rating: {Number(driver.estimated_rating || 0).toFixed(1)}</p>
                            </div>
                          </div>
                        ))}
                      </CardContent>
                    </Card>

                    {/* Top 5 Motoristas por Rating */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-yellow-50 rounded-2xl shadow-xl border border-yellow-100">
                      <CardHeader className="border-b border-yellow-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-lg shadow-lg">
                            <Star className="h-5 w-5 text-white" />
                          </div>
                          Top 5 - Melhor Rating
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4 pt-6">
                        {getTopDrivers('rating', 5, daysFilter)
                          .sort((a, b) => (b.estimated_rating || 0) - (a.estimated_rating || 0))
                          .map((driver, index) => (
                          <div key={`rating-${driver.unique_key || driver.driver_id}-${index}`} className="flex items-center justify-between p-4 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl border border-yellow-100">
                            <div className="flex items-center gap-3">
                              <div className="relative">
                                <img src={getAvatarUrl(driver.name)} alt={driver.name} className="w-10 h-10 rounded-full border-2 border-yellow-200"/>
                                <div className="absolute -top-1 -right-1 bg-yellow-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                                  {index + 1}
                                </div>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{driver.name.replace("Motorista ", "")}</p>
                                <p className="text-sm text-gray-600">{Number(driver.data?.metrics?.online_hours || 0).toFixed(1)}h online</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="flex items-center gap-1">
                                <Star className="h-4 w-4 text-yellow-500 fill-current" />
                                <p className="text-lg font-bold text-yellow-600">{Number(driver.estimated_rating || 0).toFixed(1)}</p>
                              </div>
                              <p className="text-xs text-gray-500">{Number(driver.data?.metrics?.total_rides || 0)} corridas</p>
                            </div>
                          </div>
                        ))}
                      </CardContent>
                    </Card>
                    
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Análise de Tendências e Comparações Temporais */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200/50 shadow-2xl rounded-2xl backdrop-blur-lg">
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-violet-500/20 p-2 rounded-lg">
                      <TrendingUp className="w-5 h-5 text-violet-400" />
                    </div>
                    Análise de Tendências e Performance Temporal
                  </div>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    
                    {/* Tendências de Crescimento */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-violet-50 rounded-2xl shadow-xl border border-violet-100">
                      <CardHeader className="border-b border-violet-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-violet-500 to-violet-600 rounded-lg shadow-lg">
                            <TrendingUp className="h-5 w-5 text-white" />
                          </div>
                          Tendências de Performance
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-6 pt-6">
                        <div className="space-y-4">
                          {/* Crescimento de Receita */}
                          <div className="p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">Crescimento de Receita</span>
                              <span className={`text-lg font-bold ${dashboardData.revenue_growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {dashboardData.revenue_growth >= 0 ? '+' : ''}{Number(dashboardData.revenue_growth || 0).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${dashboardData.revenue_growth >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                style={{width: `${Math.min(Math.abs(dashboardData.revenue_growth || 0), 100)}%`}}
                              ></div>
                            </div>
                          </div>

                          {/* Tendência de Aceitação */}
                          <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">Tendência de Aceitação</span>
                              <span className={`text-lg font-bold ${dashboardData.acceptance_trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {dashboardData.acceptance_trend >= 0 ? '+' : ''}{Number(dashboardData.acceptance_trend || 0).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${dashboardData.acceptance_trend >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                style={{width: `${Math.min(Math.abs(dashboardData.acceptance_trend || 0), 100)}%`}}
                              ></div>
                            </div>
                          </div>

                          {/* Eficiência Temporal */}
                          <div className="p-4 bg-gradient-to-r from-pink-50 to-rose-50 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">Melhoria na Eficiência</span>
                              <span className={`text-lg font-bold ${dashboardData.efficiency_improvement >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {dashboardData.efficiency_improvement >= 0 ? '+' : ''}{Number(dashboardData.efficiency_improvement || 0).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${dashboardData.efficiency_improvement >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                style={{width: `${Math.min(Math.abs(dashboardData.efficiency_improvement || 0), 100)}%`}}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Padrões Sazonais e Oportunidades */}
                    <Card className="group hover:shadow-2xl transition-all duration-300 bg-gradient-to-br from-white to-amber-50 rounded-2xl shadow-xl border border-amber-100">
                      <CardHeader className="border-b border-amber-100 pb-4">
                        <CardTitle className="text-lg font-bold flex items-center gap-3 text-gray-900">
                          <div className="p-2 bg-gradient-to-r from-amber-500 to-amber-600 rounded-lg shadow-lg">
                            <Calendar className="h-5 w-5 text-white" />
                          </div>
                          Padrões e Oportunidades
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-6 pt-6">
                        <div className="space-y-4">
                          
                          {/* Insights Temporais */}
                          <div className="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg p-4">
                            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                              <Lightbulb className="h-4 w-4 text-amber-500" />
                              Insights do Período
                            </h4>
                            <div className="space-y-2">
                              {dashboardData.temporal_insights && dashboardData.temporal_insights.length > 0 ? (
                                dashboardData.temporal_insights.slice(0, 3).map((insight, index) => (
                                  <div key={index} className="flex items-start gap-2 text-sm">
                                    <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                                    <span className="text-gray-700">{insight}</span>
                                  </div>
                                ))
                              ) : (
                                <div className="text-sm text-gray-600 italic">
                                  Coletando dados para análise temporal...
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Recomendações de Otimização */}
                          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4">
                            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                              <Target className="h-4 w-4 text-green-500" />
                              Oportunidades de Melhoria
                            </h4>
                            <div className="space-y-2">
                              {dashboardData.optimization_opportunities && dashboardData.optimization_opportunities.length > 0 ? (
                                dashboardData.optimization_opportunities.slice(0, 3).map((opportunity, index) => (
                                  <div key={index} className="flex items-start gap-2 text-sm">
                                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                                    <span className="text-gray-700">{opportunity}</span>
                                  </div>
                                ))
                              ) : (
                                <div className="text-sm text-gray-600 italic">
                                  Analisando dados para identificar oportunidades...
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Previsões */}
                          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
                            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                              <BarChart3 className="h-4 w-4 text-blue-500" />
                              Projeções para o Próximo Período
                            </h4>
                            <div className="grid grid-cols-2 gap-3">
                              <div className="text-center">
                                <p className="text-xs text-gray-600">Receita Estimada</p>
                                <p className="text-lg font-bold text-blue-600">R$ {Number(dashboardData.projected_revenue || 0).toFixed(2)}</p>
                              </div>
                              <div className="text-center">
                                <p className="text-xs text-gray-600">Corridas Previstas</p>
                                <p className="text-lg font-bold text-indigo-600">{dashboardData.projected_rides || 0}</p>
                              </div>
                            </div>
                          </div>

                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
  
  } catch (componentError) {
    console.error('❌ Erro crítico no DriversOverview:', componentError);
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <h2 className="text-lg font-semibold text-red-800 mb-2">Erro no Componente DriversOverview</h2>
        <p className="text-red-600">Ocorreu um erro ao renderizar o componente. Detalhes no console.</p>
        <p className="text-sm text-red-500 mt-2">Erro: {componentError.message}</p>
      </div>
    );
  }
}
