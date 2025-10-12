import { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 
               (import.meta.env.PROD 
                 ? 'https://fastapi.urbanmt.com.br' 
                 : 'http://localhost:8000');

/**
 * Hook customizado para buscar dados de performance de motoristas
 * Conecta aos endpoints reais /api/analytics/performance/*
 * Com AbortController para evitar race conditions no React Strict Mode
 * 
 * @param {string} period - Período de análise: 'today', '7_days', '30_days', '90_days'
 * @returns {object} { data, loading, error, refetch }
 */
export function usePerformanceData(period = '7_days') {
  const [data, setData] = useState({
    overview: null,
    trends: [],
    achievements: [],
    alerts: [],
    predictions: [],
    detailedMetrics: []
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refetchCounter, setRefetchCounter] = useState(0);

  useEffect(() => {
    // AbortController para cancelar requisições ao desmontar (React Strict Mode)
    const abortController = new AbortController();
    let isMounted = true;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log(`🔄 [${period}] Iniciando busca de dados de performance`);

        // Fetch com AbortController (SEM timeout artificial)
        const fetchData = async (endpoint, name) => {
          const url = `${API_URL}/api/analytics/performance/${endpoint}`;
          console.log(`🔗 Buscando ${name}:`, url);
          
          try {
            const response = await fetch(url, {
              signal: abortController.signal,
              headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const json = await response.json();
            console.log(`✅ ${name} carregado:`, json);
            return { status: 'fulfilled', value: json };
          } catch (err) {
            if (err.name === 'AbortError') {
              console.log(`🚫 ${name} cancelado (componente desmontado)`);
              return { status: 'rejected', reason: err };
            }
            console.error(`❌ ${name} falhou:`, err.message);
            return { status: 'rejected', reason: err };
          }
        };

        // Buscar todos os endpoints em paralelo
        const [overview, trends, achievements, alerts, predictions, detailedMetrics] = await Promise.all([
          fetchData(`overview?period=${period}`, 'Overview'),
          fetchData(`trends?period=${period}`, 'Trends'),
          fetchData(`achievements`, 'Achievements'),
          fetchData(`alerts`, 'Alerts'),
          fetchData(`predictions`, 'Predictions'),
          fetchData(`detailed-metrics?period=${period}`, 'Detailed Metrics')
        ]);

        // Se o componente foi desmontado durante o fetch, não atualizar estado
        if (!isMounted || abortController.signal.aborted) {
          console.log('🚫 Componente desmontado, ignorando dados');
          return;
        }

        // Extrair dados com fallbacks
        const newData = {
          overview: overview.status === 'fulfilled' ? overview.value?.data : null,
          trends: trends.status === 'fulfilled' ? (trends.value?.trends || trends.value?.data || []) : [],
          achievements: achievements.status === 'fulfilled' ? (achievements.value?.achievements || achievements.value?.data || []) : [],
          alerts: alerts.status === 'fulfilled' ? (alerts.value?.alerts || alerts.value?.data || []) : [],
          predictions: predictions.status === 'fulfilled' ? (predictions.value?.predictions || predictions.value?.data || []) : [],
          detailedMetrics: detailedMetrics.status === 'fulfilled' ? (detailedMetrics.value?.metrics || detailedMetrics.value?.data || []) : []
        };

        console.log('📊 Dados extraídos:', {
          overview: newData.overview ? 'OK' : 'NULL',
          trends: `${newData.trends.length} items`,
          achievements: `${newData.achievements.length} items`,
          alerts: `${newData.alerts.length} items`,
          predictions: `${newData.predictions.length} items`,
          detailedMetrics: `${newData.detailedMetrics.length} items`
        });

        setData(newData);
        setLoading(false);

      } catch (err) {
        if (!isMounted || abortController.signal.aborted) {
          console.log('🚫 Erro ignorado (componente desmontado)');
          return;
        }
        console.error('❌ Erro geral ao carregar dados:', err);
        setError(err.message || 'Erro ao carregar dados');
        setLoading(false);
      }
    };

    loadData();

    // Cleanup: cancelar requisições pendentes ao desmontar
    return () => {
      console.log('🧹 Limpando requisições pendentes...');
      isMounted = false;
      abortController.abort();
    };
  }, [period, refetchCounter]);

  // Função para forçar um refetch
  const refetch = () => {
    console.log('🔄 Refetch solicitado');
    setRefetchCounter(prev => prev + 1);
  };

  return { data, loading, error, refetch };
}
