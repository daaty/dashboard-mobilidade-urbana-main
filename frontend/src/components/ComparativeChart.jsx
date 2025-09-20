import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar, Activity, Target } from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#06B6D4', '#F97316', '#84CC16'];

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ComparativeChart = ({ filters }) => {
  const [comparativeData, setComparativeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategory, setActiveCategory] = useState('total');
  const [monthsMetadata, setMonthsMetadata] = useState([]);
  const [rawData, setRawData] = useState(null); // Para armazenar dados brutos

  const fetchComparativeData = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔍 ComparativeChart - Filtros recebidos:', filters);

      // Determinar período em meses baseado no filtro
      let periodoMeses = 6; // padrão 6 meses
      if (filters.periodo === '3m') periodoMeses = 3;
      else if (filters.periodo === '6m') periodoMeses = 6;
      else if (filters.periodo === '12m') periodoMeses = 12;

      console.log(`📅 Buscando dados comparativos para ${periodoMeses} meses`);
      
      const params = new URLSearchParams({
        periodo: periodoMeses.toString(),
        // Removido filtro de cidade - sempre buscar todas
      });
      
      console.log(`🚀 Requisição: ${API_URL}/api/metrics/comparative?${params.toString()}`);
      
      const response = await fetch(`${API_URL}/api/metrics/comparative?${params.toString()}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('📊 Dados recebidos do endpoint:', data);
        
        if (data.success && data.daily_data && data.months_metadata) {
          console.log('📊 Estrutura dos dados recebidos:', {
            daily_data_sample: data.daily_data.slice(0, 3),
            months_metadata: data.months_metadata,
            activeCategory: activeCategory
          });
          
          // Armazenar dados brutos para reprocessamento quando categoria mudar
          setRawData(data);
          setMonthsMetadata(data.months_metadata);
          
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
    const processedData = data.daily_data.map(dayData => {
      const dayObject = {
        day: dayData.day,
      };
      
      // Para cada mês nos metadados, adicionar as linhas do gráfico
      data.months_metadata.forEach(month => {
        const key = `${month.key}_${category}`;
        dayObject[key] = dayData[key] || 0;
      });
      
      return dayObject;
    });
    
    console.log('📈 Dados processados para categoria:', category, processedData.slice(0, 5));
    setComparativeData(processedData);
  };

  // Effect para buscar dados quando filtros mudarem (nova requisição)
  useEffect(() => {
    fetchComparativeData();
  }, [filters.periodo, filters.cidade]);

  // Effect para reprocessar dados quando categoria ativa mudar (sem nova requisição)
  useEffect(() => {
    if (rawData && monthsMetadata.length > 0) {
      processDataForCategory(rawData, activeCategory);
    }
  }, [activeCategory]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-600 mb-2">{`Dia ${label}`}</p>
          {payload.map((entry, index) => {
            const monthKey = entry.dataKey.split('_')[0] + '_' + entry.dataKey.split('_')[1];
            const monthData = monthsMetadata.find(m => m.key === monthKey);
            return (
              <p key={index} className="text-sm" style={{ color: entry.color }}>
                <span className="font-medium">{monthData?.label || 'Desconhecido'}</span>
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
      <div className="w-full h-[400px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="text-blue-600" size={20} />
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500 dark:text-gray-400">Carregando dados comparativos...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-[400px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="text-red-600" size={20} />
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 mb-4">⚠️</div>
            <p className="text-gray-600 dark:text-gray-300 mb-2">Erro ao carregar dados</p>
            <p className="text-sm text-gray-400 dark:text-gray-500">{error}</p>
            <button 
              onClick={fetchComparativeData}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!comparativeData || comparativeData.length === 0) {
    return (
      <div className="w-full h-[400px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="text-gray-400" size={20} />
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Calendar className="text-gray-400 mx-auto mb-4" size={48} />
            <p className="text-gray-600 dark:text-gray-300 mb-2">Nenhum dado disponível</p>
            <p className="text-sm text-gray-400 dark:text-gray-500">Não foram encontrados dados para o período selecionado</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-[500px] bg-gray-50 dark:bg-gray-700 rounded-lg p-6 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <TrendingUp className="text-blue-600" size={20} />
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Análise Comparativa por Dia do Mês</h2>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Resumo dos Meses */}
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {monthsMetadata.length} meses comparados
          </div>
        </div>
      </div>

      {/* ABAS DE CATEGORIA - Voltando ao estilo original */}
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

      {/* Resumo dos Meses */}
      <div className="flex flex-wrap gap-2 mb-4">
        {monthsMetadata.map((month, index) => (
          <div key={month.key} className="flex items-center space-x-2 text-xs bg-white dark:bg-gray-800 px-2 py-1 rounded border border-gray-200 dark:border-gray-600">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            ></div>
            <span className="text-gray-700 dark:text-gray-300">{month.label}</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {activeCategory === 'total' ? month.total_geral :
               activeCategory === 'concluidas' ? month.total_concluidas :
               activeCategory === 'canceladas' ? month.total_canceladas :
               month.total_perdidas}
            </span>
          </div>
        ))}
      </div>

      {/* Gráfico */}
      <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={comparativeData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="day" 
              stroke="#666"
              fontSize={11}
              tick={{ fill: '#666' }}
              tickLine={{ stroke: '#666' }}
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
                const monthKey = value.split('_')[0] + '_' + value.split('_')[1];
                const monthData = monthsMetadata.find(m => m.key === monthKey);
                return monthData?.label || 'Desconhecido';
              }}
            />
            
            {/* Uma linha para cada mês */}
            {monthsMetadata.map((month, index) => (
              <Line
                key={`${month.key}_${activeCategory}`}
                type="monotone"
                dataKey={`${month.key}_${activeCategory}`}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2}
                dot={{ fill: COLORS[index % COLORS.length], strokeWidth: 2, r: 3 }}
                activeDot={{ r: 5, fill: COLORS[index % COLORS.length] }}
                connectNulls={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ComparativeChart;
