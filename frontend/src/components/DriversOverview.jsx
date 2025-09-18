import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, Star, TrendingUp, UserCheck, Activity, Award, AlertTriangle, Clock, BarChart3, Wifi, Filter, Target, DollarSign, MapPin, Car, AlertCircle, CheckCircle, XCircle, TrendingDown, Calendar, Lightbulb, RefreshCw, Eye } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend, BarChart, Bar, XAxis, YAxis, LineChart, Line } from 'recharts';
import DriverDetailsModal from './DriverDetailsModal';
import { useDriverModal } from '../hooks/useDriverModal';


const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: '7 dias', value: '7_days' },
  { label: '30 dias', value: '30_days' },
  { label: '3 meses', value: '3_months' },
  { label: '6 meses', value: '6_months' },
  { label: '12 meses', value: '12_months' }
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
    const [period, setPeriod] = useState('6_months'); // Mudado para 6 meses
    const [filters, setFilters] = useState({
      period: '6_months', // Mudado para 6 meses para incluir dados históricos
      status: 'all',
      performance: 'all',
      order_by: 'rating',
      city: 'all',
      vehicle: 'all',
      revenue_range: 'all',
      alerts: true
    });

    const [showComparison, setShowComparison] = useState(false);
    const [selectedAlert, setSelectedAlert] = useState('');

    // Hook para modal de detalhes do motorista
    const { isModalOpen, selectedDriverId, selectedDriverName, openModal, closeModal } = useDriverModal();

    // Estados para dados dos motoristas usando nossa API real
    const [driversData, setDriversData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [kpisData, setKpisData] = useState({});
    const [citiesData, setCitiesData] = useState([]);

    // Configuração da API
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Função para buscar KPIs da nossa API
    const fetchKpis = async () => {
      try {
        console.log('Buscando KPIs com parâmetros:', { 
          period: filters.period, 
          city: filters.city, 
          status: filters.status 
        });
        const response = await fetch(`${API_URL}/api/drivers/kpis?period=${filters.period}&city=${filters.city}&status=${filters.status}`);
        const result = await response.json();
        console.log('Resposta da API de KPIs:', result);
        if (result.success) {
          setKpisData(result.data);
          return result.data;
        }
        return null;
      } catch (err) {
        console.error('Erro ao buscar KPIs:', err);
        return null;
      }
    };

    // Função para buscar lista de motoristas da nossa API
    const fetchDrivers = async () => {
      try {
        const queryParams = new URLSearchParams({
          period: filters.period,
          city: filters.city,
          status: filters.status,
          performance: filters.performance,
          revenue_range: filters.revenue_range,
          order_by: filters.order_by,
          limit: '1000', // Aumentado para garantir que pegue todos os motoristas
          offset: '0'
        });

        console.log('Buscando motoristas com parâmetros:', Object.fromEntries(queryParams));
        const response = await fetch(`${API_URL}/api/drivers/list?${queryParams}`);
        const result = await response.json();
        
        console.log('Resposta da API de motoristas:', result);
        if (result.success) {
          console.log('🎯 SETANDO driversData com:', result.data.drivers);
          console.log('🎯 TAMANHO DO ARRAY:', result.data.drivers?.length);
          setDriversData(result.data.drivers);
          return result.data.drivers;
        } else {
          console.log('❌ API retornou success: false');
        }
        return [];
      } catch (err) {
        console.error('Erro ao buscar motoristas:', err);
        return [];
      }
    };

    // Função para buscar cidades da nossa API
    const fetchCities = async () => {
      try {
        const response = await fetch(`${API_URL}/api/drivers/cities`);
        const result = await response.json();
        console.log('Resposta da API de cidades:', result);
        if (result.success) {
          // A API agora retorna as cidades com codificação correta
          console.log('Cidades recebidas:', result.data);
          setCitiesData(result.data);
          return result.data;
        }
        return [];
      } catch (err) {
        console.error('Erro ao buscar cidades:', err);
        return [];
      }
    };

    // Carregar dados quando componente monta ou filtros mudam
    useEffect(() => {
      const loadData = async () => {
        setLoading(true);
        setError(null);
        
        try {
          await Promise.all([
            fetchKpis(),
            fetchDrivers(),
            fetchCities()
          ]);
        } catch (err) {
          setError('Erro ao carregar dados dos motoristas');
          console.error('Erro geral:', err);
        } finally {
          setLoading(false);
        }
      };

      loadData();
    }, [filters]);

    // Função SIMPLIFICADA para usar dados da API DIRETAMENTE
    const calculateAggregatedMetrics = () => {
      // Se não tem dados, retorna null
      if (!kpisData || Object.keys(kpisData).length === 0) {
        console.log('❌ Sem dados de KPIs disponíveis');
        return null;
      }
      
      console.log('✅ Usando dados DIRETOS da API:', kpisData);
      
      // Retorna os dados EXATAMENTE como vêm da API (já filtrados)
      return {
        rawData: kpisData,
        drivers: driversData || []
      };
    };

    const getTopDrivers = (sortBy = 'rating', limit = 5, daysFilter = 30) => {
      if (!driversData || driversData.length === 0) return [];
      
      // Os dados já vêm filtrados da API, só precisamos ordenar
      let sortedDrivers = [...driversData];
      
      switch (sortBy) {
        case 'total_online_hours':
          sortedDrivers.sort((a, b) => (b.data?.metrics?.online_hours || 0) - (a.data?.metrics?.online_hours || 0));
          break;
        case 'rating':
          sortedDrivers.sort((a, b) => (b.estimated_rating || 0) - (a.estimated_rating || 0));
          break;
        case 'total_rides':
          sortedDrivers.sort((a, b) => (b.data?.metrics?.total_rides || 0) - (a.data?.metrics?.total_rides || 0));
          break;
        default:
          sortedDrivers.sort((a, b) => (b.estimated_rating || 0) - (a.estimated_rating || 0));
      }
      
      return sortedDrivers.slice(0, limit);
    };

    const getFilteredDrivers = (filterParams = {}) => {
      // Como o backend já está filtrando corretamente, 
      // retornamos todos os dados que já vêm filtrados da API
      return driversData || [];
    };

    const getTemporalComparison = () => {
      return {
        current: kpisData,
        previous: {}
      };
    };

    const getSpecificAlerts = () => {
      return [];
    };

    // Calcular análise de tipos de veículos dos motoristas filtrados
    const getVehicleAnalysis = () => {
      if (!driversData || driversData.length === 0) {
        return {};
      }

      const vehicleStats = {};

      driversData.forEach(driver => {
        // PULAR motoristas sem personal_data válido
        if (!driver.data?.personal_data) {
          return; // Pula para o próximo motorista
        }

        // Extrair tipo de veículo do personal_data
        let vehicleType = 'Não especificado';
        
        try {
          const personalData = typeof driver.data.personal_data === 'string' 
            ? JSON.parse(driver.data.personal_data) 
            : driver.data.personal_data;
          vehicleType = personalData.vehicle_type || 'Não especificado';
        } catch (error) {
          console.error('Erro ao processar personal_data:', error);
          return; // Pula se houver erro no parse
        }

        // Inicializar dados do veículo se não existir
        if (!vehicleStats[vehicleType]) {
          vehicleStats[vehicleType] = {
            drivers: 0,
            revenue: 0,
            rides: 0
          };
        }

        // Incrementar estatísticas
        vehicleStats[vehicleType].drivers += 1;
        vehicleStats[vehicleType].revenue += driver.revenue || 0;
        vehicleStats[vehicleType].rides += driver.total_rides || 0;
      });

      return vehicleStats;
    };

    // Calcular métricas de eficiência operacional
    const getOperationalMetrics = () => {
      if (!driversData || driversData.length === 0 || !kpisData) {
        return {
          completionRate: 0,
          responseTime: 0,
          cancellationRate: 0,
          lostRides: 0,
          kmPerRide: 0
        };
      }

      const totalRides = kpisData.total_rides || 0;
      const cancelledRides = kpisData.cancelled_rides || 0;
      const totalDistance = kpisData.total_distance || 0;

      return {
        completionRate: totalRides > 0 ? ((totalRides - cancelledRides) / totalRides * 100) : 0,
        responseTime: 45, // Simulado - poderia vir de dados reais
        cancellationRate: totalRides > 0 ? (cancelledRides / totalRides * 100) : 0,
        lostRides: cancelledRides,
        kmPerRide: totalRides > 0 ? (totalDistance / totalRides) : 0
      };
    };

    // Calcular métricas baseadas no período selecionado
  const daysMap = {
    'hoje': 1,
    '7_days': 7,
    '30_days': 30,
    '3_months': 90,
    '6_months': 180,
    '12_months': 365
  };
  const daysFilter = daysMap[filters.period] || daysMap[period] || 180; // Usar filters.period primeiro
  
  // Aplicar filtros aos dados antes de calcular métricas - SIMPLIFICADO
  // Os dados já vêm filtrados da API, não precisamos filtrar novamente
  let filteredData = driversData || [];
  let aggregatedData = null;
  
  try {
    // Não precisa passar parâmetros, pois a função usa kpisData e driversData que já estão no escopo
    aggregatedData = calculateAggregatedMetrics();
    console.log('Métricas agregadas calculadas:', aggregatedData);
  } catch (error) {
    console.error('Erro em calculateAggregatedMetrics:', error);
    aggregatedData = null;
  }

  // Debug: Log dos dados recebidos
  console.log('DriversOverview - dados agregados:', aggregatedData);
  console.log('DriversOverview - driversData original:', driversData);
  console.log('DriversOverview - driversData length:', driversData?.length);
  console.log('DriversOverview - loading:', loading);
  console.log('🔍 DADOS EXATOS DA API:', aggregatedData?.rawData);
  console.log('🔍 DRIVERS ARRAY:', aggregatedData?.drivers);
  console.log('🔍 DRIVERS ARRAY LENGTH:', aggregatedData?.drivers?.length);

  // DADOS DIRETOS DA API - SEM TRANSFORMAÇÕES DESNECESSÁRIAS
  const dashboardData = aggregatedData && aggregatedData.rawData ? 
    aggregatedData.rawData : {
      total_drivers: 0,
      active_drivers: 0,
      inactive_drivers: 0,
      online_drivers: 0,
      average_rating: 0,
      total_rides_completed: 0,
      total_cancelled_rides: 0,
      avg_rides_per_driver: 0,
      total_revenue: 0,
      avg_hours_online: 0,
      acceptance_rate: 0,
      revenue_per_hour: 0,
      total_distance: 0
    };

  console.log('📊 DADOS DASHBOARD SIMPLIFICADOS:', dashboardData);
  
  // Top drivers simples - limitado a 5
  const topDrivers = (aggregatedData?.drivers || []).slice(0, 5);

  // KPIs SIMPLES usando dados diretos da API
  const kpis = {
    activationRate: dashboardData?.total_drivers > 0 ? (dashboardData.active_drivers / dashboardData.total_drivers) * 100 : 0,
    onlineRate: dashboardData?.active_drivers > 0 ? ((dashboardData.online_drivers || 0) / dashboardData.active_drivers) * 100 : 0,
    excellenceRate: dashboardData?.kpi_metrics?.excellence_rate || 0,
    avgRatingTrend: (dashboardData?.average_rating || 0) >= 4.5 ? 'positive' : (dashboardData?.average_rating || 0) >= 4.0 ? 'neutral' : 'negative',
    performanceDistribution: dashboardData?.performance_metrics || {
      excellent: 0,
      good: 0,
      average: 0,
      below: 0
    }
  };
  
  // Status chart SIMPLES
  const statusChartData = [
    { name: 'Ativos', value: dashboardData?.active_drivers || 0, color: STATUS_COLORS.active },
    { name: 'Inativos', value: dashboardData?.inactive_drivers || 0, color: STATUS_COLORS.inactive },
  ];


  // Dispara o callback para buscar novos dados quando o período é alterado.
  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    setFilters(prev => ({ ...prev, period: newPeriod }));
    if (onPeriodChange) onPeriodChange(newPeriod);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    // Se for mudança de período, sincronizar com o estado period
    if (key === 'period') {
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
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
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Cabeçalho animado e padronizado */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }} 
          animate={{ opacity: 1, y: 0 }} 
          className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
            <Users className="h-8 w-8 text-blue-500" />
            GESTÃO DE MOTORISTAS
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Dashboard executivo com KPIs e métricas de performance dos motoristas
          </p>
          
          {/* Indicadores de Status dos Dados */}
          <div className="flex items-center gap-4 mt-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${loading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></div>
              <span className="text-sm text-gray-600">Dados Analíticos: {loading ? 'Carregando...' : 'Conectado'}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-sm text-gray-600">
                Modal de Detalhes: Disponível
              </span>
            </div>
          </div>
        </motion.div>

        {/* Filtros executivos - Estilo AnaliseCorreidas */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="bg-white dark:bg-gray-800 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 dark:bg-blue-900 p-2 rounded-lg">
                <Filter className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filtros de Análise - Motoristas</h2>
            </div>
          </div>
          <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Período</label>
                  <select
                    value={filters.period}
                    onChange={(e) => handleFilterChange('period', e.target.value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2 text-gray-900 dark:text-white"
                  >
                    {periodOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2 text-gray-900 dark:text-white"
                  >
                    {statusOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Performance</label>
                  <select
                    value={filters.performance}
                    onChange={(e) => handleFilterChange('performance', e.target.value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2 text-gray-900 dark:text-white"
                  >
                    {performanceOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Cidade</label>
                  <select
                    value={filters.city}
                    onChange={(e) => handleFilterChange('city', e.target.value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2 text-gray-900 dark:text-white"
                  >
                    <option value="all">Todas as Cidades</option>
                    {citiesData && citiesData.length > 0 ? citiesData.map(city => (
                      <option key={city} value={city}>{city}</option>
                    )) : (
                      <option disabled>Carregando cidades...</option>
                    )}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Faixa de Receita</label>
                  <select
                    value={filters.revenue_range}
                    onChange={(e) => handleFilterChange('revenue_range', e.target.value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2 text-gray-900 dark:text-white"
                  >
                    {revenueRanges.map(option => (
                      <option key={option.label} value={JSON.stringify(option.value)}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-600 dark:text-gray-400 tracking-wide">Ordenação</label>
                  <select
                    value={filters.order_by}
                    onChange={(e) => handleFilterChange('order_by', e.target.value)}
                    className="w-full bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-blue-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 p-2 text-gray-900 dark:text-white"
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
            {/* KPIs Principais - Mobile Optimized */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }} 
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6"
            >
                {/* Total de Motoristas */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                        <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Total de Motoristas</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1 sm:mt-2 truncate">{dashboardData.total_drivers || 0}</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">{dashboardData.active_drivers || 0} ativos</p>
                        </div>
                        <div className="bg-blue-100 dark:bg-blue-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <Users className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400" />
                        </div>
                    </div>
                </motion.div>

                {/* Corridas Canceladas pelos Motoristas */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                        <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Corridas Canceladas</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-red-600 dark:text-red-400 mt-1 sm:mt-2 truncate">{dashboardData.cancelled_rides || 0}</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">Total por motoristas</p>
                        </div>
                        <div className="bg-red-100 dark:bg-red-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-red-600 dark:text-red-400" />
                        </div>
                    </div>
                </motion.div>

                {/* Média Horas por Motorista */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                        <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Média por Motorista</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-purple-600 dark:text-purple-400 mt-1 sm:mt-2 truncate">{Number(dashboardData.avg_hours_online || 0).toFixed(1)}h</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">Horas online médias</p>
                        </div>
                        <div className="bg-purple-100 dark:bg-purple-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <Activity className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600 dark:text-purple-400" />
                        </div>
                    </div>
                </motion.div>

                {/* Rating Médio dos Motoristas */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                         <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Rating Médio</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-amber-600 dark:text-amber-400 mt-1 sm:mt-2 truncate">{Number(dashboardData.avg_rating || 0).toFixed(1)}</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">Avaliação média</p>
                        </div>
                        <div className="bg-amber-100 dark:bg-amber-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <Target className="w-5 h-5 sm:w-6 sm:h-6 text-amber-600 dark:text-amber-400" />
                        </div>
                    </div>
                </motion.div>
            </motion.div>

            {/* KPIs Financeiros - Mobile Optimized */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }} 
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6"
            >
                {/* Receita Total */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                        <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Receita Total</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-emerald-600 dark:text-emerald-400 mt-1 sm:mt-2 truncate">R$ {Number(dashboardData.total_revenue || 0).toFixed(2)}</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">Últimos {dashboardData.periodo_dias} dias</p>
                        </div>
                        <div className="bg-emerald-100 dark:bg-emerald-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <DollarSign className="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600 dark:text-emerald-400" />
                        </div>
                    </div>
                </motion.div>

                {/* Taxa de Aceitação */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                        <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Taxa de Aceitação</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1 sm:mt-2 truncate">{Number(dashboardData.acceptance_rate || 0).toFixed(1)}%</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">Média geral</p>
                        </div>
                        <div className="bg-blue-100 dark:bg-blue-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400" />
                        </div>
                    </div>
                </motion.div>

                {/* Receita por Hora */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                        <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Receita por Hora</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-indigo-600 dark:text-indigo-400 mt-1 sm:mt-2 truncate">R$ {Number(dashboardData.revenue_per_hour || 0).toFixed(2)}</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">Produtividade média</p>
                        </div>
                        <div className="bg-indigo-100 dark:bg-indigo-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600 dark:text-indigo-400" />
                        </div>
                    </div>
                </motion.div>

                {/* Distância Total */}
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 hover:shadow-xl transition-all duration-300 min-h-[120px] sm:min-h-[140px]"
                >
                    <div className="flex items-center justify-between h-full">
                        <div className="flex-1 min-w-0">
                            <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium tracking-wide uppercase truncate">Distância Total</p>
                            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-teal-600 dark:text-teal-400 mt-1 sm:mt-2 truncate">{Number(dashboardData.total_distance || 0).toFixed(1)} km</p>
                            <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm mt-1 sm:mt-2 truncate">Quilometragem acumulada</p>
                        </div>
                        <div className="bg-teal-100 dark:bg-teal-900/30 p-2 sm:p-3 rounded-lg flex-shrink-0 ml-2">
                          <MapPin className="w-5 h-5 sm:w-6 sm:h-6 text-teal-600 dark:text-teal-400" />
                        </div>
                    </div>
                </motion.div>
            </motion.div>

            {/* Alertas Inteligentes */}
            {dashboardData.alerts && dashboardData.alerts.length > 0 && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
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
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
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
                    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:shadow-xl transition-all duration-300">
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
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                        <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h3 className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                                <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg">
                                    <Activity className="h-6 w-6 text-white" />
                                </div>
                                Métricas Operacionais
                            </h3>
                        </div>
                        <div className="space-y-6 p-6">
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
                        </div>
                    </motion.div>
                  </div>
                </div>
              </div>
            </motion.div>
            
            {/* Top Motoristas e Performance - Estilo Executivo */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
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
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                        <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h3 className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                                <div className="p-3 bg-gradient-to-r from-green-500 to-green-600 rounded-xl shadow-lg">
                                    <Clock className="h-6 w-6 text-white" />
                                </div>
                                Top 5 - Horas Online
                            </h3>
                        </div>
                        <div className="p-6">
                            <div className="space-y-4">
                                {topDrivers?.length > 0 ? topDrivers.map((driver, index) => (
                                    <div 
                                      key={`top-driver-${driver.unique_key || driver.driver_id || driver.name}-${index}`} 
                                      className="flex items-center justify-between p-4 bg-gradient-to-r from-white to-yellow-50 dark:from-gray-700 dark:to-yellow-900/20 rounded-xl shadow-md border border-yellow-100 dark:border-yellow-800 hover:shadow-lg transition-all duration-300 cursor-pointer"
                                      onClick={() => openModal(driver.driver_id || driver.id, driver.name || 'Motorista')}
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="relative">
                                                <img src={getAvatarUrl(driver.name || 'Motorista')} alt={driver.name || 'Motorista'} className="w-12 h-12 rounded-full shadow-lg border-2 border-yellow-200 dark:border-yellow-700"/>
                                                <div className="absolute -top-1 -right-1 bg-gradient-to-r from-yellow-400 to-yellow-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
                                                    {index + 1}
                                                </div>
                                            </div>
                                            <div>
                                                <p className="font-bold text-gray-900 dark:text-white text-lg">{(driver.name || 'Motorista').replace("Motorista ", "")}</p>
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
                        </div>
                    </motion.div>
                    
                    {/* Performance dos Motoristas */}
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                        <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h3 className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                                <div className="p-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl shadow-lg">
                                    <TrendingUp className="h-6 w-6 text-white" />
                                </div>
                                Distribuição de Performance
                            </h3>
                        </div>
                        <div className="space-y-4 p-6">
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
                        </div>
                    </motion.div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Análise Geográfica e de Veículos */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
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
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-lg shadow-lg">
                            <MapPin className="h-5 w-5 text-white" />
                          </div>
                          Top Cidades
                        </h3>
                      </div>
                      <div className="p-6">
                        <div className="space-y-4">
                          {filters.city === 'all' ? (
                            // Quando "todas as cidades" está selecionado, mostrar dados das cidades
                            citiesData && citiesData.length > 0 ? citiesData.slice(0, 5).map((city, index) => (
                              <div key={city} className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
                                <div className="flex items-center gap-3">
                                  <div className="w-8 h-8 bg-cyan-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    {index + 1}
                                  </div>
                                  <div>
                                    <p className="font-semibold text-gray-900">{city}</p>
                                    <p className="text-sm text-gray-600">Cidade disponível</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <p className="text-lg font-bold text-cyan-600">Ativa</p>
                                  <p className="text-xs text-gray-500">Operando</p>
                                </div>
                              </div>
                            )) : (
                              <div className="text-center py-4 text-gray-500">
                                <MapPin className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                <p>Carregando cidades...</p>
                              </div>
                            )
                          ) : (
                            // Quando uma cidade específica está selecionada, mostrar informações dessa cidade
                            <div className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-cyan-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                  1
                                </div>
                                <div>
                                  <p className="font-semibold text-gray-900">{filters.city}</p>
                                  <p className="text-sm text-gray-600">{kpisData?.active_drivers || 0} motoristas ativos</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="text-lg font-bold text-cyan-600">R$ {Number(kpisData?.total_revenue || 0).toFixed(2)}</p>
                                <p className="text-xs text-gray-500">{kpisData?.total_rides || 0} corridas</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>

                    {/* Análise de Veículos */}
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow-lg">
                            <Car className="h-5 w-5 text-white" />
                          </div>
                          Tipos de Veículos
                        </h3>
                      </div>
                      <div className="p-6">
                        <div className="space-y-4">
                          {Object.entries(getVehicleAnalysis())
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
                          {Object.keys(getVehicleAnalysis()).length === 0 && (
                            <div className="text-center py-4 text-gray-500">
                              <Car className="h-8 w-8 mx-auto mb-2 opacity-50" />
                              <p>Nenhum dado de veículo disponível</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>

                    {/* Métricas de Eficiência */}
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow-lg">
                            <Activity className="h-5 w-5 text-white" />
                          </div>
                          Eficiência Operacional
                        </h3>
                      </div>
                      <div className="space-y-4 p-6">
                        <div className="space-y-4">
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Taxa de Conclusão</span>
                            <span className="text-xl font-bold text-purple-600">{Number(kpisData?.completion_rate || 0).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-pink-50 to-rose-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Tempo de Resposta</span>
                            <span className="text-xl font-bold text-pink-600">{Number(kpisData?.avg_response_time || 0).toFixed(1)}s</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-rose-50 to-red-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Taxa de Cancelamento</span>
                            <span className="text-xl font-bold text-rose-600">{Number(kpisData?.cancellation_rate || 0).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Corridas Perdidas</span>
                            <span className="text-xl font-bold text-emerald-600">{kpisData?.lost_rides || 0}</span>
                          </div>
                          <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                            <span className="text-sm font-medium text-gray-700">Km por Corrida</span>
                            <span className="text-xl font-bold text-blue-600">{Number(kpisData?.km_per_ride || 0).toFixed(1)}</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Ranking e Performance - Todos os Motoristas */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-t-2xl p-6">
                  <div className="flex items-center gap-3 text-lg font-semibold">
                    <div className="bg-yellow-500/20 p-2 rounded-lg">
                      <Star className="w-5 h-5 text-yellow-400" />
                    </div>
                    Ranking e Performance - Todos os Motoristas
                  </div>
                </div>
                <div className="p-8">
                  <motion.div 
                    whileHover={{ scale: 1.02, y: -2 }}
                    className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                  >
                    <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                      <h3 className="text-xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                        <div className="p-3 bg-gradient-to-r from-gray-500 to-gray-600 rounded-xl shadow-lg">
                          <Users className="h-6 w-6 text-white" />
                        </div>
                        Lista Completa de Motoristas
                      </h3>
                    </div>
                    <div className="p-6">
                      <div className="max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                        <div className="space-y-4">
                          {aggregatedData?.drivers?.length > 0 ? aggregatedData.drivers
                            .sort((a, b) => {
                              switch (filters.order_by) {
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
                                <div 
                                  key={`all-driver-${driver.unique_key || driver.driver_id || driver.name}-${index}`} 
                                  className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all duration-300 hover:scale-[1.02] cursor-pointer"
                                  onClick={() => openModal(driver.driver_id || driver.id, driver.name || 'Motorista')}
                                >
                                  <div className="flex items-center gap-4">
                                    <div className="relative">
                                      <img src={getAvatarUrl(driver.name || 'Motorista')} alt={driver.name || 'Motorista'} className="w-12 h-12 rounded-full shadow-lg border-2 border-gray-200"/>
                                      <div className="absolute -top-1 -right-1 bg-gradient-to-r from-gray-400 to-gray-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
                                        {index + 1}
                                      </div>
                                    </div>
                                    <div>
                                      <p className="font-bold text-gray-900 dark:text-white text-lg">{(driver.name || 'Motorista').replace("Motorista ", "")}</p>
                                      <div className="flex gap-4 text-sm text-gray-700 dark:text-gray-300">
                                        <span>{onlineHours.toFixed(1)}h online</span>
                                        <span>{totalRides} corridas</span>
                                        <span>{cancelledRides} canceladas</span>
                                      </div>
                                    </div>
                                  </div>
                                  <div className="text-right">
                                    <div className="flex items-center gap-2 mb-1">
                                      <Star className="h-5 w-5 text-yellow-500 fill-current" />
                                      <span className="text-xl font-bold text-gray-900 dark:text-white">{Number(driverRating).toFixed(1)}</span>
                                    </div>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">Rating</p>
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
                              <div className="text-center py-12 text-gray-600 dark:text-gray-400">
                                <p className="text-lg font-medium">Nenhum motorista encontrado</p>
                              </div>
                            )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>

            {/* Análise Temporal Detalhada */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
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
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg shadow-lg">
                            <Clock className="h-5 w-5 text-white" />
                          </div>
                          Distribuição Temporal
                        </h3>
                      </div>
                      <div className="space-y-4 p-6">
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
                            <span className="text-xl font-bold text-cyan-600">
                              {Number(dashboardData.avg_hours_per_driver || 0).toFixed(1)}h
                              {/* DEBUG: {JSON.stringify(dashboardData.avg_hours_per_driver)} */}
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>

                    {/* Métricas de Produtividade */}
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg shadow-lg">
                            <Activity className="h-5 w-5 text-white" />
                          </div>
                          Produtividade
                        </h3>
                      </div>
                      <div className="space-y-4 p-6">
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
                      </div>
                    </motion.div>

                    {/* Insights e Recomendações */}
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-amber-500 to-amber-600 rounded-lg shadow-lg">
                            <TrendingUp className="h-5 w-5 text-white" />
                          </div>
                          Insights
                        </h3>
                      </div>
                      <div className="p-6">
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
                      </div>
                    </motion.div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Nova Seção: Análise de Produtividade */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
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
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg shadow-lg">
                            <Clock className="h-5 w-5 text-white" />
                          </div>
                          Top 5 - Mais Horas Online
                        </h3>
                      </div>
                      <div className="space-y-4 p-6">
                        {getTopDrivers('total_online_hours', 5, daysFilter).map((driver, index) => (
                          <div 
                            key={`hours-${driver.unique_key || driver.driver_id}-${index}`} 
                            className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-100 cursor-pointer hover:shadow-lg transition-all duration-300"
                            onClick={() => openModal(driver.driver_id || driver.id, driver.name || 'Motorista')}
                          >
                            <div className="flex items-center gap-3">
                              <div className="relative">
                                <img src={getAvatarUrl(driver.name || 'Motorista')} alt={driver.name || 'Motorista'} className="w-10 h-10 rounded-full border-2 border-emerald-200"/>
                                <div className="absolute -top-1 -right-1 bg-emerald-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                                  {index + 1}
                                </div>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{(driver.name || 'Motorista').replace("Motorista ", "")}</p>
                                <p className="text-sm text-gray-600">{Number(driver.data?.metrics?.total_rides || 0)} corridas</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-lg font-bold text-emerald-600">{Number(driver.data?.metrics?.online_hours || 0).toFixed(1)}h</p>
                              <p className="text-xs text-gray-500">Rating: {Number(driver.estimated_rating || 0).toFixed(1)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>

                    {/* Top 5 Motoristas por Rating */}
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-lg shadow-lg">
                            <Star className="h-5 w-5 text-white" />
                          </div>
                          Top 5 - Melhor Rating
                        </h3>
                      </div>
                      <div className="space-y-4 p-6">
                        {getTopDrivers('rating', 5, daysFilter)
                          .sort((a, b) => (b.estimated_rating || 0) - (a.estimated_rating || 0))
                          .map((driver, index) => (
                          <div 
                            key={`rating-${driver.unique_key || driver.driver_id}-${index}`} 
                            className="flex items-center justify-between p-4 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl border border-yellow-100 cursor-pointer hover:shadow-lg transition-all duration-300"
                            onClick={() => openModal(driver.driver_id || driver.id, driver.name || 'Motorista')}
                          >
                            <div className="flex items-center gap-3">
                              <div className="relative">
                                <img src={getAvatarUrl(driver.name || 'Motorista')} alt={driver.name || 'Motorista'} className="w-10 h-10 rounded-full border-2 border-yellow-200"/>
                                <div className="absolute -top-1 -right-1 bg-yellow-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                                  {index + 1}
                                </div>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{(driver.name || 'Motorista').replace("Motorista ", "")}</p>
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
                      </div>
                    </motion.div>
                    
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Análise de Tendências e Comparações Temporais */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl rounded-2xl">
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
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-violet-500 to-violet-600 rounded-lg shadow-lg">
                            <TrendingUp className="h-5 w-5 text-white" />
                          </div>
                          Tendências de Performance
                        </h3>
                      </div>
                      <div className="space-y-6 p-6">
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
                      </div>
                    </motion.div>

                    {/* Padrões Sazonais e Oportunidades */}
                    <motion.div 
                      whileHover={{ scale: 1.02, y: -2 }}
                      className="bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
                    >
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-t-xl px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-bold flex items-center gap-3 text-gray-900 dark:text-white">
                          <div className="p-2 bg-gradient-to-r from-amber-500 to-amber-600 rounded-lg shadow-lg">
                            <Calendar className="h-5 w-5 text-white" />
                          </div>
                          Padrões e Oportunidades
                        </h3>
                      </div>
                      <div className="space-y-6 p-6">
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
                      </div>
                    </motion.div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>

      {/* Modal de Detalhes do Motorista */}
      <DriverDetailsModal 
        isOpen={isModalOpen}
        onClose={closeModal}
        driverId={selectedDriverId}
        driverName={selectedDriverName}
      />
    </div>
  );
  
  } catch (componentError) {
    console.error('Erro crítico no DriversOverview:', componentError);
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <h2 className="text-lg font-semibold text-red-800 mb-2">Erro no Componente DriversOverview</h2>
        <p className="text-red-600">Ocorreu um erro ao renderizar o componente. Detalhes no console.</p>
      </div>
    );
  }
}
