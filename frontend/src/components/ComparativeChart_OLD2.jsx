import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar, Activity, Target } from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#06B6D4', '#F97316', '#84CC16'];

const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://dashboard-mobilidade-urbana-main.onrender.com'
  : 'http://localhost:8000';

const ComparativeChart = ({ filters }) => {
  const [comparativeData, setComparativeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategory, setActiveCategory] = useState('total');
  const [monthsMetadata, setMonthsMetadata] = useState([]);

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
          // Processar dados da nova estrutura do endpoint
          const processedData = data.daily_data.map(dayData => ({
            day: dayData.day,
            // Para cada mês nos metadados, adicionar as linhas do gráfico
            ...Object.fromEntries(
              data.months_metadata.map(month => [
                `${month.key}_${activeCategory}`, 
                dayData[`${month.key}_${activeCategory}`] || 0
              ])
            )
          }));
          
          console.log('📈 Dados processados para o gráfico:', processedData.slice(0, 5));
          console.log('🗓️ Metadados dos meses:', data.months_metadata);
          
          setComparativeData(processedData);
          setMonthsMetadata(data.months_metadata);
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

  // Effect para buscar dados quando filtros mudarem
  useEffect(() => {
    fetchComparativeData();
  }, [filters.periodo, filters.cidade]);

  // Effect para reprocessar dados quando categoria ativa mudar
  useEffect(() => {
    if (monthsMetadata.length > 0) {
      fetchComparativeData();
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
      <div className="w-full h-[400px] bg-white rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="text-blue-600" size={20} />
            <h2 className="text-lg font-semibold text-gray-800">Análise Comparativa</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Carregando dados comparativos...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-[400px] bg-white rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="text-red-600" size={20} />
            <h2 className="text-lg font-semibold text-gray-800">Análise Comparativa</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 mb-4">⚠️</div>
            <p className="text-gray-600 mb-2">Erro ao carregar dados</p>
            <p className="text-sm text-gray-400">{error}</p>
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
      <div className="w-full h-[400px] bg-white rounded-lg p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="text-gray-400" size={20} />
            <h2 className="text-lg font-semibold text-gray-800">Análise Comparativa</h2>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Calendar className="text-gray-400 mx-auto mb-4" size={48} />
            <p className="text-gray-600 mb-2">Nenhum dado disponível</p>
            <p className="text-sm text-gray-400">Não foram encontrados dados para o período selecionado</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-[500px] bg-white rounded-lg p-6 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <TrendingUp className="text-blue-600" size={20} />
          <h2 className="text-lg font-semibold text-gray-800">Análise Comparativa por Dia do Mês</h2>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Seletor de Categoria */}
          <div className="flex items-center space-x-2">
            <Activity size={16} className="text-gray-500" />
            <select 
              value={activeCategory} 
              onChange={(e) => setActiveCategory(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="total">Total de Corridas</option>
              <option value="concluidas">Corridas Concluídas</option>
              <option value="canceladas">Corridas Canceladas</option>
              <option value="perdidas">Corridas Perdidas</option>
            </select>
          </div>

          {/* Resumo dos Meses */}
          <div className="text-sm text-gray-600">
            {monthsMetadata.length} meses comparados
          </div>
        </div>
      </div>

      {/* Resumo dos Meses */}
      <div className="flex flex-wrap gap-2 mb-4">
        {monthsMetadata.map((month, index) => (
          <div key={month.key} className="flex items-center space-x-2 text-xs bg-gray-50 px-2 py-1 rounded">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            ></div>
            <span className="text-gray-700">{month.label}</span>
            <span className="font-medium text-gray-900">
              {activeCategory === 'total' ? month.total_geral :
               activeCategory === 'concluidas' ? month.total_concluidas :
               activeCategory === 'canceladas' ? month.total_canceladas :
               month.total_perdidas}
            </span>
          </div>
        ))}
      </div>

      {/* Gráfico */}
      <div className="flex-1">
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