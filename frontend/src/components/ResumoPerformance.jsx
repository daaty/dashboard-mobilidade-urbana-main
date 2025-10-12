import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  LineChart,
  Line,
  AreaChart,
  Area,
  CartesianGrid,
  Legend,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  RefreshCw,
  DollarSign, 
  Users,
  Award,
  Activity,
  Zap,
  Star,
  PieChart as PieChartIcon
} from 'lucide-react';
import { usePerformanceData } from '../hooks/usePerformanceData';
import { PerformanceFilter } from './PerformanceFilter';
import { PerformanceCard } from './PerformanceCard';
import { PerformanceAlert } from './PerformanceAlert';
import { PerformancePrediction } from './PerformancePrediction';

const COLORS = {
  excellent: '#10B981',
  good: '#3B82F6',
  average: '#F59E0B',
  poor: '#EF4444'
};

export function ResumoPerformance() {
  const [period, setPeriod] = useState('7_days');
  const { data: performanceData, loading, error, refetch } = usePerformanceData(period);

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
  };

  const handleAlertAction = (alert) => {
    console.log('Ação do alerta:', alert);
    // TODO: Implementar ações específicas por tipo de alerta
  };


  const getPerformanceLevel = (score) => {
    if (score >= 90) return { level: 'Excelente', color: COLORS.excellent };
    if (score >= 75) return { level: 'Bom', color: COLORS.good };
    if (score >= 60) return { level: 'Regular', color: COLORS.average };
    return { level: 'Crítico', color: COLORS.poor };
  };

  // Preparar dados para os gráficos
  const performanceChartData = performanceData?.overview ? [
    { 
      name: 'Eficiência', 
      value: performanceData.overview.efficiency_score || 0, 
      maxValue: 100,
      fill: COLORS.good
    },
    { 
      name: 'Qualidade', 
      value: performanceData.overview.quality_score || 0, 
      maxValue: 100,
      fill: COLORS.excellent
    },
    { 
      name: 'Velocidade', 
      value: performanceData.overview.speed_score || 0, 
      maxValue: 100,
      fill: COLORS.average
    },
    { 
      name: 'Satisfação', 
      value: (performanceData.overview.satisfaction_score || 0) * 20, 
      maxValue: 100,
      fill: '#8B5CF6'
    }
  ] : [];

  const performance = getPerformanceLevel(performanceData?.overview?.performance_score || 0);

  // Loading state
  if (loading) {
    return (
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-64"></div>
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
        </div>

        {/* KPIs Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            </div>
          ))}
        </div>

        {/* Charts Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
              <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Activity className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Erro ao Carregar Dados de Performance
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center space-x-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Tentar Novamente</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header com Filtro e Refresh */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div className="flex items-center space-x-3">
          <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Resumo de Performance</h2>
        </div>

        <div className="flex items-center space-x-4">
          <PerformanceFilter period={period} onPeriodChange={handlePeriodChange} loading={loading} />
          
          <button
            onClick={refetch}
            disabled={loading}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 
                       text-white rounded-lg transition-colors duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed"
            title="Atualizar dados"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Atualizar</span>
          </button>
        </div>
      </motion.div>

      {/* Score Geral */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90 mb-1">Score Geral de Performance</p>
            <p className="text-4xl font-bold">{performanceData?.overview?.performance_score || 0}%</p>
            <p className="text-sm opacity-90 mt-1">{performance.level}</p>
          </div>
          <div className="bg-white/20 p-4 rounded-lg">
            <Award className="w-12 h-12" />
          </div>
        </div>
      </motion.div>

      {/* KPIs Principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <PerformanceCard
          title="Motoristas Ativos"
          value={performanceData?.overview?.active_drivers || 0}
          subtitle={`de ${performanceData?.overview?.total_drivers || 0} total`}
          icon={Users}
          color="blue"
          delay={0}
        />
        <PerformanceCard
          title="Taxa de Eficiência"
          value={`${performanceData?.overview?.efficiency_score || 0}%`}
          subtitle="Taxa de conclusão"
          icon={Zap}
          color="green"
          delay={0.1}
        />
        <PerformanceCard
          title="Qualidade Média"
          value={`${performanceData?.overview?.quality_score || 0}%`}
          subtitle="Avaliações"
          icon={Star}
          color="yellow"
          delay={0.2}
        />
        <PerformanceCard
          title="Satisfação"
          value={`⭐ ${performanceData?.overview?.satisfaction_score?.toFixed(2) || '0.00'}`}
          subtitle="Rating médio"
          icon={Target}
          color="purple"
          delay={0.3}
        />
      </div>

      {/* Performance Overview - Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Performance Radial Chart - MELHORADO COM TOOLTIPS DETALHADOS */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <span>Indicadores de Performance</span>
          </h3>
          <ResponsiveContainer width="100%" height={560}>
            <RadialBarChart 
              cx="50%" 
              cy="50%" 
              innerRadius="20%" 
              outerRadius="100%" 
              data={performanceChartData}
              startAngle={90}
              endAngle={-270}
            >
              <RadialBar
                minAngle={15}
                label={{ 
                  position: 'insideStart', 
                  fill: '#fff', 
                  fontSize: 14,
                  fontWeight: 'bold',
                  formatter: (value) => `${value}%`
                }}
                background={{ fill: '#f3f4f6' }}
                clockWise
                dataKey="value"
                cornerRadius={10}
              />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    const descriptions = {
                      'Eficiência': 'Taxa de conclusão de corridas sem cancelamentos',
                      'Qualidade': 'Média ponderada das avaliações dos motoristas',
                      'Velocidade': 'Tempo médio de resposta e conclusão de corridas',
                      'Satisfação': 'Rating médio (0-5 estrelas) convertido para escala de 100'
                    };
                    
                    return (
                      <div className="bg-gray-900 text-white p-3 rounded-lg shadow-lg border border-gray-700 max-w-xs">
                        <p className="font-semibold text-sm mb-1">{data.name}</p>
                        <p className="text-2xl font-bold mb-2" style={{ color: data.fill }}>
                          {data.name === 'Satisfação' 
                            ? `⭐ ${(data.value / 20).toFixed(2)}/5.00` 
                            : `${data.value}%`
                          }
                        </p>
                        <p className="text-xs text-gray-300 leading-relaxed">
                          {descriptions[data.name]}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </RadialBarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Trend Analysis - MELHORADO com Área e Múltiplas Linhas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <span>Evolução de Performance</span>
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={performanceData?.trends || []}>
              <defs>
                <linearGradient id="performanceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="efficiencyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} stroke="#E5E7EB" />
              <XAxis 
                dataKey="period" 
                fontSize={12}
                stroke="#9CA3AF"
                tickLine={false}
              />
              <YAxis 
                fontSize={12}
                stroke="#9CA3AF"
                tickLine={false}
                domain={[0, 100]}
              />
              <Tooltip 
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const metricDescriptions = {
                      'Performance': 'Score geral calculado com base em eficiência e qualidade',
                      'Eficiência': 'Percentual de corridas concluídas com sucesso',
                      'Satisfação': 'Avaliação média dos passageiros (escala de 0 a 5)'
                    };
                    
                    return (
                      <div className="bg-gray-900 text-white p-4 rounded-lg shadow-xl border border-gray-700 min-w-[250px]">
                        <p className="font-bold text-base mb-3 border-b border-gray-700 pb-2">
                          {label}
                        </p>
                        {payload.map((entry, index) => (
                          <div key={index} className="mb-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="flex items-center gap-2 text-sm">
                                <span 
                                  className="w-3 h-3 rounded-full" 
                                  style={{ backgroundColor: entry.color }}
                                ></span>
                                {entry.name}
                              </span>
                              <span className="font-bold text-lg" style={{ color: entry.color }}>
                                {entry.name === 'Satisfação' 
                                  ? `⭐ ${entry.value}` 
                                  : `${entry.value}%`
                                }
                              </span>
                            </div>
                            <p className="text-xs text-gray-400 ml-5">
                              {metricDescriptions[entry.name]}
                            </p>
                          </div>
                        ))}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '10px' }}
                iconType="circle"
              />
              <Area
                type="monotone"
                dataKey="performance"
                stroke="#10B981"
                strokeWidth={3}
                fill="url(#performanceGradient)"
                name="Performance"
                dot={{ fill: '#10B981', strokeWidth: 2, r: 5 }}
                activeDot={{ r: 7 }}
              />
              <Area
                type="monotone"
                dataKey="efficiency"
                stroke="#3B82F6"
                strokeWidth={2}
                fill="url(#efficiencyGradient)"
                name="Eficiência"
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Distribuição de Performance - NOVO GRÁFICO DE PIZZA */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <PieChartIcon className="w-5 h-5 text-purple-600" />
            <span>Distribuição de Motoristas</span>
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={[
                  { 
                    name: 'Excelente', 
                    value: performanceData?.overview?.performance_distribution?.excellent || 0,
                    color: '#10B981'
                  },
                  { 
                    name: 'Bom', 
                    value: performanceData?.overview?.performance_distribution?.good || 0,
                    color: '#3B82F6'
                  },
                  { 
                    name: 'Médio', 
                    value: performanceData?.overview?.performance_distribution?.average || 0,
                    color: '#F59E0B'
                  },
                  { 
                    name: 'Baixo', 
                    value: performanceData?.overview?.performance_distribution?.poor || 0,
                    color: '#EF4444'
                  }
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => 
                  percent > 0 ? `${name} ${(percent * 100).toFixed(0)}%` : null
                }
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"
              >
                {[
                  { 
                    name: 'Excelente', 
                    value: performanceData?.overview?.performance_distribution?.excellent || 0,
                    color: '#10B981'
                  },
                  { 
                    name: 'Bom', 
                    value: performanceData?.overview?.performance_distribution?.good || 0,
                    color: '#3B82F6'
                  },
                  { 
                    name: 'Médio', 
                    value: performanceData?.overview?.performance_distribution?.average || 0,
                    color: '#F59E0B'
                  },
                  { 
                    name: 'Baixo', 
                    value: performanceData?.overview?.performance_distribution?.poor || 0,
                    color: '#EF4444'
                  }
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0];
                    const categoryDescriptions = {
                      'Excelente': 'Motoristas com avaliação ≥ 4.5 estrelas - Excedem expectativas',
                      'Bom': 'Motoristas com avaliação entre 4.0 e 4.4 estrelas - Atendem expectativas',
                      'Médio': 'Motoristas com avaliação entre 3.5 e 3.9 estrelas - Necessitam melhorias',
                      'Baixo': 'Motoristas com avaliação < 3.5 estrelas - Atenção requerida'
                    };
                    
                    const total = performanceData?.overview?.total_drivers || 0;
                    const percentage = total > 0 ? ((data.value / total) * 100).toFixed(1) : 0;
                    
                    return (
                      <div className="bg-gray-900 text-white p-4 rounded-lg shadow-xl border border-gray-700 min-w-[280px]">
                        <div className="flex items-center gap-2 mb-2">
                          <span 
                            className="w-4 h-4 rounded-full" 
                            style={{ backgroundColor: data.payload.color }}
                          ></span>
                          <p className="font-bold text-base">{data.name}</p>
                        </div>
                        <p className="text-3xl font-bold mb-2" style={{ color: data.payload.color }}>
                          {data.value} motoristas
                        </p>
                        <p className="text-sm text-gray-400 mb-2">
                          {percentage}% do total ({total} motoristas)
                        </p>
                        <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
                          <div 
                            className="h-2 rounded-full" 
                            style={{ 
                              width: `${percentage}%`,
                              backgroundColor: data.payload.color 
                            }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-300 leading-relaxed">
                          {categoryDescriptions[data.name]}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend 
                verticalAlign="bottom"
                height={36}
                iconType="circle"
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Conquistas Recentes - Movido para baixo dos gráficos */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Award className="w-5 h-5 text-yellow-500" />
            <span>Conquistas Recentes</span>
          </h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {(performanceData?.achievements || []).map((achievement) => (
              <div key={achievement.id} className="flex items-start space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <Award className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-900 dark:text-green-100">{achievement.title}</p>
                  <p className="text-xs text-green-700 dark:text-green-300 mt-1">{achievement.description}</p>
                  <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                    {new Date(achievement.date).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>
            ))}
            {(!performanceData?.achievements || performanceData.achievements.length === 0) && (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                Nenhuma conquista registrada no período
              </p>
            )}
          </div>
        </motion.div>

      {/* Alerts and Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Alerts */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Activity className="w-5 h-5 text-orange-500" />
            <span>Alertas e Recomendações</span>
          </h3>
          <div className="space-y-3">
            {(performanceData?.alerts || []).map((alert) => (
              <PerformanceAlert key={alert.id} alert={alert} onAction={handleAlertAction} />
            ))}
            {(!performanceData?.alerts || performanceData.alerts.length === 0) && (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                Nenhum alerta no momento
              </p>
            )}
          </div>
        </motion.div>

        {/* Predictions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Target className="w-5 h-5 text-purple-500" />
            <span>Previsões</span>
          </h3>
          <div className="space-y-4">
            {(performanceData?.predictions || []).map((prediction, index) => (
              <PerformancePrediction key={index} prediction={prediction} delay={0.1 * index} />
            ))}
            {(!performanceData?.predictions || performanceData.predictions.length === 0) && (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                Nenhuma previsão disponível
              </p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Top Performers Table */}
      {performanceData?.detailedMetrics && performanceData.detailedMetrics.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Award className="w-5 h-5 text-yellow-500" />
            <span>🏆 Top 10 Performers</span>
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b dark:border-gray-700">
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-700 dark:text-gray-300">#</th>
                  <th className="text-left py-3 px-2 text-sm font-medium text-gray-700 dark:text-gray-300">Motorista</th>
                  <th className="text-center py-3 px-2 text-sm font-medium text-gray-700 dark:text-gray-300">Corridas</th>
                  <th className="text-center py-3 px-2 text-sm font-medium text-gray-700 dark:text-gray-300">Conclusão</th>
                  <th className="text-center py-3 px-2 text-sm font-medium text-gray-700 dark:text-gray-300">Rating</th>
                  <th className="text-center py-3 px-2 text-sm font-medium text-gray-700 dark:text-gray-300">Categoria</th>
                </tr>
              </thead>
              <tbody>
                {performanceData.detailedMetrics.slice(0, 10).map((driver, idx) => {
                  const getCategoryBadge = (category) => {
                    const badges = {
                      excellent: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-800 dark:text-green-200', label: 'Excelente' },
                      good: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-800 dark:text-blue-200', label: 'Bom' },
                      average: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-800 dark:text-yellow-200', label: 'Regular' },
                      poor: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-200', label: 'Crítico' }
                    };
                    return badges[category] || badges.average;
                  };

                  const badge = getCategoryBadge(driver.performance_category);

                  return (
                    <tr key={`performer-${idx}-${driver.driver_id}`} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="py-3 px-2 text-sm font-medium text-gray-900 dark:text-white">{idx + 1}</td>
                      <td className="py-3 px-2 text-sm font-medium text-gray-900 dark:text-white">{driver.name}</td>
                      <td className="py-3 px-2 text-center text-sm text-gray-700 dark:text-gray-300">{driver.total_rides}</td>
                      <td className="py-3 px-2 text-center text-sm text-gray-700 dark:text-gray-300">{driver.completion_rate}%</td>
                      <td className="py-3 px-2 text-center text-sm text-gray-700 dark:text-gray-300">
                        ⭐ {driver.rating.toFixed(1)}
                      </td>
                      <td className="py-3 px-2 text-center">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
                          {badge.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white"
      >
        <h3 className="text-lg font-semibold mb-4">Ações Recomendadas</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-white/20 hover:bg-white/30 rounded-lg p-4 text-left transition-all">
            <Users className="w-6 h-6 mb-2" />
            <p className="font-medium">Motivar Motoristas</p>
            <p className="text-sm opacity-90">Criar campanha de incentivos</p>
          </button>
          
          <button className="bg-white/20 hover:bg-white/30 rounded-lg p-4 text-left transition-all">
            <Target className="w-6 h-6 mb-2" />
            <p className="font-medium">Ajustar Metas</p>
            <p className="text-sm opacity-90">Revisar metas mensais</p>
          </button>
          
          <button className="bg-white/20 hover:bg-white/30 rounded-lg p-4 text-left transition-all">
            <DollarSign className="w-6 h-6 mb-2" />
            <p className="font-medium">Otimizar Preços</p>
            <p className="text-sm opacity-90">Análise de precificação dinâmica</p>
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default ResumoPerformance;
