import { useState, useEffect, useCallback } from 'react';

/**
 * Hook para buscar dados de motoristas por cidade
 * Integra com API /api/drivers/list (MESMO ENDPOINT DA ABA MOTORISTAS)
 * 
 * @param {string} cidade - Nome da cidade
 * @param {string} period - Período de análise (não usado, mantido para compatibilidade)
 * @param {boolean} autoRefresh - Ativar polling automático (5 minutos)
 * @returns {Object} { data, loading, error, refresh, hasData, isEmpty, percentualAtivos }
 */
export const useDriversByCidade = (cidade = 'all', period = '3_months', autoRefresh = false) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  const fetchDrivers = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      console.log(`[useDriversByCidade] Buscando dados: cidade=${cidade}, period=${period}`);
      
      // USAR MESMO ENDPOINT DA ABA MOTORISTAS
      const driversResponse = await fetch(
        `${API_URL}/api/drivers/list?city=${encodeURIComponent(cidade)}&limit=1000`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!driversResponse.ok) {
        throw new Error(`HTTP ${driversResponse.status}: Erro ao buscar motoristas`);
      }
      
      const driversData = await driversResponse.json();
      
      // Validar estrutura da resposta
      if (!driversData.success || !driversData.data) {
        throw new Error('Resposta da API inválida');
      }
      
      // Extrair lista de motoristas
      const motoristas = driversData.data.drivers || [];
      const totalMotoristas = driversData.data.total_count || 0;
      
      // Calcular métricas agregadas
      const totalCorridas = motoristas.reduce((sum, m) => sum + (m.total_rides || 0), 0);
      const totalReceita = motoristas.reduce((sum, m) => sum + (m.revenue || 0), 0);
      const totalHorasOnline = motoristas.reduce((sum, m) => sum + (m.hours_online || 0), 0);
      const totalCancelamentos = motoristas.reduce((sum, m) => sum + (m.cancelled_rides || 0), 0);
      
      // Motoristas ativos (com corridas > 0)
      const motoristasAtivos = motoristas.filter(m => (m.total_rides || 0) > 0).length;
      const motoristasInativos = totalMotoristas - motoristasAtivos;
      
      // Motoristas online (status = "active")
      const motoristasOnline = motoristas.filter(m => m.status === 'active').length;
      
      // Calcular rating médio (apenas motoristas com rating > 0)
      const motoristasComRating = motoristas.filter(m => (m.rating || 0) > 0);
      const ratingMedio = motoristasComRating.length > 0
        ? motoristasComRating.reduce((sum, m) => sum + (m.rating || 0), 0) / motoristasComRating.length
        : 0;
      
      // Distribuição por performance
      const performance = {
        excelente: motoristas.filter(m => m.performance_category === 'excellent').length,
        bom: motoristas.filter(m => m.performance_category === 'good').length,
        medio: motoristas.filter(m => m.performance_category === 'average').length,
        abaixo: motoristas.filter(m => m.performance_category === 'below').length,
      };
      
      // Processar dados
      const processedData = {
        cidade: cidade,
        periodo: period,
        
        // Contadores principais
        total_motoristas: totalMotoristas,
        motoristas_ativos: motoristasAtivos,
        motoristas_inativos: motoristasInativos,
        motoristas_online: motoristasOnline,
        
        // Métricas de corridas
        total_corridas: totalCorridas,
        total_cancelamentos: totalCancelamentos,
        media_corridas_motorista: totalMotoristas > 0 ? (totalCorridas / totalMotoristas).toFixed(1) : 0,
        
        // Métricas financeiras
        total_receita: totalReceita,
        receita_media_motorista: totalMotoristas > 0 ? (totalReceita / totalMotoristas).toFixed(2) : 0,
        receita_por_corrida: totalCorridas > 0 ? (totalReceita / totalCorridas).toFixed(2) : 0,
        
        // Métricas de qualidade
        rating_medio: ratingMedio.toFixed(2),
        horas_online_total: totalHorasOnline,
        horas_online_media: totalMotoristas > 0 ? (totalHorasOnline / totalMotoristas).toFixed(1) : 0,
        
        // Métricas de performance
        taxa_ativacao: totalMotoristas > 0 ? ((motoristasAtivos / totalMotoristas) * 100).toFixed(1) : 0,
        taxa_cancelamento: totalCorridas > 0 ? ((totalCancelamentos / totalCorridas) * 100).toFixed(1) : 0,
        taxa_conclusao: totalCorridas > 0 ? (((totalCorridas - totalCancelamentos) / totalCorridas) * 100).toFixed(1) : 100,
        
        // Distribuição por performance
        performance: performance,
        
        // Lista completa de motoristas
        motoristas: motoristas,
        
        // Metadados
        ultima_atualizacao: new Date().toISOString(),
        raw_data: driversData, // Dados brutos para debug
      };
      
      console.log(`[useDriversByCidade] ✅ Dados carregados:`, {
        cidade: processedData.cidade,
        total: processedData.total_motoristas,
        ativos: processedData.motoristas_ativos,
        online: processedData.motoristas_online,
        total_corridas: processedData.total_corridas,
        receita_total: processedData.total_receita,
        rating_medio: processedData.rating_medio
      });
      
      setData(processedData);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error('[useDriversByCidade] ❌ Erro:', err);
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [cidade, period]);
  
  // Efeito inicial: buscar dados ao montar ou quando mudar cidade/período
  useEffect(() => {
    fetchDrivers();
  }, [fetchDrivers]);
  
  // Efeito de polling: atualizar automaticamente a cada 5 minutos
  useEffect(() => {
    if (!autoRefresh) return;
    
    console.log('[useDriversByCidade] 🔄 Auto-refresh ativado (5 minutos)');
    
    const interval = setInterval(() => {
      console.log('[useDriversByCidade] 🔄 Atualizando dados automaticamente...');
      fetchDrivers();
    }, 5 * 60 * 1000); // 5 minutos
    
    return () => {
      console.log('[useDriversByCidade] 🛑 Auto-refresh desativado');
      clearInterval(interval);
    };
  }, [autoRefresh, fetchDrivers]);
  
  return {
    data,
    loading,
    error,
    lastUpdate,
    refresh: fetchDrivers,
    
    // Helpers computados
    hasData: data !== null && !error,
    isEmpty: data !== null && data.total_motoristas === 0,
    percentualAtivos: data 
      ? ((data.motoristas_ativos / data.total_motoristas) * 100).toFixed(1)
      : 0,
  };
};

export default useDriversByCidade;
