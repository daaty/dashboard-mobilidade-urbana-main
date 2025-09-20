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
          
          console.log('� Dados processados para o gráfico:', processedData.slice(0, 5));
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
              const data = await response.json();
              console.log(`✅ Dados recebidos para ${monthLabel}:`, data);
              
              if (data.success && data.comparative_data && data.comparative_data.length > 0) {
                const monthData = {
                  period: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}`,
                  label: monthLabel,
                  dailyData: {}
                };
                
                // Inicializar todos os dias do mês
                for (let day = 1; day <= 31; day++) {
                  monthData.dailyData[day] = { total: 0, concluidas: 0, canceladas: 0, perdidas: 0 };
                }
                
                // Processar dados do mês
                data.comparative_data.forEach((item, index) => {
                  let day = null;
                  
                  if (item.nome && item.nome.includes('/')) {
                    day = parseInt(item.nome.split('/')[0]);
                  } else if (item.periodo) {
                    const date = new Date(item.periodo);
                    day = !isNaN(date.getTime()) ? date.getDate() : null;
                  } else {
                    day = index + 1; // Fallback: usar índice
                  }
                  
                  if (day && day >= 1 && day <= 31) {
                    monthData.dailyData[day] = {
                      total: item.total || 0,
                      concluidas: item.concluidas || 0,
                      canceladas: item.canceladas || 0,
                      perdidas: item.perdidas || 0
                    };
                  }
                });
                
                // Verificar se o mês tem dados válidos
                const totalRecords = Object.values(monthData.dailyData).reduce((sum, day) => sum + day.total, 0);
                console.log(`📊 ${monthLabel}: ${totalRecords} corridas totais`);
                
                allMonthsData.push(monthData);
              } else {
                console.log(`❌ ${monthLabel}: Sem dados válidos`);
                // Mesmo sem dados, adicionar mês vazio para manter estrutura
                const emptyMonth = {
                  period: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}`,
                  label: monthLabel,
                  dailyData: {}
                };
                for (let day = 1; day <= 31; day++) {
                  emptyMonth.dailyData[day] = { total: 0, concluidas: 0, canceladas: 0, perdidas: 0 };
                }
                allMonthsData.push(emptyMonth);
              }
            } else {
              console.error(`❌ ${monthLabel}: HTTP ${response.status}`);
            }
          } catch (err) {
            console.error(`❌ Erro ao buscar ${monthLabel}:`, err);
          }
        }
        
        console.log(`📊 Total de meses processados: ${allMonthsData.length}`);
        setComparativeData({ months: allMonthsData });
        
      } else {
        // Para períodos menores (hoje, 7d, 30d), usar lógica atual
        console.log(`🔍 Período simples: ${filters.periodo}`);
        
        const params = new URLSearchParams({
          periodo: filters.periodo || '30d',
          cidade: filters.cidade || 'todas'
        });
        
        console.log(`🚀 Requisição única: ${API_URL}/api/metrics/comparative?${params.toString()}`);
        
        const response = await fetch(`${API_URL}/api/metrics/comparative?${params.toString()}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Dados recebidos:', data);
        
        if (!data.success || !data.comparative_data) {
          console.log('❌ Estrutura de dados inválida:', data);
          setComparativeData({ months: [] });
          return;
        }
        
        console.log(`📊 Total de ${data.comparative_data.length} registros recebidos`);
        
        // Processar dados em formato de mês único
        const monthData = {
          period: data.periodo || filters.periodo,
          label: 'Atual',
          dailyData: {}
        };
        
        // Inicializar todos os dias do mês (1-31)
        for (let day = 1; day <= 31; day++) {
          monthData.dailyData[day] = { total: 0, concluidas: 0, canceladas: 0, perdidas: 0 };
        }
        
        // Processar dados recebidos
        data.comparative_data.forEach((item, index) => {
          console.log(`🔍 Item ${index}:`, {
            nome: item.nome,
            periodo: item.periodo,
            total: item.total,
            concluidas: item.concluidas,
            canceladas: item.canceladas,
            perdidas: item.perdidas
          });
          
          let day = null;
          
          if (item.nome && item.nome.includes('/')) {
            const dayPart = item.nome.split('/')[0];
            day = parseInt(dayPart);
            console.log(`📅 Dia extraído do nome '${item.nome}': ${day}`);
          } else if (item.periodo) {
            const date = new Date(item.periodo);
            if (!isNaN(date.getTime())) {
              day = date.getDate();
              console.log(`📅 Dia extraído do período '${item.periodo}': ${day}`);
            }
          } else {
            day = index + 1;
            console.log(`📅 Usando índice como dia: ${day}`);
          }
          
          if (day && day >= 1 && day <= 31) {
            monthData.dailyData[day] = {
              total: item.total || 0,
              concluidas: item.concluidas || 0,
              canceladas: item.canceladas || 0,
              perdidas: item.perdidas || 0
            };
            console.log(`✅ Processado dia ${day}:`, monthData.dailyData[day]);
          } else {
            console.log(`❌ Dia inválido (${day}) para item:`, item);
          }
        });
        
        // Verificar se temos dados válidos
        const totalDays = Object.keys(monthData.dailyData).length;
        const daysWithData = Object.values(monthData.dailyData).filter(day => day.total > 0).length;
        console.log(`📊 Resumo: ${daysWithData} dias com dados de ${totalDays} dias totais`);
        
        setComparativeData({ months: [monthData] });
      }
      
    } catch (err) {
      console.error('❌ Erro ao buscar dados comparativos:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComparativeData();
  }, [filters]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-700 rounded-xl">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <div className="text-gray-600 dark:text-gray-400">Carregando análise comparativa...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64 bg-red-50 dark:bg-red-900/20 rounded-xl">
          <div className="text-center">
            <div className="text-red-600 dark:text-red-400 text-lg font-medium mb-2">Erro ao carregar dados</div>
            <div className="text-red-500 dark:text-red-300 text-sm">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!comparativeData || !comparativeData.months || comparativeData.months.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-700 rounded-xl">
          <div className="text-center">
            <div className="text-gray-600 dark:text-gray-400 text-lg font-medium">Sem dados comparativos</div>
            <div className="text-gray-500 dark:text-gray-500 text-sm mt-1">Nenhum dado encontrado para comparação</div>
          </div>
        </div>
      </div>
    );
  }

  // Preparar dados para o gráfico
  const chartData = [];
  for (let day = 1; day <= 31; day++) {
    const dayData = { day: day };
    
    // Para cada mês, adicionar os dados desse dia
    comparativeData.months.forEach((monthData) => {
      const dayInfo = monthData.dailyData[day];
      dayData[monthData.label] = dayInfo[activeCategory];
    });
    
    chartData.push(dayData);
  }

  console.log('📊 Dados finais do gráfico:', chartData.slice(0, 5)); // Mostrar primeiros 5 dias

  const categoryOptions = [
    { value: 'total', label: 'Total de Corridas', icon: Activity },
    { value: 'concluidas', label: 'Corridas Concluídas', icon: Target },
    { value: 'canceladas', label: 'Corridas Canceladas', icon: Target },
    { value: 'perdidas', label: 'Corridas Perdidas', icon: Target }
  ];

  const activeOption = categoryOptions.find(opt => opt.value === activeCategory);

  return (
    <div className="space-y-8">
      {/* Debug Info */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
        <div className="text-sm text-yellow-800 dark:text-yellow-200">
          <strong>Debug Info:</strong><br/>
          • Período: {filters?.periodo || 'não definido'}<br/>
          • Cidade: {filters?.cidade || 'todas (padrão)'}<br/>
          • Meses carregados: {comparativeData?.months?.length || 0}<br/>
          • Categoria ativa: {activeCategory}<br/>
          {comparativeData?.months?.length > 0 && comparativeData.months.map(month => {
            const totalRides = Object.values(month.dailyData || {}).reduce((sum, day) => sum + (day[activeCategory] || 0), 0);
            return `• ${month.label}: ${totalRides} corridas`;
          }).join(', ')}
        </div>
      </div>

      {/* Controle de Categoria */}
      <div className="flex flex-wrap gap-2 sm:gap-3 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
        {categoryOptions.map(option => (
          <button
            key={option.value}
            onClick={() => setActiveCategory(option.value)}
            className={`
              flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
              ${activeCategory === option.value
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }
            `}
          >
            <option.icon className="w-4 h-4" />
            <span className="hidden sm:inline">{option.label}</span>
          </button>
        ))}
      </div>

      {/* Gráfico Comparativo por Dias do Mês */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              Comparativo por Dia do Mês - {activeOption.label}
            </h3>
          </div>
          <div className="text-xs text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900 px-3 py-1 rounded-lg">
            {comparativeData.months.length} {comparativeData.months.length === 1 ? 'mês' : 'meses'}
          </div>
        </div>
        
        <div className="h-96 bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart 
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="day" 
                tick={{ fontSize: 12, fill: '#666' }}
                label={{ value: 'Dia do Mês', position: 'insideBottom', offset: -10, style: { textAnchor: 'middle' } }}
                domain={[1, 31]}
                type="number"
                ticks={[1, 5, 10, 15, 20, 25, 31]}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#666' }}
                label={{ value: 'Quantidade', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
              />
              <Tooltip 
                formatter={(value, name) => [value?.toLocaleString() || '0', name]}
                labelFormatter={(day) => `Dia ${day}`}
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '13px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend 
                verticalAlign="top" 
                height={36}
                iconType="line"
              />
              
              {/* Renderizar uma linha para cada mês */}
              {comparativeData.months.map((monthData, index) => (
                <Line
                  key={monthData.label}
                  type="monotone"
                  dataKey={monthData.label}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={3}
                  name={monthData.label}
                  dot={{ fill: COLORS[index % COLORS.length], strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: COLORS[index % COLORS.length], strokeWidth: 2 }}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Resumo Estatístico */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
            <Calendar className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            Resumo por Mês
          </h3>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {comparativeData.months.map((monthData, index) => {
            // Calcular total do mês
            const monthTotal = Object.values(monthData.dailyData).reduce((sum, day) => sum + day[activeCategory], 0);
            
            return (
              <div key={monthData.label} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  ></div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{monthData.label}</div>
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                  {monthTotal.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {activeOption.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ComparativeChart;