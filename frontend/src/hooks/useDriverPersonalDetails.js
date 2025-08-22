// Hook para dados pessoais detalhados dos motoristas da tabela driver_personal_details
import { useState, useEffect } from 'react';

export const useDriverPersonalDetails = () => {
  const [personalData, setPersonalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [cities, setCities] = useState([]);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Buscar dados pessoais dos motoristas com paginação
  const fetchPersonalDetails = async (page = 1, limit = 50, city = null) => {
    try {
      const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
      if (city) params.append('city', city);

      const response = await fetch(`${API_URL}/api/drivers/personal-details?${params}`);
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log('🔍 Dados pessoais dos motoristas:', data);
      
      return data;
    } catch (err) {
      console.error('Erro ao buscar dados pessoais:', err);
      throw err;
    }
  };

  // Buscar resumo geral
  const fetchSummary = async (city = null) => {
    try {
      const params = new URLSearchParams();
      if (city) params.append('city', city);

      const response = await fetch(`${API_URL}/api/drivers/summary?${params}`);
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log('📊 Resumo dos motoristas:', data);
      
      return data;
    } catch (err) {
      console.error('Erro ao buscar resumo:', err);
      throw err;
    }
  };

  // Buscar cidades disponíveis
  const fetchCities = async () => {
    try {
      const response = await fetch(`${API_URL}/api/drivers/cities`);
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log('🏙️ Cidades disponíveis:', data);
      
      return data;
    } catch (err) {
      console.error('Erro ao buscar cidades:', err);
      throw err;
    }
  };

  // Buscar analytics detalhadas de um motorista específico
  const fetchDriverAnalytics = async (driverId) => {
    try {
      const response = await fetch(`${API_URL}/api/drivers/analytics/${driverId}`);
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log(`📈 Analytics do motorista ${driverId}:`, data);
      
      return data;
    } catch (err) {
      console.error(`Erro ao buscar analytics do motorista ${driverId}:`, err);
      throw err;
    }
  };

  // Carregar todos os dados iniciais
  const loadAllData = async (city = null) => {
    try {
      setLoading(true);
      setError(null);

      // Buscar dados em paralelo
      const [personalDetailsResult, summaryResult, citiesResult] = await Promise.all([
        fetchPersonalDetails(1, 100, city), // Buscar primeiros 100 motoristas
        fetchSummary(city),
        fetchCities()
      ]);

      // Processar dados pessoais
      const driversWithDetails = personalDetailsResult.drivers.map(driver => ({
        ...driver,
        // Adicionar campos calculados
        completion_rate: driver.total_rides > 0 ? 
          ((driver.total_rides - (driver.cancelled_rides || 0)) / driver.total_rides * 100) : 100,
        rides_per_day: driver.active_days > 0 ? 
          (driver.total_rides / driver.active_days) : 0,
        earnings_per_ride: driver.total_rides > 0 ? 
          (driver.total_earnings / driver.total_rides) : 0,
        // Status baseado em atividade recente
        status: driver.last_activity && 
          new Date(driver.last_activity) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) ? 
          'active' : 'inactive',
        // Classificação de performance baseada no rating
        performance_level: driver.average_rating >= 4.5 ? 'excellent' :
          driver.average_rating >= 4.0 ? 'good' :
          driver.average_rating >= 3.5 ? 'average' : 'below'
      }));

      setPersonalData(driversWithDetails);
      setSummary(summaryResult);
      setCities(citiesResult);

      console.log('✅ Dados carregados com sucesso:', {
        totalDrivers: personalDetailsResult.total_count,
        driversLoaded: driversWithDetails.length,
        summary: summaryResult,
        cities: citiesResult.length
      });

    } catch (err) {
      setError(err.message);
      console.error('Erro ao carregar dados:', err);
    } finally {
      setLoading(false);
    }
  };

  // Calcular métricas detalhadas baseadas nos dados reais
  const calculateDetailedMetrics = () => {
    if (!personalData.length || !summary) return null;

    // Métricas de performance
    const performanceDistribution = {
      excellent: personalData.filter(d => d.performance_level === 'excellent').length,
      good: personalData.filter(d => d.performance_level === 'good').length,
      average: personalData.filter(d => d.performance_level === 'average').length,
      below: personalData.filter(d => d.performance_level === 'below').length
    };

    // Análise de receita
    const revenueAnalysis = {
      total_earnings: summary.total_earnings,
      avg_earnings_per_driver: personalData.length > 0 ? 
        summary.total_earnings / personalData.length : 0,
      top_earners: personalData
        .filter(d => d.total_earnings > 0)
        .sort((a, b) => b.total_earnings - a.total_earnings)
        .slice(0, 10),
      earnings_distribution: {
        high: personalData.filter(d => d.total_earnings > 1000).length,
        medium: personalData.filter(d => d.total_earnings >= 500 && d.total_earnings <= 1000).length,
        low: personalData.filter(d => d.total_earnings < 500).length
      }
    };

    // Análise temporal
    const temporalAnalysis = {
      drivers_with_recent_activity: personalData.filter(d => 
        d.last_activity && new Date(d.last_activity) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      ).length,
      avg_rides_per_driver: personalData.length > 0 ? 
        personalData.reduce((sum, d) => sum + d.total_rides, 0) / personalData.length : 0,
      most_active_drivers: personalData
        .filter(d => d.total_rides > 0)
        .sort((a, b) => b.total_rides - a.total_rides)
        .slice(0, 10)
    };

    // Análise de qualidade
    const qualityMetrics = {
      avg_rating: summary.average_rating,
      high_rated_drivers: personalData.filter(d => d.average_rating && d.average_rating >= 4.5).length,
      low_rated_drivers: personalData.filter(d => d.average_rating && d.average_rating < 3.5).length,
      unrated_drivers: personalData.filter(d => !d.average_rating).length
    };

    return {
      performance: performanceDistribution,
      revenue: revenueAnalysis,
      temporal: temporalAnalysis,
      quality: qualityMetrics,
      raw_summary: summary
    };
  };

  // Filtrar motoristas por critérios
  const filterDrivers = (filters = {}) => {
    let filtered = [...personalData];

    if (filters.city) {
      filtered = filtered.filter(d => d.city.toLowerCase().includes(filters.city.toLowerCase()));
    }

    if (filters.status) {
      filtered = filtered.filter(d => d.status === filters.status);
    }

    if (filters.performance) {
      filtered = filtered.filter(d => d.performance_level === filters.performance);
    }

    if (filters.min_rides) {
      filtered = filtered.filter(d => d.total_rides >= filters.min_rides);
    }

    if (filters.min_earnings) {
      filtered = filtered.filter(d => d.total_earnings >= filters.min_earnings);
    }

    if (filters.min_rating) {
      filtered = filtered.filter(d => d.average_rating && d.average_rating >= filters.min_rating);
    }

    return filtered;
  };

  // Obter top motoristas por critério
  const getTopDrivers = (criteria = 'total_rides', limit = 10) => {
    const validCriteria = ['total_rides', 'total_earnings', 'average_rating'];
    const sortBy = validCriteria.includes(criteria) ? criteria : 'total_rides';

    return personalData
      .filter(d => d[sortBy] > 0)
      .sort((a, b) => {
        const aValue = a[sortBy] || 0;
        const bValue = b[sortBy] || 0;
        return bValue - aValue;
      })
      .slice(0, limit);
  };

  // Carregar dados na inicialização
  useEffect(() => {
    loadAllData();
  }, []);

  return {
    // Dados
    personalData,
    summary,
    cities,
    loading,
    error,
    
    // Funções
    fetchPersonalDetails,
    fetchSummary,
    fetchCities,
    fetchDriverAnalytics,
    loadAllData,
    calculateDetailedMetrics,
    filterDrivers,
    getTopDrivers,
    
    // Métricas calculadas
    detailedMetrics: calculateDetailedMetrics()
  };
};
