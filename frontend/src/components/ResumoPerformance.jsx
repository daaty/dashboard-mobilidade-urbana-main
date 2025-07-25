import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  LineChart,
  Line,
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
  Clock, 
  DollarSign, 
  Users,
  Award,
  AlertTriangle,
  CheckCircle,
  Activity
} from 'lucide-react';

const COLORS = {
  excellent: '#10B981',
  good: '#3B82F6',
  average: '#F59E0B',
  poor: '#EF4444'
};

export function ResumoPerformance({ data, loading }) {
  const [insights, setInsights] = useState({
    performanceScore: 85,
    trends: [],
    achievements: [],
    alerts: [],
    predictions: []
  });

  useEffect(() => {
    if (data) {
      generateInsights(data);
    }
  }, [data]);

  const generateInsights = (rawData) => {
    // Simular análise de performance e insights
    const performanceData = [
      { name: 'Eficiência', value: 87, maxValue: 100 },
      { name: 'Qualidade', value: 92, maxValue: 100 },
      { name: 'Velocidade', value: 78, maxValue: 100 },
      { name: 'Satisfação', value: 94, maxValue: 100 }
    ];

    const trendsData = [
      { period: 'Jan', performance: 78 },
      { period: 'Fev', performance: 82 },
      { period: 'Mar', performance: 85 },
      { period: 'Abr', performance: 88 },
      { period: 'Mai', performance: 85 },
      { period: 'Jun', performance: 92 }
    ];

    const achievements = [
      {
        id: 1,
        title: 'Meta Superada',
        description: 'São Paulo atingiu 115% da meta mensal',
        type: 'success',
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
      },
      {
        id: 2,
        title: 'Tempo Record',
        description: 'Menor tempo médio de corrida dos últimos 6 meses',
        type: 'success',
        date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
      },
      {
        id: 3,
        title: 'Avaliação Excelente',
        description: '95% das corridas com avaliação 4+ estrelas',
        type: 'success',
        date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      }
    ];

    const alerts = [
      {
        id: 1,
        title: 'Cancelamentos Acima da Média',
        description: 'Taxa de cancelamento 12% acima do usual',
        severity: 'warning',
        action: 'Investigar Causas'
      },
      {
        id: 2,
        title: 'Horário de Pico',
        description: 'Demanda alta entre 18h-20h com poucos motoristas',
        severity: 'info',
        action: 'Incentivar Horário'
      }
    ];

    const predictions = [
      {
        metric: 'Receita Próxima Semana',
        predicted: 'R$ 45.200',
        confidence: 89,
        trend: 'up',
        change: '+8.5%'
      },
      {
        metric: 'Corridas Amanhã',
        predicted: '156 corridas',
        confidence: 92,
        trend: 'up',
        change: '+12%'
      },
      {
        metric: 'Taxa de Conversão',
        predicted: '87.2%',
        confidence: 76,
        trend: 'down',
        change: '-2.1%'
      }
    ];

    setInsights({
      performanceScore: 85,
      performanceData,
      trendsData,
      achievements,
      alerts,
      predictions
    });
  };

  const getPerformanceLevel = (score) => {
    if (score >= 90) return { level: 'Excelente', color: COLORS.excellent };
    if (score >= 75) return { level: 'Bom', color: COLORS.good };
    if (score >= 60) return { level: 'Regular', color: COLORS.average };
    return { level: 'Crítico', color: COLORS.poor };
  };

  const performance = getPerformanceLevel(insights.performanceScore);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-3">
          <Activity className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Resumo de Performance</h2>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Score Geral:</span>
          <span className={`text-lg font-bold`} style={{ color: performance.color }}>
            {insights.performanceScore}%
          </span>
          <span className={`text-sm font-medium`} style={{ color: performance.color }}>
            {performance.level}
          </span>
        </div>
      </motion.div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Performance Radial Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Indicadores de Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <RadialBarChart cx="50%" cy="50%" innerRadius="30%" outerRadius="90%" data={insights.performanceData}>
              <RadialBar
                minAngle={15}
                label={{ position: 'insideStart', fill: '#fff', fontSize: 12 }}
                background
                clockWise
                dataKey="value"
                fill="#3B82F6"
              />
              <Tooltip formatter={(value) => [`${value}%`, '']} />
            </RadialBarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Trend Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tendência de Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={insights.trendsData}>
              <XAxis dataKey="period" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip formatter={(value) => [`${value}%`, 'Performance']} />
              <Line 
                type="monotone" 
                dataKey="performance" 
                stroke="#10B981"
                strokeWidth={3}
                dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Recent Achievements */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Award className="w-5 h-5 text-yellow-500" />
            <span>Conquistas Recentes</span>
          </h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {insights.achievements?.map((achievement) => (
              <div key={achievement.id} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-900">{achievement.title}</p>
                  <p className="text-xs text-green-700 mt-1">{achievement.description}</p>
                  <p className="text-xs text-green-600 mt-2">
                    {achievement.date.toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Alerts and Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Alerts */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            <span>Alertas e Recomendações</span>
          </h3>
          <div className="space-y-3">
            {insights.alerts?.map((alert) => (
              <div 
                key={alert.id} 
                className={`p-4 rounded-lg border-l-4 ${
                  alert.severity === 'warning' 
                    ? 'bg-yellow-50 border-yellow-400' 
                    : 'bg-blue-50 border-blue-400'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${
                      alert.severity === 'warning' ? 'text-yellow-900' : 'text-blue-900'
                    }`}>
                      {alert.title}
                    </p>
                    <p className={`text-xs mt-1 ${
                      alert.severity === 'warning' ? 'text-yellow-700' : 'text-blue-700'
                    }`}>
                      {alert.description}
                    </p>
                  </div>
                  <button className={`text-xs font-medium px-2 py-1 rounded ${
                    alert.severity === 'warning' 
                      ? 'bg-yellow-200 text-yellow-800 hover:bg-yellow-300' 
                      : 'bg-blue-200 text-blue-800 hover:bg-blue-300'
                  }`}>
                    {alert.action}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Predictions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Target className="w-5 h-5 text-purple-500" />
            <span>Predições</span>
          </h3>
          <div className="space-y-4">
            {insights.predictions?.map((prediction, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-sm font-medium text-gray-900">{prediction.metric}</p>
                  <div className="flex items-center space-x-1">
                    {prediction.trend === 'up' ? (
                      <TrendingUp className="w-4 h-4 text-green-600" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-600" />
                    )}
                    <span className={`text-sm font-medium ${
                      prediction.trend === 'up' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {prediction.change}
                    </span>
                  </div>
                </div>
                <p className="text-lg font-bold text-gray-900 mb-1">{prediction.predicted}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    Confiança: {prediction.confidence}%
                  </span>
                  <div className="w-20 bg-gray-200 rounded-full h-1.5">
                    <div 
                      className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                      style={{ width: `${prediction.confidence}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white"
      >
        <h3 className="text-lg font-semibold mb-4">Ações Recomendadas</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all">
            <Users className="w-6 h-6 mb-2" />
            <p className="font-medium">Motivar Motoristas</p>
            <p className="text-sm opacity-90">Criar campanha de incentivos</p>
          </button>
          
          <button className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all">
            <Target className="w-6 h-6 mb-2" />
            <p className="font-medium">Ajustar Metas</p>
            <p className="text-sm opacity-90">Revisar metas mensais</p>
          </button>
          
          <button className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all">
            <DollarSign className="w-6 h-6 mb-2" />
            <p className="font-medium">Otimizar Preços</p>
            <p className="text-sm opacity-90">Análise de precificação dinâmica</p>
          </button>
        </div>
      </motion.div>
    </div>
  );
}
