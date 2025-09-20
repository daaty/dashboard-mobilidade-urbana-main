import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Clock, TrendingUp, Activity, Target, BarChart3 } from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#06B6D4', '#F97316', '#84CC16'];

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ComparativeHourlyChart = ({ filters }) => {
  const [hourlyData, setHourlyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategory, setActiveCategory] = useState('total');
  const [chartType, setChartType] = useState('line'); // 'line' ou 'bar'
  const [periodsMetadata, setPeriodsMetadata] = useState([]);
  const [rawData, setRawData] = useState(null);

  const fetchHourlyData = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔍 ComparativeHourlyChart - Filtros recebidos:', filters);

      // Determinar período baseado no filtro
      let periodo = '6m'; // padrão 6 meses
      if (filters.periodo === '3m') periodo = '3m';
      else if (filters.periodo === '6m') periodo = '6m';
      else if (filters.periodo === '12m') periodo = '12m';
      else if (filters.periodo === '30d') periodo = '30d';
      else if (filters.periodo === '7d') periodo = '7d';

      console.log(`⏰ Buscando dados comparativos por horário para ${periodo}`);
      
      const params = new URLSearchParams({
        periodo: periodo,
        tipo: 'horario' // Especificar que queremos análise por horário
      });
      
      // Adicionar filtro de cidade se selecionado
      if (filters.cidade) {
        params.append('cidade', filters.cidade);
      }
      
      console.log(`🚀 Requisição: ${API_URL}/api/metrics/comparative-hourly?${params.toString()}`);
      
      const response = await fetch(`${API_URL}/api/metrics/comparative-hourly?${params.toString()}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('📊 Dados por horário recebidos:', data);
        
        if (data.success && data.hourly_data && data.periods_metadata) {
          // Armazenar dados brutos para reprocessamento quando categoria mudar
          setRawData(data);
          setPeriodsMetadata(data.periods_metadata);
          
          // Processar dados da nova estrutura do endpoint
          processDataForCategory(data, activeCategory);
        } else {
          console.warn('⚠️ Estrutura de dados inválida:', data);
          setError('Estrutura de dados inválida recebida do servidor');
        }
      } else {
        console.error(`❌ Erro na requisição: ${response.status}`);
        const errorText = await response.text();
        setError(`Erro ${response.status}: ${errorText}`);
      }
    } catch (err) {
      console.error('💥 Erro na busca dos dados:', err);
      setError(`Erro de conexão: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const processDataForCategory = (data, category) => {
    const processedData = data.hourly_data.map(hourData => {
      const hourObject = {
        hour: hourData.hour,
        hourFormatted: `${hourData.hour.toString().padStart(2, '0')}:00`, // Formato visual
      };
      
      // Para cada período nos metadados, adicionar as linhas do gráfico
      data.periods_metadata.forEach(period => {
        const key = `${period.key}_${category}`;
        hourObject[key] = hourData[key] || 0;
      });
      
      return hourObject;
    });
    
    console.log('📈 Dados processados para categoria por horário:', category, processedData.slice(0, 5));
    setHourlyData(processedData);
  };

  // Effect para buscar dados quando filtros mudarem (nova requisição)
  useEffect(() => {
    fetchHourlyData();
  }, [filters.periodo, filters.cidade]);

  // Effect para reprocessar dados quando categoria ativa mudar (sem nova requisição)
  useEffect(() => {
    if (rawData && periodsMetadata.length > 0) {
      processDataForCategory(rawData, activeCategory);
    }
  }, [activeCategory]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border dark:border-gray-600 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">{`${label}`}</p>
          {payload.map((entry, index) => {
            const periodKey = entry.dataKey.replace(`_${activeCategory}`, '');
            const periodData = periodsMetadata.find(p => p.key === periodKey);
            return (
              <p key={index} className="text-sm" style={{ color: entry.color }}>
                <span className="font-medium">{periodData?.label || 'Período'}</span>
                {`: ${entry.value} ${activeCategory === 'total' ? 'corridas' : 
                  activeCategory === 'concluidas' ? 'concluídas' :
                  activeCategory === 'canceladas' ? 'canceladas' : 'perdidas'}`}
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="w-full h-[500px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Clock className="text-blue-600" size={20} />
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa por Horário</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500 dark:text-gray-400">Carregando dados por horário...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-[500px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Clock className="text-red-600" size={20} />
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa por Horário</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 mb-4">⚠️</div>
            <p className="text-gray-600 dark:text-gray-300 mb-2">Erro ao carregar dados</p>
            <p className="text-sm text-gray-400 dark:text-gray-500">{error}</p>
            <button 
              onClick={fetchHourlyData}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!hourlyData || hourlyData.length === 0) {
    return (
      <div className="w-full h-[500px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Clock className="text-gray-400" size={20} />
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa por Horário</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Clock className="text-gray-400 mx-auto mb-4" size={48} />
            <p className="text-gray-600 dark:text-gray-300 mb-2">Nenhum dado disponível</p>
            <p className="text-sm text-gray-400 dark:text-gray-500">Não foram encontrados dados para o período selecionado</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-[600px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Clock className="text-blue-600" size={20} />
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa por Horário do Dia</h2>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Tipo de Gráfico */}
          <div className="flex space-x-1">
            <button
              onClick={() => setChartType('line')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                chartType === 'line'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600'
              }`}
            >
              <TrendingUp size={12} className="inline mr-1" />
              Linha
            </button>
            <button
              onClick={() => setChartType('bar')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                chartType === 'bar'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600'
              }`}
            >
              <BarChart3 size={12} className="inline mr-1" />
              Barra
            </button>
          </div>
          
          {/* Resumo dos Períodos */}
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {periodsMetadata.length} períodos comparados
          </div>
        </div>
      </div>

      {/* ABAS DE CATEGORIA */}
      <div className="flex space-x-1 mb-4">
        {[
          { key: 'total', label: 'Total', icon: Target },
          { key: 'concluidas', label: 'Concluídas', icon: Activity },
          { key: 'canceladas', label: 'Canceladas', icon: Activity },
          { key: 'perdidas', label: 'Perdidas', icon: Activity }
        ].map((category) => {
          const Icon = category.icon;
          return (
            <button
              key={category.key}
              onClick={() => setActiveCategory(category.key)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeCategory === category.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600'
              }`}
            >
              <Icon size={16} />
              <span>{category.label}</span>
            </button>
          );
        })}
      </div>

      {/* Resumo dos Períodos */}
      <div className="flex flex-wrap gap-2 mb-4">
        {periodsMetadata.map((period, index) => (
          <div key={period.key} className="flex items-center space-x-2 text-xs bg-white dark:bg-gray-800 px-2 py-1 rounded border border-gray-200 dark:border-gray-600">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            ></div>
            <span className="text-gray-700 dark:text-gray-300">{period.label}</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {activeCategory === 'total' ? period.total_geral :
               activeCategory === 'concluidas' ? period.total_concluidas :
               activeCategory === 'canceladas' ? period.total_canceladas :
               period.total_perdidas}
            </span>
          </div>
        ))}
      </div>

      {/* Gráfico */}
      <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg p-4">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'line' ? (
            <LineChart data={hourlyData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="hourFormatted" 
                stroke="#666"
                fontSize={11}
                tick={{ fill: '#666' }}
                tickLine={{ stroke: '#666' }}
                interval={0}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                stroke="#666"
                fontSize={11}
                tick={{ fill: '#666' }}
                tickLine={{ stroke: '#666' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '12px' }}
                formatter={(value, entry) => {
                  const periodKey = value.replace(`_${activeCategory}`, '');
                  const periodData = periodsMetadata.find(p => p.key === periodKey);
                  return periodData?.label || 'Período';
                }}
              />
              
              {/* Uma linha para cada período */}
              {periodsMetadata.map((period, index) => (
                <Line
                  key={`${period.key}_${activeCategory}`}
                  type="monotone"
                  dataKey={`${period.key}_${activeCategory}`}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                  dot={{ fill: COLORS[index % COLORS.length], strokeWidth: 2, r: 3 }}
                  activeDot={{ r: 5, fill: COLORS[index % COLORS.length] }}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          ) : (
            <BarChart data={hourlyData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="hourFormatted" 
                stroke="#666"
                fontSize={11}
                tick={{ fill: '#666' }}
                tickLine={{ stroke: '#666' }}
                interval={0}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                stroke="#666"
                fontSize={11}
                tick={{ fill: '#666' }}
                tickLine={{ stroke: '#666' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '12px' }}
                formatter={(value, entry) => {
                  const periodKey = value.replace(`_${activeCategory}`, '');
                  const periodData = periodsMetadata.find(p => p.key === periodKey);
                  return periodData?.label || 'Período';
                }}
              />
              
              {/* Uma barra para cada período */}
              {periodsMetadata.map((period, index) => (
                <Bar
                  key={`${period.key}_${activeCategory}`}
                  dataKey={`${period.key}_${activeCategory}`}
                  fill={COLORS[index % COLORS.length]}
                  name={period.label}
                />
              ))}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ComparativeHourlyChart;