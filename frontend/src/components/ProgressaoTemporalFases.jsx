import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  ComposedChart,
  Area,
  AreaChart
} from 'recharts';
import { Calendar, TrendingUp, BarChart3, Activity } from 'lucide-react';

const ProgressaoTemporalFases = ({ campanhasData, cidadesData }) => {
  const [tipoGrafico, setTipoGrafico] = useState('line');
  const [metricaSelecionada, setMetricaSelecionada] = useState('corridas');

  // Processar dados para progressão temporal
  const processarDadosTemporais = () => {
    const fases = ['Fase 1', 'Fase 2', 'Fase 3'];
    const meses = ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6'];
    
    return meses.map((mes, index) => {
      const dadosMes = {
        mes,
        mesNumero: index + 1
      };

      fases.forEach(fase => {
        // Calcular campanhas da fase
        const campanhasFase = campanhasData ? campanhasData.filter(c => c.fase === fase) : [];
        const cidadesFase = campanhasFase.map(c => c.cidade?.nome).filter(Boolean);
        
        // Simular progressão baseada na fase e mês
        let multiplicador = 1;
        if (fase === 'Fase 1' && index < 2) multiplicador = 1;
        else if (fase === 'Fase 2' && index >= 2 && index < 4) multiplicador = 1;
        else if (fase === 'Fase 3' && index >= 4) multiplicador = 1;
        else multiplicador = 0.3; // Fases futuras com progressão menor

        // Calcular métricas simuladas
        const baseCorridasFase = fase === 'Fase 1' ? 50 : fase === 'Fase 2' ? 50 : 110;
        const baseMotoristasFase = fase === 'Fase 1' ? 10 : fase === 'Fase 2' ? 12 : 15;
        const baseOrcamentoFase = fase === 'Fase 1' ? 4060 : fase === 'Fase 2' ? 6700 : 9030;

        const progressaoMes = Math.min(1, (index + 1) * 0.2); // Progressão até 100%
        
        dadosMes[`${fase}_corridas`] = Math.round(baseCorridasFase * multiplicador * progressaoMes);
        dadosMes[`${fase}_motoristas`] = Math.round(baseMotoristasFase * multiplicador * progressaoMes);
        dadosMes[`${fase}_orcamento`] = Math.round(baseOrcamentoFase * multiplicador * progressaoMes);
        dadosMes[`${fase}_roi`] = Math.round(250 * multiplicador * progressaoMes); // ROI simulado
        
        // Metas (valores fixos)
        dadosMes[`${fase}_meta_corridas`] = baseCorridasFase;
        dadosMes[`${fase}_meta_motoristas`] = baseMotoristasFase;
      });

      return dadosMes;
    });
  };

  const dados = processarDadosTemporais();

  // Configurações dos gráficos
  const configGraficos = {
    corridas: {
      titulo: 'Progressão de Corridas por Fase',
      dadosKey: 'corridas',
      unidade: 'corridas',
      cor: { 'Fase 1': '#3b82f6', 'Fase 2': '#8b5cf6', 'Fase 3': '#10b981' }
    },
    motoristas: {
      titulo: 'Aquisição de Motoristas por Fase',
      dadosKey: 'motoristas', 
      unidade: 'motoristas',
      cor: { 'Fase 1': '#f59e0b', 'Fase 2': '#ef4444', 'Fase 3': '#06b6d4' }
    },
    orcamento: {
      titulo: 'Execução Orçamentária por Fase',
      dadosKey: 'orcamento',
      unidade: 'R$',
      cor: { 'Fase 1': '#84cc16', 'Fase 2': '#f97316', 'Fase 3': '#ec4899' }
    },
    roi: {
      titulo: 'ROI Acumulado por Fase',
      dadosKey: 'roi',
      unidade: '%',
      cor: { 'Fase 1': '#6366f1', 'Fase 2': '#8b5cf6', 'Fase 3': '#a855f7' }
    }
  };

  const config = configGraficos[metricaSelecionada];

  const renderGraficoLinha = () => (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={dados}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="mes" stroke="#666" />
        <YAxis stroke="#666" />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '1px solid #e5e7eb',
            borderRadius: '8px'
          }}
          formatter={(value, name) => [
            `${value.toLocaleString()} ${config.unidade}`, 
            name.replace('Fase_', 'Fase ')
          ]}
        />
        <Legend />
        
        {['Fase 1', 'Fase 2', 'Fase 3'].map(fase => (
          <Line
            key={fase}
            type="monotone"
            dataKey={`${fase}_${config.dadosKey}`}
            stroke={config.cor[fase]}
            strokeWidth={3}
            dot={{ fill: config.cor[fase], strokeWidth: 2, r: 4 }}
            name={fase}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );

  const renderGraficoArea = () => (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={dados}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="mes" stroke="#666" />
        <YAxis stroke="#666" />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '1px solid #e5e7eb',
            borderRadius: '8px'
          }}
        />
        <Legend />
        
        {['Fase 1', 'Fase 2', 'Fase 3'].map(fase => (
          <Area
            key={fase}
            type="monotone"
            dataKey={`${fase}_${config.dadosKey}`}
            stackId="1"
            stroke={config.cor[fase]}
            fill={config.cor[fase]}
            fillOpacity={0.6}
            name={fase}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );

  const renderGraficoBarra = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={dados}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="mes" stroke="#666" />
        <YAxis stroke="#666" />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '1px solid #e5e7eb',
            borderRadius: '8px'
          }}
        />
        <Legend />
        
        {['Fase 1', 'Fase 2', 'Fase 3'].map(fase => (
          <Bar
            key={fase}
            dataKey={`${fase}_${config.dadosKey}`}
            fill={config.cor[fase]}
            name={fase}
            radius={[2, 2, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );

  const renderGrafico = () => {
    switch (tipoGrafico) {
      case 'line': return renderGraficoLinha();
      case 'area': return renderGraficoArea();
      case 'bar': return renderGraficoBarra();
      default: return renderGraficoLinha();
    }
  };

  // Calcular resumo das fases
  const resumoFases = ['Fase 1', 'Fase 2', 'Fase 3'].map(fase => {
    const campanhasFase = campanhasData ? campanhasData.filter(c => c.fase === fase) : [];
    const totalCampanhas = campanhasFase.length;
    const cidadesUnicas = [...new Set(campanhasFase.map(c => c.cidade?.nome))].filter(Boolean);
    const orcamentoTotal = campanhasFase.reduce((sum, c) => sum + (c.orcamento_previsto || 0), 0);
    
    return {
      fase,
      totalCampanhas,
      cidadesCount: cidadesUnicas.length,
      cidades: cidadesUnicas,
      orcamentoTotal,
      status: fase === 'Fase 1' ? 'Em Andamento' : fase === 'Fase 2' ? 'Iniciando' : 'Planejamento'
    };
  });

  return (
    <div className="space-y-6">
      {/* Cards Resumo das Fases */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {resumoFases.map((resumo, index) => (
          <Card key={index} className="relative overflow-hidden">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-bold flex items-center justify-between">
                <span>{resumo.fase}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  resumo.status === 'Em Andamento' ? 'bg-green-100 text-green-800' :
                  resumo.status === 'Iniciando' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {resumo.status}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Campanhas:</span>
                  <span className="font-semibold">{resumo.totalCampanhas}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Cidades:</span>
                  <span className="font-semibold">{resumo.cidadesCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Orçamento:</span>
                  <span className="font-semibold">R$ {resumo.orcamentoTotal.toLocaleString()}</span>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  {resumo.cidades.join(', ')}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Gráfico Principal */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
            <CardTitle className="text-xl font-bold flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>{config.titulo}</span>
            </CardTitle>
            
            <div className="flex flex-wrap gap-2">
              {/* Seletor de Métrica */}
              <select 
                value={metricaSelecionada}
                onChange={(e) => setMetricaSelecionada(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value="corridas">Corridas</option>
                <option value="motoristas">Motoristas</option>
                <option value="orcamento">Orçamento</option>
                <option value="roi">ROI</option>
              </select>

              {/* Tipo de Gráfico */}
              <div className="flex border border-gray-300 rounded-lg overflow-hidden">
                <button
                  onClick={() => setTipoGrafico('line')}
                  className={`px-3 py-1 text-sm ${tipoGrafico === 'line' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'}`}
                >
                  Linha
                </button>
                <button
                  onClick={() => setTipoGrafico('area')}
                  className={`px-3 py-1 text-sm ${tipoGrafico === 'area' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'}`}
                >
                  Área
                </button>
                <button
                  onClick={() => setTipoGrafico('bar')}
                  className={`px-3 py-1 text-sm ${tipoGrafico === 'bar' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'}`}
                >
                  Barra
                </button>
              </div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {renderGrafico()}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProgressaoTemporalFases;
