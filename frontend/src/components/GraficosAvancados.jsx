import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  RadialBarChart,
  RadialBar
} from 'recharts';
import { TrendingUp, Target, MapPin, Clock, DollarSign } from 'lucide-react';

const COLORS = {
  primary: '#3B82F6',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#6366F1',
  purple: '#8B5CF6'
};

const CHART_COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
  '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
];

export function GraficosAvancados({ data, loading }) {
  const [chartData, setChartData] = useState({
    corridas_diarias: [],
    receita_mensal: [],
    performance_motoristas: [],
    distribuicao_cidades: [],
    horarios_pico: []
  });

  useEffect(() => {
    if (data) {
      // Processar dados para gráficos
      processChartData(data);
    }
  }, [data]);

  const processChartData = (rawData) => {
    // Dados de corridas diárias dos últimos 7 dias
    const corridasDiarias = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      corridasDiarias.push({
        data: date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
        concluidas: Math.floor(Math.random() * 50) + 20,
        canceladas: Math.floor(Math.random() * 15) + 3,
        receita: Math.floor(Math.random() * 2000) + 800
      });
    }

    // Dados de receita mensal
    const receitaMensal = [
      { mes: 'Jan', receita: 45000, meta: 50000 },
      { mes: 'Fev', receita: 52000, meta: 50000 },
      { mes: 'Mar', receita: 48000, meta: 55000 },
      { mes: 'Abr', receita: 61000, meta: 55000 },
      { mes: 'Mai', receita: 58000, meta: 60000 },
      { mes: 'Jun', receita: 67000, meta: 60000 }
    ];

    // Performance dos motoristas
    const performanceMotoristas = [
      { nome: 'João', corridas: 95, avaliacao: 4.8, receita: 3200 },
      { nome: 'Maria', corridas: 87, avaliacao: 4.9, receita: 2950 },
      { nome: 'Pedro', corridas: 78, avaliacao: 4.6, receita: 2680 },
      { nome: 'Ana', corridas: 92, avaliacao: 4.7, receita: 3100 },
      { nome: 'Carlos', corridas: 83, avaliacao: 4.5, receita: 2800 }
    ];

    // Distribuição por cidades
    const distribuicaoCidades = [
      { cidade: 'São Paulo', corridas: 245, receita: 12500 },
      { cidade: 'Rio de Janeiro', corridas: 189, receita: 9800 },
      { cidade: 'Brasília', corridas: 156, receita: 8200 },
      { cidade: 'Salvador', corridas: 134, receita: 6900 },
      { cidade: 'Fortaleza', corridas: 98, receita: 5100 }
    ];

    // Horários de pico
    const horariosPico = [
      { hora: '6h', corridas: 12 },
      { hora: '7h', corridas: 28 },
      { hora: '8h', corridas: 45 },
      { hora: '9h', corridas: 32 },
      { hora: '12h', corridas: 38 },
      { hora: '18h', corridas: 52 },
      { hora: '19h', corridas: 48 },
      { hora: '20h', corridas: 35 }
    ];

    setChartData({
      corridas_diarias: corridasDiarias,
      receita_mensal: receitaMensal,
      performance_motoristas: performanceMotoristas,
      distribuicao_cidades: distribuicaoCidades,
      horarios_pico: horariosPico
    });
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        ))}
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
        <TrendingUp className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">Análises Avançadas</h2>
      </motion.div>

      {/* Grid de Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Gráfico de Corridas Diárias */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Clock className="w-5 h-5 text-blue-600" />
            <span>Tendência de Corridas (7 dias)</span>
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.corridas_diarias}>
              <defs>
                <linearGradient id="concluidas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={COLORS.success} stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="canceladas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.danger} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={COLORS.danger} stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="data" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="concluidas"
                stackId="1"
                stroke={COLORS.success}
                fill="url(#concluidas)"
                name="Concluídas"
              />
              <Area
                type="monotone"
                dataKey="canceladas"
                stackId="1"
                stroke={COLORS.danger}
                fill="url(#canceladas)"
                name="Canceladas"
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Gráfico de Receita vs Meta */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            <span>Receita vs Meta Mensal</span>
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.receita_mensal}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="mes" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip 
                formatter={(value) => [`R$ ${value.toLocaleString()}`, '']}
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Legend />
              <Bar 
                dataKey="receita" 
                fill={COLORS.success} 
                name="Receita Real"
                radius={[4, 4, 0, 0]}
              />
              <Bar 
                dataKey="meta" 
                fill={COLORS.warning} 
                name="Meta"
                radius={[4, 4, 0, 0]}
                opacity={0.7}
              />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Performance dos Motoristas */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Target className="w-5 h-5 text-purple-600" />
            <span>Top 5 Motoristas</span>
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart 
              data={chartData.performance_motoristas}
              layout="horizontal"
            >
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis type="number" fontSize={12} />
              <YAxis dataKey="nome" type="category" fontSize={12} width={60} />
              <Tooltip 
                formatter={(value, name) => {
                  if (name === 'corridas') return [`${value} corridas`, ''];
                  if (name === 'avaliacao') return [`${value} ⭐`, ''];
                  return [`R$ ${value}`, ''];
                }}
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Bar 
                dataKey="corridas" 
                fill={COLORS.primary} 
                name="Corridas"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Distribuição por Cidades */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <MapPin className="w-5 h-5 text-red-600" />
            <span>Corridas por Cidade</span>
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.distribuicao_cidades}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ cidade, percent }) => `${cidade} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="corridas"
              >
                {chartData.distribuicao_cidades.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value, name) => [`${value} corridas`, '']}
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Gráfico de Horários de Pico (Full Width) */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Clock className="w-5 h-5 text-indigo-600" />
          <span>Horários de Maior Demanda</span>
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData.horarios_pico}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis dataKey="hora" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip 
              formatter={(value) => [`${value} corridas`, '']}
              contentStyle={{
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                border: 'none',
                borderRadius: '8px',
                color: 'white'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="corridas" 
              stroke={COLORS.info}
              strokeWidth={3}
              dot={{ fill: COLORS.info, strokeWidth: 2, r: 6 }}
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Crescimento Semanal</p>
              <p className="text-2xl font-bold">+15.3%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Eficiência Média</p>
              <p className="text-2xl font-bold">87.5%</p>
            </div>
            <Target className="w-8 h-8 text-green-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Ticket Médio</p>
              <p className="text-2xl font-bold">R$ 25.80</p>
            </div>
            <DollarSign className="w-8 h-8 text-purple-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-gradient-to-r from-red-500 to-red-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm">Tempo Médio</p>
              <p className="text-2xl font-bold">18 min</p>
            </div>
            <Clock className="w-8 h-8 text-red-200" />
          </div>
        </motion.div>
      </div>
    </div>
  );
}
