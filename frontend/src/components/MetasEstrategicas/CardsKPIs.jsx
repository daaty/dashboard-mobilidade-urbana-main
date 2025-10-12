import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Target, DollarSign, Users, Car } from 'lucide-react';

const CardsKPIs = ({ periodoMeses = 3 }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [kpis, setKpis] = useState({
    totalCorridas: { meta: 0, realizado: 0, percentual: 0 },
    totalReceita: { meta: 0, realizado: 0, percentual: 0 },
    totalMotoristas: { meta: 0, realizado: 0, percentual: 0 },
    taxaAtingimentoMedia: 0,
    melhorCidade: { nome: '', percentual: 0 },
    piorCidade: { nome: '', percentual: 0 }
  });

  useEffect(() => {
    fetchKPIs();
  }, [periodoMeses]);

  const fetchKPIs = async () => {
    try {
      setLoading(true);
      setError(null);

      // Buscar dados de todas as cidades
      const cidades = [
        { id: 1, nome: 'Peixoto de Azevedo' },
        { id: 2, nome: 'Nova Monte Verde' },
        { id: 3, nome: 'Matupá' },
        { id: 4, nome: 'Guarantã do Norte' },
        { id: 5, nome: 'Nova Bandeirantes' }
      ];

      let totalMetaCorridas = 0;
      let totalRealizadoCorridas = 0;
      let totalMetaReceita = 0;
      let totalRealizadoReceita = 0;
      let totalMetaMotoristas = 0;
      let totalRealizadoMotoristas = 0;
      let cidadesComDados = 0;
      let melhorPercentual = 0;
      let piorPercentual = 100;
      let melhorCidadeNome = '';
      let piorCidadeNome = '';

      for (const cidade of cidades) {
        try {
          const response = await axios.get(`http://localhost:8000/api/metas-estrategicas/consolidado/${cidade.id}`);
          
          if (response.data.success && response.data.metas && response.data.metas.length > 0) {
            const metasPeriodo = response.data.metas.find(m => m.periodo_meses === periodoMeses);
            
            if (metasPeriodo) {
              cidadesComDados++;

              // Acumular totais
              totalMetaCorridas += metasPeriodo.metas?.corridas || 0;
              totalRealizadoCorridas += metasPeriodo.resultados?.corridas || 0;
              totalMetaReceita += metasPeriodo.metas?.receita || 0;
              totalRealizadoReceita += metasPeriodo.resultados?.receita || 0;
              totalMetaMotoristas += metasPeriodo.metas?.motoristas || 0;
              totalRealizadoMotoristas += metasPeriodo.resultados?.motoristas || 0;

              // Calcular percentual da cidade
              const metaCorridas = metasPeriodo.metas?.corridas || 0;
              const realizadoCorridas = metasPeriodo.resultados?.corridas || 0;
              const percentualCidade = metaCorridas > 0 ? (realizadoCorridas / metaCorridas) * 100 : 0;

              // Atualizar melhor e pior cidade
              if (percentualCidade > melhorPercentual) {
                melhorPercentual = percentualCidade;
                melhorCidadeNome = response.data.cidade_nome;
              }
              if (percentualCidade < piorPercentual && percentualCidade > 0) {
                piorPercentual = percentualCidade;
                piorCidadeNome = response.data.cidade_nome;
              }
            }
          }
        } catch (err) {
          console.warn(`Erro ao buscar cidade ${cidade.nome}:`, err.message);
        }
      }

      // Calcular percentuais gerais
      const percentualCorridas = totalMetaCorridas > 0 
        ? (totalRealizadoCorridas / totalMetaCorridas) * 100 
        : 0;
      
      const percentualReceita = totalMetaReceita > 0 
        ? (totalRealizadoReceita / totalMetaReceita) * 100 
        : 0;
      
      const percentualMotoristas = totalMetaMotoristas > 0 
        ? (totalRealizadoMotoristas / totalMetaMotoristas) * 100 
        : 0;

      // Taxa de atingimento média (média dos 3 percentuais)
      const taxaAtingimentoMedia = (percentualCorridas + percentualReceita + percentualMotoristas) / 3;

      setKpis({
        totalCorridas: {
          meta: totalMetaCorridas,
          realizado: totalRealizadoCorridas,
          percentual: percentualCorridas
        },
        totalReceita: {
          meta: totalMetaReceita,
          realizado: totalRealizadoReceita,
          percentual: percentualReceita
        },
        totalMotoristas: {
          meta: totalMetaMotoristas,
          realizado: totalRealizadoMotoristas,
          percentual: percentualMotoristas
        },
        taxaAtingimentoMedia,
        melhorCidade: {
          nome: melhorCidadeNome,
          percentual: melhorPercentual
        },
        piorCidade: {
          nome: piorCidadeNome,
          percentual: piorPercentual
        },
        cidadesComDados
      });

      setLoading(false);
    } catch (err) {
      console.error('Erro ao buscar KPIs:', err);
      setError('Erro ao carregar KPIs. Verifique se o backend está rodando.');
      setLoading(false);
    }
  };

  const getCorPorPercentual = (percentual) => {
    if (percentual >= 100) return 'text-green-600 bg-green-50 border-green-200';
    if (percentual >= 80) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (percentual >= 50) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getTendenciaIcone = (percentual) => {
    if (percentual >= 80) {
      return <TrendingUp className="w-6 h-6 text-green-500" />;
    }
    return <TrendingDown className="w-6 h-6 text-red-500" />;
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white rounded-lg shadow-lg p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600 font-medium">❌ {error}</p>
        <button
          onClick={fetchKPIs}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Cards principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Card: Total de Corridas */}
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <Car className="w-8 h-8 text-blue-500 mr-2" />
              <h3 className="text-sm font-medium text-gray-600">Total de Corridas</h3>
            </div>
            {getTendenciaIcone(kpis.totalCorridas.percentual)}
          </div>
          <p className="text-3xl font-bold text-gray-800 mb-2">
            {kpis.totalCorridas.realizado.toLocaleString('pt-BR')}
          </p>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">
              Meta: {kpis.totalCorridas.meta.toLocaleString('pt-BR')}
            </span>
            <span className={`px-2 py-1 rounded-full font-medium ${getCorPorPercentual(kpis.totalCorridas.percentual)}`}>
              {kpis.totalCorridas.percentual.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Card: Receita Total */}
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <DollarSign className="w-8 h-8 text-green-500 mr-2" />
              <h3 className="text-sm font-medium text-gray-600">Receita Total</h3>
            </div>
            {getTendenciaIcone(kpis.totalReceita.percentual)}
          </div>
          <p className="text-3xl font-bold text-gray-800 mb-2">
            R$ {kpis.totalReceita.realizado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </p>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">
              Meta: R$ {kpis.totalReceita.meta.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </span>
            <span className={`px-2 py-1 rounded-full font-medium ${getCorPorPercentual(kpis.totalReceita.percentual)}`}>
              {kpis.totalReceita.percentual.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Card: Motoristas Ativos */}
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-purple-500 mr-2" />
              <h3 className="text-sm font-medium text-gray-600">Motoristas Ativos</h3>
            </div>
            {getTendenciaIcone(kpis.totalMotoristas.percentual)}
          </div>
          <p className="text-3xl font-bold text-gray-800 mb-2">
            {kpis.totalMotoristas.realizado.toLocaleString('pt-BR')}
          </p>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">
              Meta: {kpis.totalMotoristas.meta.toLocaleString('pt-BR')}
            </span>
            <span className={`px-2 py-1 rounded-full font-medium ${getCorPorPercentual(kpis.totalMotoristas.percentual)}`}>
              {kpis.totalMotoristas.percentual.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Card: Taxa de Atingimento Média */}
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <Target className="w-8 h-8 text-yellow-500 mr-2" />
              <h3 className="text-sm font-medium text-gray-600">Atingimento Médio</h3>
            </div>
            {getTendenciaIcone(kpis.taxaAtingimentoMedia)}
          </div>
          <p className="text-3xl font-bold text-gray-800 mb-2">
            {kpis.taxaAtingimentoMedia.toFixed(1)}%
          </p>
          <div className="text-sm text-gray-500">
            Média de todas as métricas
          </div>
        </div>
      </div>

      {/* Cards secundários - Melhor e Pior Cidade */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Melhor Cidade */}
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg shadow-md p-6 border border-green-200">
          <div className="flex items-center mb-3">
            <div className="bg-green-500 rounded-full p-2 mr-3">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-lg font-bold text-green-800">🏆 Melhor Desempenho</h3>
          </div>
          <p className="text-2xl font-bold text-gray-800 mb-1">
            {kpis.melhorCidade.nome || 'N/A'}
          </p>
          <p className="text-green-600 font-semibold">
            {kpis.melhorCidade.percentual.toFixed(1)}% de atingimento
          </p>
        </div>

        {/* Pior Cidade */}
        <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg shadow-md p-6 border border-red-200">
          <div className="flex items-center mb-3">
            <div className="bg-red-500 rounded-full p-2 mr-3">
              <TrendingDown className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-lg font-bold text-red-800">⚠️ Necessita Atenção</h3>
          </div>
          <p className="text-2xl font-bold text-gray-800 mb-1">
            {kpis.piorCidade.nome || 'N/A'}
          </p>
          <p className="text-red-600 font-semibold">
            {kpis.piorCidade.percentual.toFixed(1)}% de atingimento
          </p>
        </div>
      </div>

      {/* Informação adicional */}
      <div className="mt-4 text-center text-sm text-gray-500">
        Período: {periodoMeses} {periodoMeses === 1 ? 'mês' : 'meses'} | 
        {kpis.cidadesComDados} {kpis.cidadesComDados === 1 ? 'cidade' : 'cidades'} com dados
      </div>
    </div>
  );
};

export default CardsKPIs;
