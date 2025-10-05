import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line
} from 'recharts';
import {
  MapPin,
  TrendingUp,
  Star,
  Clock,
  Users,
  Activity,
  Calendar,
  AlertCircle,
  Award,
  Loader2
} from 'lucide-react';

const COLORS = {
  primary: '#3B82F6',
  secondary: '#8B5CF6',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#06B6D4',
  purple: '#A855F7',
  pink: '#EC4899'
};

const CHART_COLORS = [
  COLORS.primary,
  COLORS.secondary,
  COLORS.success,
  COLORS.warning,
  COLORS.danger,
  COLORS.info,
  COLORS.purple,
  COLORS.pink
];

export default function DriversAnalytics({ period = '6_months', activeDriversCount = 0, totalDriversCount = 0 }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    byCity: [],
    topPerformers: [],
    ratingsDistribution: [],
    recentEnrollments: [],
    performanceMetrics: null,
    onlineActivity: null,
    activityComparison: [],
    activeDriversCount: activeDriversCount  // Total de motoristas ATIVOS (status != unknown) vindo como prop
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchAllData();
  }, [period]);

  // Atualizar activeDriversCount quando a prop mudar
  useEffect(() => {
    console.log('🔍 activeDriversCount recebido como prop:', activeDriversCount);
    setData(prev => ({ ...prev, activeDriversCount }));
  }, [activeDriversCount]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      const [
        byCityRes,
        topPerformersRes,
        ratingsRes,
        enrollmentsRes,
        performanceRes,
        activityRes,
        comparisonRes,
        cityGrowthRes,
        inactiveByCityRes
      ] = await Promise.all([
        fetch(`${API_URL}/api/drivers/analytics/by-city?period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/top-performers?limit=10&period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/ratings-distribution?period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/recent-enrollments?period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/performance-metrics?period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/online-activity?period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/activity-comparison?limit=15&period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/city-growth?period=${period}`),
        fetch(`${API_URL}/api/drivers/analytics/inactive-by-city?period=${period}`)
      ]);

      const [byCity, topPerformers, ratings, enrollments, performance, activity, comparison, cityGrowth, inactiveByCity] = await Promise.all([
        byCityRes.json(),
        topPerformersRes.json(),
        ratingsRes.json(),
        enrollmentsRes.json(),
        performanceRes.json(),
        activityRes.json(),
        comparisonRes.json(),
        cityGrowthRes.json(),
        inactiveByCityRes.json()
      ]);

      setData({
        byCity: byCity.data || [],
        topPerformers: topPerformers.data || [],
        ratingsDistribution: ratings.data || [],
        ratingsSummary: ratings.summary || {},
        recentEnrollments: enrollments.data || {},
        performanceMetrics: performance.data || null,
        onlineActivity: activity.data || null,
        activityComparison: comparison.data || [],
        cityGrowth: cityGrowth.data || [],
        inactiveByCity: inactiveByCity.data || [],
        activeDriversCount: activeDriversCount  // ← Recebido como prop do DriversOverview
      });

    } catch (error) {
      console.error('Erro ao buscar dados de analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 text-white p-3 rounded-lg shadow-xl border border-gray-700">
          <p className="text-sm font-semibold">{payload[0].name}</p>
          <p className="text-sm text-blue-400">
            {payload[0].value} {payload[0].unit || ''}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600 dark:text-gray-400">Carregando analytics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-3"
      >
        <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Analytics de Motoristas
        </h2>
      </motion.div>

      {/* Grid de Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* 1. Distribuição por Cidade */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-blue-600" />
              <span>Motoristas por Cidade</span>
            </h3>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {data.byCity.length} cidades
            </span>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.byCity}
                dataKey="total"
                nameKey="cidade"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ cidade, total }) => `${cidade}: ${total}`}
                labelLine={false}
              >
                {data.byCity.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* 2. Top 10 Performers */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
              <Award className="w-5 h-5 text-yellow-600" />
              <span>Top 10 Motoristas (Success Rides)</span>
            </h3>
          </div>
          
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={data.topPerformers}
              margin={{ top: 20, right: 30, left: 20, bottom: 100 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="name" 
                stroke="#6B7280" 
                fontSize={10}
                angle={-45}
                textAnchor="end"
                height={100}
                interval={0}
                tick={({ x, y, payload }) => {
                  const name = payload.value;
                  const displayName = name.length > 15 ? name.substring(0, 15) + '...' : name;
                  return (
                    <g transform={`translate(${x},${y})`}>
                      <text 
                        x={0} 
                        y={0} 
                        dy={16} 
                        textAnchor="end" 
                        fill="#6B7280" 
                        fontSize={10}
                        transform="rotate(-45)"
                      >
                        {displayName}
                      </text>
                    </g>
                  );
                }}
              />
              <YAxis 
                stroke="#6B7280" 
                fontSize={12}
                domain={[0, 'dataMax + 2']}
                allowDecimals={false}
              />
              <Tooltip 
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const item = data.topPerformers.find(d => d.name === label);
                    return (
                      <div style={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        padding: '12px',
                        color: '#fff'
                      }}>
                        <div style={{ fontWeight: 600, marginBottom: '8px' }}>{item?.name || label}</div>
                        <div style={{ marginBottom: '4px' }}>
                          <span style={{ color: '#10B981' }}>Corridas Concluídas: </span>
                          <span style={{ fontWeight: 600 }}>{payload[0].value}</span>
                        </div>
                        {item && (
                          <div style={{ fontSize: '12px', color: '#9CA3AF', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #374151' }}>
                            <div>Horas Online: {item.online_hours}h</div>
                            <div>Rejeitadas: {item.rejected_rides}</div>
                            <div>Perdidas: {item.missed_rides}</div>
                          </div>
                        )}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar 
                dataKey="success_rides" 
                fill={COLORS.success} 
                radius={[4, 4, 0, 0]}
                minPointSize={5}
                label={{ 
                  position: 'top', 
                  fill: '#6B7280',
                  fontSize: 11,
                  formatter: (value) => value > 0 ? value : ''
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* 3. Distribuição de Avaliações */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
              <Star className="w-5 h-5 text-yellow-500" />
              <span>Distribuição de Avaliações</span>
            </h3>
            <div className="text-right">
              <div className="text-2xl font-bold text-yellow-600">
                {data.ratingsSummary?.media_geral || 0}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Média Geral
              </div>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.ratingsDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="faixa" stroke="#6B7280" fontSize={12} />
              <YAxis stroke="#6B7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="quantidade" fill={COLORS.warning} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* 4. Comparativo 7d vs 30d */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <span>Atividade: 7d vs 30d</span>
            </h3>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={data.activityComparison.slice(0, 10)}
              margin={{ top: 5, right: 20, left: 5, bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="name" 
                stroke="#6B7280" 
                fontSize={10}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis stroke="#6B7280" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="rides_7d" fill={COLORS.info} name="Últimos 7 dias" radius={[4, 4, 0, 0]} />
              <Bar dataKey="rides_30d" fill={COLORS.primary} name="Últimos 30 dias" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* 5. Métricas de Performance */}
        {data.performanceMetrics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 lg:col-span-2"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
                <Activity className="w-5 h-5 text-purple-600" />
                <span>Métricas de Performance Agregadas</span>
              </h3>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {data.performanceMetrics.summary.active_drivers_period} motoristas ativos
              </div>
            </div>
            
            {/* Grid Principal de Métricas */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-green-50 to-emerald-100 dark:bg-green-900/20 rounded-lg p-4 border border-green-200">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total de Corridas</div>
                <div className="text-2xl font-bold text-green-600">
                  {data.performanceMetrics.summary.total_rides}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {(data.performanceMetrics.summary.total_rides / data.performanceMetrics.summary.total_drivers).toFixed(1)} por motorista
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-blue-50 to-cyan-100 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Receita Total</div>
                <div className="text-2xl font-bold text-blue-600">
                  R$ {data.performanceMetrics.summary.total_revenue.toFixed(2)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  R$ {(data.performanceMetrics.summary.total_revenue / data.performanceMetrics.summary.total_drivers).toFixed(2)} por motorista
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-purple-50 to-violet-100 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Ticket Médio</div>
                <div className="text-2xl font-bold text-purple-600">
                  R$ {data.performanceMetrics.summary.avg_ticket.toFixed(2)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  por corrida
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-orange-50 to-amber-100 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Distância Total</div>
                <div className="text-2xl font-bold text-orange-600">
                  {data.performanceMetrics.summary.total_distance_km.toFixed(1)} km
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {data.performanceMetrics.summary.avg_distance_km.toFixed(2)} km/corrida
                </div>
              </div>
            </div>

            {/* Métricas Secundárias */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Duração Média</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {data.performanceMetrics.summary.avg_duration_minutes.toFixed(1)} min
                </div>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Tempo Total em Corrida</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {data.performanceMetrics.summary.total_duration_hours.toFixed(1)}h
                </div>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Motoristas Ativos</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {data.activeDriversCount}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Status: Active/Online/Offline
                </div>
              </div>
            </div>

            {/* Gráficos de Distribuição */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              {/* Distribuição de Corridas por Motorista */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Distribuição de Corridas por Motorista
                </h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={data.performanceMetrics.rides_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis 
                      dataKey="faixa" 
                      stroke="#6B7280" 
                      fontSize={10}
                      angle={-15}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                    />
                    <Bar dataKey="quantidade" fill={COLORS.purple} radius={[4, 4, 0, 0]} name="Motoristas" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Distribuição por Período do Dia */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Corridas por Período do Dia
                </h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={data.performanceMetrics.period_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis 
                      dataKey="periodo" 
                      stroke="#6B7280" 
                      fontSize={12}
                    />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#fff'
                      }}
                    />
                    <Bar dataKey="quantidade" fill={COLORS.warning} radius={[4, 4, 0, 0]} name="Corridas" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </motion.div>
        )}

        {/* 6. Crescimento de Motoristas por Cidade */}
        {data.cityGrowth && data.cityGrowth.length > 0 && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 col-span-2"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <span>Crescimento de Motoristas por Cidade</span>
              </h3>
              <div className="text-right">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Comparativo: Cadastrados vs Ativos
                </div>
              </div>
            </div>
            
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={data.cityGrowth.slice(0, 10)}
                margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                <XAxis 
                  dataKey="cidade" 
                  stroke="#6B7280" 
                  fontSize={11}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  interval={0}
                />
                <YAxis 
                  stroke="#6B7280" 
                  fontSize={12}
                  label={{ value: 'Quantidade de Motoristas', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const item = data.cityGrowth.find(d => d.cidade === label);
                      return (
                        <div style={{
                          backgroundColor: '#1F2937',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          padding: '12px',
                          color: '#fff'
                        }}>
                          <div style={{ fontWeight: 600, marginBottom: '8px', fontSize: '14px' }}>{label}</div>
                          <div style={{ marginBottom: '4px', fontSize: '13px' }}>
                            <span style={{ color: '#60A5FA' }}>Total Cadastrados: </span>
                            <span style={{ fontWeight: 600 }}>{item?.total_cadastrados || 0}</span>
                          </div>
                          <div style={{ marginBottom: '4px', fontSize: '13px' }}>
                            <span style={{ color: '#34D399' }}>Motoristas Ativos: </span>
                            <span style={{ fontWeight: 600 }}>{item?.total_ativos || 0}</span>
                          </div>
                          <div style={{ marginBottom: '4px', fontSize: '13px' }}>
                            <span style={{ color: '#FBBF24' }}>Novos no Período: </span>
                            <span style={{ fontWeight: 600 }}>{item?.novos_cadastrados || 0}</span>
                          </div>
                          {item && (
                            <div style={{ fontSize: '12px', color: '#9CA3AF', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #374151' }}>
                              <div>Taxa de Ativação: {item.taxa_ativacao}%</div>
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend 
                  wrapperStyle={{ paddingTop: '20px' }}
                  iconType="rect"
                />
                <Bar 
                  dataKey="total_cadastrados" 
                  fill="#60A5FA" 
                  name="Total Cadastrados"
                  radius={[4, 4, 0, 0]}
                  label={{ 
                    position: 'top', 
                    fill: '#6B7280',
                    fontSize: 10,
                    formatter: (value) => value > 0 ? value : ''
                  }}
                />
                <Bar 
                  dataKey="total_ativos" 
                  fill="#34D399" 
                  name="Motoristas Ativos"
                  radius={[4, 4, 0, 0]}
                  label={{ 
                    position: 'top', 
                    fill: '#6B7280',
                    fontSize: 10,
                    formatter: (value) => value > 0 ? value : ''
                  }}
                />
                <Bar 
                  dataKey="novos_cadastrados" 
                  fill="#FBBF24" 
                  name="Novos no Período"
                  radius={[4, 4, 0, 0]}
                  label={{ 
                    position: 'top', 
                    fill: '#6B7280',
                    fontSize: 10,
                    formatter: (value) => value > 0 ? value : ''
                  }}
                />
              </BarChart>
            </ResponsiveContainer>
            
            {/* Legenda adicional com insights */}
            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
              <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {data.cityGrowth.reduce((sum, city) => sum + city.total_cadastrados, 0)}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Total Cadastrados</div>
              </div>
              <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {data.cityGrowth.reduce((sum, city) => sum + city.total_ativos, 0)}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Motoristas Ativos</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {data.cityGrowth.reduce((sum, city) => sum + city.novos_cadastrados, 0)}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Novos no Período</div>
              </div>
            </div>
          </motion.div>
        )}

        {/* 7. Motoristas Inativos por Cidade (Alerta) */}
        {data.inactiveByCity && data.inactiveByCity.length > 0 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-red-200 dark:border-red-700 p-6 col-span-2"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span>Motoristas Inativos por Cidade</span>
              </h3>
              <div className="text-right">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Motoristas cadastrados sem corridas
                </div>
              </div>
            </div>
            
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={data.inactiveByCity.slice(0, 10)}
                margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                <XAxis 
                  dataKey="cidade" 
                  stroke="#6B7280" 
                  fontSize={11}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  interval={0}
                />
                <YAxis 
                  stroke="#6B7280" 
                  fontSize={12}
                  label={{ value: 'Quantidade de Motoristas', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const item = data.inactiveByCity.find(d => d.cidade === label);
                      return (
                        <div style={{
                          backgroundColor: '#1F2937',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          padding: '12px',
                          color: '#fff'
                        }}>
                          <div style={{ fontWeight: 600, marginBottom: '8px', fontSize: '14px' }}>{label}</div>
                          <div style={{ marginBottom: '4px', fontSize: '13px' }}>
                            <span style={{ color: '#EF4444' }}>Total Inativos: </span>
                            <span style={{ fontWeight: 600 }}>{item?.total_inativos || 0}</span>
                          </div>
                          <div style={{ marginBottom: '4px', fontSize: '13px' }}>
                            <span style={{ color: '#F87171' }}>Novos Inativos no Período: </span>
                            <span style={{ fontWeight: 600 }}>{item?.novos_inativos || 0}</span>
                          </div>
                          <div style={{ marginBottom: '4px', fontSize: '13px' }}>
                            <span style={{ color: '#34D399' }}>Motoristas Ativos: </span>
                            <span style={{ fontWeight: 600 }}>{item?.total_ativos || 0}</span>
                          </div>
                          {item && (
                            <div style={{ fontSize: '12px', color: '#9CA3AF', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #374151' }}>
                              <div>Total Cadastrados: {item.total_cadastrados}</div>
                              <div>Taxa de Inatividade: {item.taxa_inatividade}%</div>
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend 
                  wrapperStyle={{ paddingTop: '20px' }}
                  iconType="rect"
                />
                <Bar 
                  dataKey="total_inativos" 
                  fill="#EF4444" 
                  name="Total Inativos"
                  radius={[4, 4, 0, 0]}
                  label={{ 
                    position: 'top', 
                    fill: '#6B7280',
                    fontSize: 10,
                    formatter: (value) => value > 0 ? value : ''
                  }}
                />
                <Bar 
                  dataKey="novos_inativos" 
                  fill="#F87171" 
                  name="Novos Inativos no Período"
                  radius={[4, 4, 0, 0]}
                  label={{ 
                    position: 'top', 
                    fill: '#6B7280',
                    fontSize: 10,
                    formatter: (value) => value > 0 ? value : ''
                  }}
                />
                <Bar 
                  dataKey="total_ativos" 
                  fill="#34D399" 
                  name="Ativos (Referência)"
                  radius={[4, 4, 0, 0]}
                  label={{ 
                    position: 'top', 
                    fill: '#6B7280',
                    fontSize: 10,
                    formatter: (value) => value > 0 ? value : ''
                  }}
                />
              </BarChart>
            </ResponsiveContainer>
            
            {/* Cards de Alerta */}
            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
              <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-700">
                <div className="text-2xl font-bold text-red-600">
                  {data.inactiveByCity.reduce((sum, city) => sum + city.total_inativos, 0)}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Total Inativos</div>
              </div>
              <div className="text-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-700">
                <div className="text-2xl font-bold text-orange-600">
                  {data.inactiveByCity.reduce((sum, city) => sum + city.novos_inativos, 0)}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Novos Inativos</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-700">
                <div className="text-2xl font-bold text-yellow-600">
                  {Math.round(
                    data.inactiveByCity.reduce((sum, city) => sum + city.taxa_inatividade, 0) / 
                    data.inactiveByCity.length
                  )}%
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Taxa Média de Inatividade</div>
              </div>
            </div>
          </motion.div>
        )}

      </div>
    </div>
  );
}
