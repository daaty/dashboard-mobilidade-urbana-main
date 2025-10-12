import { useState, useEffect, useCallback } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 
               (import.meta.env.PROD 
                 ? 'https://fastapi.urbanmt.com.br' 
                 : 'http://localhost:8000');

/**
 * Hook customizado para buscar dados de performance de motoristas
 * Conecta aos endpoints reais /api/analytics/performance/*
 * 
 * @param {string} period - Período de análise: 'today', '7_days', '30_days', '90_days'
 * @returns {object} { data, loading, error, refetch }
 */
export function usePerformanceData(period = '7_days') {
  const [data, setData] = useState({
    overview: null,
    trends: null,
    achievements: null,
    alerts: null,
    predictions: null,
    detailedMetrics: null
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log(`🔄 Buscando dados de performance para período: ${period}`);
      console.log(`🌐 API URL: ${API_URL}`);

      // Helper para criar fetch com timeout e tratamento de erro
      const fetchWithTimeout = (url, timeout = 15000) => {
        console.log(`🔗 Buscando: ${url}`);
        return Promise.race([
          fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }).then(r => {
            console.log(`📡 Resposta de ${url}: Status ${r.status}`);
            return r;
          }).catch(err => {
            console.error(`❌ Erro de rede em ${url}:`, err);
            throw err;
          }),
          new Promise((_, reject) => 
            setTimeout(() => {
              console.error(`⏱️ Timeout em ${url} após ${timeout}ms`);
              reject(new Error(`Timeout após ${timeout}ms`));
            }, timeout)
          )
        ]);
      };

      // Buscar todos os endpoints em paralelo com Promise.allSettled
      // para permitir que alguns falhem sem quebrar toda a interface
      const results = await Promise.allSettled([
        fetchWithTimeout(`${API_URL}/api/analytics/performance/overview?period=${period}`, 15000)
          .then(r => {
            console.log('📥 Overview response status:', r.status, 'OK:', r.ok);
            if (!r.ok) throw new Error(`Erro ao buscar overview: ${r.status}`);
            return r.json();
          }),
        fetchWithTimeout(`${API_URL}/api/analytics/performance/trends?period=${period}`, 15000)
          .then(r => {
            console.log('📥 Trends response status:', r.status, 'OK:', r.ok);
            if (!r.ok) throw new Error(`Erro ao buscar trends: ${r.status}`);
            return r.json();
          }),
        fetchWithTimeout(`${API_URL}/api/analytics/performance/achievements`, 15000)
          .then(r => {
            console.log('📥 Achievements response status:', r.status, 'OK:', r.ok);
            if (!r.ok) throw new Error(`Erro ao buscar achievements: ${r.status}`);
            return r.json();
          }),
        fetchWithTimeout(`${API_URL}/api/analytics/performance/alerts`, 15000)
          .then(r => {
            console.log('📥 Alerts response status:', r.status, 'OK:', r.ok);
            if (!r.ok) throw new Error(`Erro ao buscar alerts: ${r.status}`);
            return r.json();
          }),
        fetchWithTimeout(`${API_URL}/api/analytics/performance/predictions`, 15000)
          .then(r => {
            console.log('📥 Predictions response status:', r.status, 'OK:', r.ok);
            if (!r.ok) throw new Error(`Erro ao buscar predictions: ${r.status}`);
            return r.json();
          }),
        fetchWithTimeout(`${API_URL}/api/analytics/performance/detailed-metrics?period=${period}`, 15000)
          .then(r => {
            console.log('📥 Detailed-metrics response status:', r.status, 'OK:', r.ok);
            if (!r.ok) throw new Error(`Erro ao buscar detailed-metrics: ${r.status}`);
            return r.json();
          })
        ]);

      // Extrair os valores ou usar fallbacks
      const [overview, trends, achievements, alerts, predictions, detailed] = results.map((result, index) => {
        const names = ['overview', 'trends', 'achievements', 'alerts', 'predictions', 'detailed-metrics'];
        if (result.status === 'fulfilled') {
          console.log(`✅ ${names[index]} carregado com sucesso:`, result.value);
          return result.value;
        } else {
          console.error(`❌ Falha ao carregar ${names[index]}:`, result.reason?.message || result.reason);
          console.error(`❌ Detalhes do erro ${names[index]}:`, {
            name: result.reason?.name,
            message: result.reason?.message,
            stack: result.reason?.stack?.split('\n').slice(0, 3).join('\n')
          });
          return { success: true, data: null, [names[index]]: [] };
        }
      });

      // Validar apenas o endpoint crítico (overview)
      if (!overview?.success) {
        console.warn('⚠️ Overview não disponível, usando dados padrão');
      }

      const finalData = {
        overview: overview?.data || {},
        trends: trends?.trends || trends?.data || [],
        achievements: achievements?.achievements || achievements?.data || [],
        alerts: alerts?.alerts || alerts?.data || [],
        predictions: predictions?.predictions || predictions?.data || [],
        detailedMetrics: detailed?.metrics || detailed?.data || []
      };

      console.log('📊 Dados finais extraídos:', {
        overview: finalData.overview,
        trendsCount: finalData.trends?.length,
        achievementsCount: finalData.achievements?.length,
        alertsCount: finalData.alerts?.length,
        predictionsCount: finalData.predictions?.length,
        metricsCount: finalData.detailedMetrics?.length
      });

      setData(finalData);

      console.log('✅ Dados de performance definidos no estado!');

    } catch (err) {
      console.error('❌ Erro ao buscar dados de performance:', err);
      setError(err.message);
      
      // Fallback para dados vazios em caso de erro
      setData({
        overview: null,
        trends: [],
        achievements: [],
        alerts: [],
        predictions: [],
        detailedMetrics: []
      });
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchAllData 
  };
}
