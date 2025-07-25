import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Brain, 
  Calendar, 
  MapPin, 
  Users, 
  DollarSign,
  AlertTriangle,
  Target,
  Zap,
  ChevronRight,
  BarChart3
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const AnalisePreditiva = ({ data }) => {
  const [periodo, setPeriodo] = useState('7d');
  const [tipoAnalise, setTipoAnalise] = useState('demanda');
  const [predictions, setPredictions] = useState({});
  const [insights, setInsights] = useState([]);

  // Simular dados preditivos baseados nos dados reais
  useEffect(() => {
    // Simular análise preditiva
    const generatePredictions = () => {
      const historicalData = data?.historical || [];
      
      // Simular previsões
      const demandaPrediction = Array.from({ length: 7 }, (_, i) => ({
        dia: `Dia ${i + 1}`,
        previsao: Math.floor(Math.random() * 50) + 30,
        confianca: Math.random() * 30 + 70,
        real: i < 3 ? Math.floor(Math.random() * 45) + 25 : null
      }));

      const receitaPrediction = Array.from({ length: 30 }, (_, i) => ({
        dia: i + 1,
        previsao: Math.floor(Math.random() * 2000) + 1500,
        tendencia: Math.random() > 0.5 ? 'alta' : 'baixa',
        confianca: Math.random() * 25 + 75
      }));

      const sazonalidadeData = [
        { hora: '00:00', demanda: 15, tipo: 'Baixa' },
        { hora: '06:00', demanda: 45, tipo: 'Média' },
        { hora: '08:00', demanda: 85, tipo: 'Alta' },
        { hora: '12:00', demanda: 70, tipo: 'Alta' },
        { hora: '18:00', demanda: 95, tipo: 'Pico' },
        { hora: '22:00', demanda: 60, tipo: 'Média' },
      ];

      const zonasQuentes = [
        { zona: 'Centro', score: 95, corridas: 120, tendencia: 'crescendo' },
        { zona: 'Zona Sul', score: 87, corridas: 98, tendencia: 'estável' },
        { zona: 'Aeroporto', score: 78, corridas: 76, tendencia: 'crescendo' },
        { zona: 'Shopping', score: 65, corridas: 54, tendencia: 'declinando' },
        { zona: 'Universidade', score: 58, corridas: 43, tendencia: 'estável' }
      ];

      setPredictions({
        demanda: demandaPrediction,
        receita: receitaPrediction,
        sazonalidade: sazonalidadeData,
        zonasQuentes
      });

      // Gerar insights automáticos
      const autoInsights = [
        {
          tipo: 'oportunidade',
          titulo: 'Horário de Pico Subutilizado',
          descricao: 'Sextas-feiras às 19h mostram potencial de 25% mais corridas',
          impacto: 'Alto',
          acao: 'Implementar incentivos para motoristas neste horário',
          icone: TrendingUp,
          cor: 'green'
        },
        {
          tipo: 'risco',
          titulo: 'Queda Prevista na Zona Sul',
          descricao: 'Modelo prevê redução de 15% nas corridas nos próximos 7 dias',
          impacto: 'Médio',
          acao: 'Investigar causas e implementar campanhas de marketing local',
          icone: TrendingDown,
          cor: 'yellow'
        },
        {
          tipo: 'otimizacao',
          titulo: 'Realocação de Frota Recomendada',
          descricao: 'IA sugere mover 8 motoristas para o Centro durante manhãs',
          impacto: 'Alto',
          acao: 'Implementar sistema de redistribuição dinâmica',
          icone: Users,
          cor: 'blue'
        },
        {
          tipo: 'critico',
          titulo: 'Meta Mensal em Risco',
          descricao: 'Probabilidade de 78% de não atingir meta de receita',
          impacto: 'Crítico',
          acao: 'Ativar plano de contingência imediatamente',
          icone: AlertTriangle,
          cor: 'red'
        }
      ];

      setInsights(autoInsights);
    };

    generatePredictions();
  }, [data, periodo]);

  const ModeloCard = ({ titulo, subtitulo, valor, confianca, tendencia, icone: Icon, cor }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-lg p-6 border shadow-sm"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg bg-${cor}-100`}>
          <Icon className={`h-6 w-6 text-${cor}-600`} />
        </div>
        <span className={`text-sm font-medium px-2 py-1 rounded-full bg-${cor}-100 text-${cor}-700`}>
          {confianca}% confiança
        </span>
      </div>
      
      <h3 className="font-semibold text-gray-900 mb-1">{titulo}</h3>
      <p className="text-sm text-gray-600 mb-3">{subtitulo}</p>
      
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold text-gray-900">{valor}</span>
        <div className="flex items-center">
          {tendencia === 'alta' ? (
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
          )}
          <span className={`text-sm font-medium ${
            tendencia === 'alta' ? 'text-green-600' : 'text-red-600'
          }`}>
            {tendencia}
          </span>
        </div>
      </div>
    </motion.div>
  );

  const InsightCard = ({ insight }) => {
    const Icon = insight.icone;
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className={`bg-white border-l-4 border-${insight.cor}-500 rounded-lg p-4 shadow-sm`}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <Icon className={`h-5 w-5 text-${insight.cor}-500 mt-0.5`} />
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="font-semibold text-gray-900">{insight.titulo}</h4>
                <span className={`text-xs px-2 py-1 rounded-full bg-${insight.cor}-100 text-${insight.cor}-700`}>
                  {insight.impacto}
                </span>
              </div>
              <p className="text-gray-700 text-sm mb-2">{insight.descricao}</p>
              <p className="text-blue-600 text-sm font-medium">
                💡 {insight.acao}
              </p>
            </div>
          </div>
          <ChevronRight className="h-4 w-4 text-gray-400" />
        </div>
      </motion.div>
    );
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="h-6 w-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Análise Preditiva</h2>
          <span className="bg-purple-100 text-purple-700 text-xs font-bold px-2 py-1 rounded-full">
            IA
          </span>
        </div>
        
        <div className="flex gap-2">
          <select
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="7d">Próximos 7 dias</option>
            <option value="30d">Próximos 30 dias</option>
            <option value="90d">Próximos 3 meses</option>
          </select>
          
          <select
            value={tipoAnalise}
            onChange={(e) => setTipoAnalise(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="demanda">Demanda</option>
            <option value="receita">Receita</option>
            <option value="sazonalidade">Sazonalidade</option>
            <option value="zonas">Zonas Quentes</option>
          </select>
        </div>
      </div>

      {/* Modelos Preditivos */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ModeloCard
          titulo="Demanda Prevista"
          subtitulo="Próximas 24h"
          valor="127 corridas"
          confianca={87}
          tendencia="alta"
          icone={TrendingUp}
          cor="blue"
        />
        
        <ModeloCard
          titulo="Receita Estimada"
          subtitulo="Próximos 7 dias"
          valor="R$ 12.450"
          confianca={82}
          tendencia="alta"
          icone={DollarSign}
          cor="green"
        />
        
        <ModeloCard
          titulo="Eficiência Prevista"
          subtitulo="Taxa de conversão"
          valor="78%"
          confianca={91}
          tendencia="baixa"
          icone={Target}
          cor="yellow"
        />
      </div>

      {/* Gráficos Preditivos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Previsão de Demanda */}
        <div className="bg-white rounded-lg p-6 border shadow-sm">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            Previsão de Demanda - Próximos 7 Dias
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={predictions.demanda}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="dia" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="previsao" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6' }}
                name="Previsão"
              />
              <Line 
                type="monotone" 
                dataKey="real" 
                stroke="#10B981" 
                strokeWidth={2}
                dot={{ fill: '#10B981' }}
                name="Real"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Análise de Sazonalidade */}
        <div className="bg-white rounded-lg p-6 border shadow-sm">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Calendar className="h-5 w-5 text-green-600" />
            Padrão de Sazonalidade
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={predictions.sazonalidade}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hora" />
              <YAxis />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="demanda" 
                stroke="#10B981" 
                fill="#10B981" 
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Zonas Quentes */}
      <div className="bg-white rounded-lg p-6 border shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MapPin className="h-5 w-5 text-red-600" />
          Zonas de Alta Demanda - Análise Preditiva
        </h3>
        
        <div className="space-y-3">
          {predictions.zonasQuentes?.map((zona, index) => (
            <div key={zona.zona} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${
                  zona.score > 80 ? 'bg-red-500' : 
                  zona.score > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`} />
                <div>
                  <span className="font-medium">{zona.zona}</span>
                  <span className="text-sm text-gray-600 ml-2">
                    {zona.corridas} corridas previstas
                  </span>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium">Score: {zona.score}</span>
                <div className="flex items-center gap-1">
                  {zona.tendencia === 'crescendo' ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : zona.tendencia === 'declinando' ? (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  ) : (
                    <div className="h-4 w-4 bg-gray-400 rounded-full" />
                  )}
                  <span className="text-sm text-gray-600 capitalize">
                    {zona.tendencia}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Insights Automáticos */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Zap className="h-5 w-5 text-yellow-600" />
          Insights Automáticos da IA
        </h3>
        
        <div className="space-y-3">
          {insights.map((insight, index) => (
            <InsightCard key={index} insight={insight} />
          ))}
        </div>
      </div>

      {/* Recomendações Estratégicas */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Brain className="h-5 w-5 text-purple-600" />
          Recomendações Estratégicas
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">🎯 Otimização Imediata</h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• Aumentar frota no Centro entre 8h-10h</li>
              <li>• Reduzir tarifa no Shopping para aumentar demanda</li>
              <li>• Implementar bônus para horários de baixa demanda</li>
            </ul>
          </div>
          
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">📈 Estratégia de Médio Prazo</h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• Expandir operação na Zona Norte</li>
              <li>• Parcerias com eventos na Universidade</li>
              <li>• Programa de fidelidade para clientes frequentes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalisePreditiva;
