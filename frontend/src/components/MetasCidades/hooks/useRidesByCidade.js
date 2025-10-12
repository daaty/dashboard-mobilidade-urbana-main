import { useState, useEffect, useCallback } from 'react';

/**
 * Hook para buscar dados de corridas por cidade
 * Integra com API /api/drivers/kpis (que contém dados de corridas)
 * 
 * @param {string} cidade - Nome da cidade ('all' para todas)
 * @param {string} period - Período de análise (7_days, 30_days, 3_months)
 * @param {boolean} autoRefresh - Ativar polling automático (5 minutos)
 * @returns {Object} { data, loading, error, refresh }
 */
export const useRidesByCidade = (cidade = 'all', period = '3_months', autoRefresh = false) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  const fetchRides = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      console.log(`[useRidesByCidade] Buscando dados: cidade=${cidade}, period=${period}`);
      
      // Buscar KPIs que incluem dados de corridas
      const response = await fetch(
        `${API_URL}/api/drivers/kpis?period=${period}&city=${encodeURIComponent(cidade)}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Erro ao buscar dados de corridas`);
      }
      
      const kpisData = await response.json();
      
      // Validar estrutura
      if (!kpisData.success || !kpisData.data) {
        throw new Error('Resposta da API inválida');
      }
      
      // Processar dados de corridas
      const processedData = {
        cidade: cidade,
        periodo: period,
        
        // Contadores principais
        total_corridas: kpisData.data.total_rides || 0,
        corridas_concluidas: kpisData.data.total_rides_completed || 0,
        corridas_canceladas: kpisData.data.cancelled_rides || 0,
        
        // Métricas financeiras
        receita_estimada: kpisData.data.total_revenue || 0,
        receita_por_corrida: kpisData.data.total_rides_completed > 0
          ? (kpisData.data.total_revenue / kpisData.data.total_rides_completed).toFixed(2)
          : 0,
        receita_por_hora: kpisData.data.revenue_per_hour || 0,
        
        // Métricas operacionais
        distancia_total: kpisData.data.total_distance || 0,
        km_por_corrida: kpisData.data.km_per_ride || 0,
        corridas_por_motorista: kpisData.data.avg_rides_per_driver || 0,
        
        // Taxas de eficiência
        taxa_conclusao: kpisData.data.completion_rate || 0,
        taxa_cancelamento: kpisData.data.cancellation_rate || 0,
        tempo_resposta_medio: kpisData.data.avg_response_time || 0,
        corridas_perdidas: kpisData.data.lost_rides || 0,
        
        // Período
        periodo_dias: kpisData.data.periodo_dias || 90,
        
        // Metadados
        ultima_atualizacao: new Date().toISOString(),
        raw_data: kpisData.data,
      };
      
      console.log(`[useRidesByCidade] ✅ Dados carregados:`, {
        total: processedData.total_corridas,
        concluidas: processedData.corridas_concluidas,
        receita: processedData.receita_estimada
      });
      
      setData(processedData);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error('[useRidesByCidade] ❌ Erro:', err);
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [cidade, period]);
  
  // Efeito inicial
  useEffect(() => {
    fetchRides();
  }, [fetchRides]);
  
  // Polling automático (5 minutos)
  useEffect(() => {
    if (!autoRefresh) return;
    
    console.log('[useRidesByCidade] 🔄 Auto-refresh ativado (5 minutos)');
    
    const interval = setInterval(() => {
      console.log('[useRidesByCidade] 🔄 Atualizando dados automaticamente...');
      fetchRides();
    }, 5 * 60 * 1000);
    
    return () => {
      console.log('[useRidesByCidade] 🛑 Auto-refresh desativado');
      clearInterval(interval);
    };
  }, [autoRefresh, fetchRides]);
  
  return {
    data,
    loading,
    error,
    lastUpdate,
    refresh: fetchRides,
    
    // Helpers computados
    hasData: data !== null && !error,
    isEmpty: data !== null && data.total_corridas === 0,
    taxaSucesso: data
      ? ((data.corridas_concluidas / data.total_corridas) * 100).toFixed(1)
      : 0,
    receitaMedia: data
      ? (data.receita_estimada / (data.periodo_dias || 1)).toFixed(2)
      : 0,
  };
};

export default useRidesByCidade;
