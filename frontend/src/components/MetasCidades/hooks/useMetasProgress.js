import { useState, useEffect, useCallback } from 'react';
import { PLANO_EXECUCAO } from '../../../constants/cidadesConstants.js';

/**
 * Hook Master que combina todos os dados
 * Integra: Plano Estático + Motoristas + Corridas + Financeiro
 * 
 * Este é o hook principal que deve ser usado nos componentes
 * para ter acesso a todos os dados integrados de uma fase
 * 
 * @param {string} fase - Nome da fase ('Fase 1', 'Fase 2', 'Fase 3')
 * @param {boolean} autoRefresh - Ativar polling automático (5 minutos)
 * @returns {Object} { data, loading, error, refresh }
 */
export const useMetasProgress = (fase, autoRefresh = false) => {
  const [consolidatedData, setConsolidatedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Dados do plano estático
  const planoFase = PLANO_EXECUCAO[fase];
  
  const fetchAllData = useCallback(async () => {
    if (!planoFase) {
      setError(`Fase "${fase}" não encontrada no plano de execução`);
      setLoading(false);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      console.log(`[useMetasProgress] 🚀 Iniciando busca de dados para ${fase}`);
      console.log(`[useMetasProgress] Cidades: ${planoFase.cidades.join(', ')}`);
      
      // 1. Buscar dados financeiros da fase primeiro
      console.log('[useMetasProgress] 📊 Buscando dados financeiros...');
      
      const financeiroResponse = await fetch(
        `${API_URL}/api/financeiro/overview?periodo=90`
      );
      const financeiroData = financeiroResponse.ok 
        ? await financeiroResponse.json()
        : null;
      
      const campanhasResponse = await fetch(`${API_URL}/api/campanhas`);
      const campanhasData = campanhasResponse.ok
        ? await campanhasResponse.json()
        : [];
      
      // Filtrar campanhas da fase
      const campanhasFase = Array.isArray(campanhasData)
        ? campanhasData.filter(c => c.fase === fase)
        : [];
      
      console.log(`[useMetasProgress] 💰 Campanhas encontradas: ${campanhasFase.length}`);
      
      // 2. Buscar dados reais para cada cidade da fase
      console.log('[useMetasProgress] 🏙️  Buscando dados por cidade...');
      
      const cidadesComDados = await Promise.all(
        planoFase.cidades.map(async (nomeCidade) => {
          try {
            console.log(`  → Processando ${nomeCidade}...`);
            
            // Buscar KPIs da cidade (contém motoristas + corridas)
            const kpisResponse = await fetch(
              `${API_URL}/api/drivers/kpis?period=3_months&city=${encodeURIComponent(nomeCidade)}`
            );
            
            const kpisData = kpisResponse.ok 
              ? await kpisResponse.json()
              : { success: false, data: {} };
            
            const apiData = kpisData.data || {};
            
            // Extrair metas do plano estático
            const metaPart1Motoristas = planoFase.part1?.metas?.[nomeCidade] || 0;
            const metaPart2Corridas = planoFase.part2?.metas?.[nomeCidade] || 0;
            
            // Dados reais da API
            const motoristaRealizados = apiData.total_drivers || 0;
            const corridasRealizadas = apiData.total_rides_completed || 0;
            
            // Calcular progresso percentual
            const progressoPart1 = metaPart1Motoristas > 0 
              ? (motoristaRealizados / metaPart1Motoristas) * 100 
              : 0;
              
            const progressoPart2 = metaPart2Corridas > 0 
              ? (corridasRealizadas / metaPart2Corridas) * 100 
              : 0;
            
            // Determinar status
            const getStatus = (progresso) => {
              if (progresso >= 100) return 'concluido';
              if (progresso >= 70) return 'no_prazo';
              if (progresso >= 40) return 'atencao';
              return 'atrasado';
            };
            
            // Buscar campanhas específicas da cidade
            const campanhasCidade = campanhasFase.filter(c => c.cidade === nomeCidade);
            
            // Calcular orçamento da cidade
            const orcamentoCidade = campanhasCidade.reduce(
              (sum, c) => sum + parseFloat(c.orcamento_previsto || 0),
              0
            );
            
            const gastoCidade = campanhasCidade.reduce(
              (sum, c) => sum + parseFloat(c.custo_real || 0),
              0
            );
            
            console.log(`    ✅ ${nomeCidade}: ${motoristaRealizados}/${metaPart1Motoristas} motoristas, ${corridasRealizadas}/${metaPart2Corridas} corridas`);
            
            return {
              nome: nomeCidade,
              
              // Part 1: Motoristas
              part1: {
                tipo: 'motoristas',
                meta: metaPart1Motoristas,
                realizado: motoristaRealizados,
                progresso: Math.round(progressoPart1 * 10) / 10, // 1 casa decimal
                status: getStatus(progressoPart1),
                ativos: apiData.active_drivers || 0,
                inativos: apiData.inactive_drivers || 0,
                rating_medio: apiData.avg_rating || 0,
              },
              
              // Part 2: Corridas
              part2: {
                tipo: 'corridas',
                meta: metaPart2Corridas,
                realizado: corridasRealizadas,
                progresso: Math.round(progressoPart2 * 10) / 10,
                status: getStatus(progressoPart2),
                canceladas: apiData.cancelled_rides || 0,
                receita: apiData.total_revenue || 0,
                distancia: apiData.total_distance || 0,
              },
              
              // Financeiro da cidade
              financeiro: {
                orcamento: orcamentoCidade,
                gasto: gastoCidade,
                saldo: orcamentoCidade - gastoCidade,
                percentual: orcamentoCidade > 0
                  ? ((gastoCidade / orcamentoCidade) * 100).toFixed(1)
                  : 0,
                campanhas: campanhasCidade.length,
              },
              
              // Dados brutos da API para referência
              dados_api: {
                motoristas: {
                  total: motoristaRealizados,
                  ativos: apiData.active_drivers || 0,
                  rating: apiData.avg_rating || 0,
                },
                corridas: {
                  total: corridasRealizadas,
                  canceladas: apiData.cancelled_rides || 0,
                  receita: apiData.total_revenue || 0,
                },
                ultima_atualizacao: new Date().toISOString(),
              },
            };
          } catch (cityError) {
            console.error(`    ❌ Erro em ${nomeCidade}:`, cityError.message);
            
            // Retornar dados vazios em caso de erro
            return {
              nome: nomeCidade,
              part1: {
                tipo: 'motoristas',
                meta: planoFase.part1?.metas?.[nomeCidade] || 0,
                realizado: 0,
                progresso: 0,
                status: 'erro',
              },
              part2: {
                tipo: 'corridas',
                meta: planoFase.part2?.metas?.[nomeCidade] || 0,
                realizado: 0,
                progresso: 0,
                status: 'erro',
              },
              financeiro: {
                orcamento: 0,
                gasto: 0,
                saldo: 0,
                percentual: 0,
                campanhas: 0,
              },
              erro: cityError.message,
            };
          }
        })
      );
      
      // 3. Calcular totais e estatísticas da fase
      const estatisticas = {
        // Metas totais
        total_motoristas_meta: cidadesComDados.reduce((sum, c) => sum + c.part1.meta, 0),
        total_corridas_meta: cidadesComDados.reduce((sum, c) => sum + c.part2.meta, 0),
        
        // Realizados totais
        total_motoristas_real: cidadesComDados.reduce((sum, c) => sum + c.part1.realizado, 0),
        total_corridas_real: cidadesComDados.reduce((sum, c) => sum + c.part2.realizado, 0),
        
        // Progressos médios
        progresso_medio_motoristas: cidadesComDados.length > 0
          ? cidadesComDados.reduce((sum, c) => sum + c.part1.progresso, 0) / cidadesComDados.length
          : 0,
        progresso_medio_corridas: cidadesComDados.length > 0
          ? cidadesComDados.reduce((sum, c) => sum + c.part2.progresso, 0) / cidadesComDados.length
          : 0,
        
        // Distribuição de status
        cidades_atrasadas: cidadesComDados.filter(
          c => c.part1.status === 'atrasado' || c.part2.status === 'atrasado'
        ).length,
        cidades_no_prazo: cidadesComDados.filter(
          c => c.part1.status === 'no_prazo' || c.part2.status === 'no_prazo'
        ).length,
        cidades_concluidas: cidadesComDados.filter(
          c => c.part1.status === 'concluido' && c.part2.status === 'concluido'
        ).length,
      };
      
      // 4. Calcular orçamento consolidado
      const orcamentoTotal = planoFase.orcamento?.previsto || 0;
      const gastoRealTotal = cidadesComDados.reduce((sum, c) => sum + c.financeiro.gasto, 0);
      
      const orcamento = {
        previsto: orcamentoTotal,
        empenhado: campanhasFase.filter(c => c.status_financeiro === 'empenhado')
          .reduce((sum, c) => sum + parseFloat(c.orcamento_previsto || 0), 0),
        pago: campanhasFase.filter(c => c.status_financeiro === 'pago')
          .reduce((sum, c) => sum + parseFloat(c.custo_real || 0), 0),
        liquidado: campanhasFase.filter(c => c.status_financeiro === 'liquidado')
          .reduce((sum, c) => sum + parseFloat(c.custo_real || 0), 0),
        gasto_real: gastoRealTotal,
        saldo: orcamentoTotal - gastoRealTotal,
        percentual_utilizado: orcamentoTotal > 0
          ? ((gastoRealTotal / orcamentoTotal) * 100).toFixed(1)
          : 0,
      };
      
      // 5. Gerar alertas
      const alertas = gerarAlertas(cidadesComDados, planoFase, orcamento, financeiroData);
      
      // 6. Consolidar tudo
      const consolidated = {
        fase: fase,
        periodo: planoFase.periodo,
        status: planoFase.status,
        cidades: cidadesComDados,
        estatisticas,
        orcamento,
        campanhas: campanhasFase,
        alertas,
        financeiro_raw: financeiroData,
        plano_original: planoFase,
        ultima_atualizacao: new Date().toISOString(),
      };
      
      console.log(`[useMetasProgress] ✅ Dados consolidados:`, {
        cidades: cidadesComDados.length,
        campanhas: campanhasFase.length,
        alertas: alertas.length,
        progresso_motoristas: `${estatisticas.progresso_medio_motoristas.toFixed(1)}%`,
        progresso_corridas: `${estatisticas.progresso_medio_corridas.toFixed(1)}%`,
      });
      
      setConsolidatedData(consolidated);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error('[useMetasProgress] ❌ Erro fatal:', err);
      setError(err.message);
      setConsolidatedData(null);
    } finally {
      setLoading(false);
    }
  }, [fase, planoFase]);
  
  // Efeito inicial
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);
  
  // Polling automático (5 minutos)
  useEffect(() => {
    if (!autoRefresh) return;
    
    console.log('[useMetasProgress] 🔄 Auto-refresh ativado (5 minutos)');
    
    const interval = setInterval(() => {
      console.log('[useMetasProgress] 🔄 Atualizando dados automaticamente...');
      fetchAllData();
    }, 5 * 60 * 1000);
    
    return () => {
      console.log('[useMetasProgress] 🛑 Auto-refresh desativado');
      clearInterval(interval);
    };
  }, [autoRefresh, fetchAllData]);
  
  return {
    data: consolidatedData,
    loading,
    error,
    lastUpdate,
    refresh: fetchAllData,
    
    // Helpers computados
    hasData: consolidatedData !== null && !error,
    isEmpty: consolidatedData !== null && consolidatedData.cidades.length === 0,
    temAlertas: consolidatedData && consolidatedData.alertas.length > 0,
    alertasCriticos: consolidatedData 
      ? consolidatedData.alertas.filter(a => a.nivel === 'danger').length
      : 0,
  };
};

// Função auxiliar para gerar alertas integrados
function gerarAlertas(cidades, plano, orcamento, financeiro) {
  const alertas = [];
  
  // 1. Alertas de progresso de motoristas
  cidades.forEach(cidade => {
    if (cidade.part1.status === 'atrasado') {
      alertas.push({
        tipo: 'progresso',
        subtipo: 'motoristas',
        nivel: 'danger',
        cidade: cidade.nome,
        mensagem: `Meta de motoristas atrasada: ${cidade.part1.progresso.toFixed(1)}% (${cidade.part1.realizado}/${cidade.part1.meta})`,
        icone: '🚗',
        dados: cidade.part1,
      });
    } else if (cidade.part1.status === 'atencao') {
      alertas.push({
        tipo: 'progresso',
        subtipo: 'motoristas',
        nivel: 'warning',
        cidade: cidade.nome,
        mensagem: `Atenção: ${cidade.nome} com ${cidade.part1.progresso.toFixed(1)}% da meta de motoristas`,
        icone: '⚠️',
        dados: cidade.part1,
      });
    }
  });
  
  // 2. Alertas de progresso de corridas
  cidades.forEach(cidade => {
    if (cidade.part2.status === 'atrasado') {
      alertas.push({
        tipo: 'progresso',
        subtipo: 'corridas',
        nivel: 'danger',
        cidade: cidade.nome,
        mensagem: `Meta de corridas atrasada: ${cidade.part2.progresso.toFixed(1)}% (${cidade.part2.realizado}/${cidade.part2.meta})`,
        icone: '📱',
        dados: cidade.part2,
      });
    } else if (cidade.part2.status === 'atencao') {
      alertas.push({
        tipo: 'progresso',
        subtipo: 'corridas',
        nivel: 'warning',
        cidade: cidade.nome,
        mensagem: `Atenção: ${cidade.nome} com ${cidade.part2.progresso.toFixed(1)}% da meta de corridas`,
        icone: '⚠️',
        dados: cidade.part2,
      });
    }
  });
  
  // 3. Alertas orçamentários
  const percentualOrcamento = parseFloat(orcamento.percentual_utilizado);
  
  if (orcamento.saldo < 0) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'danger',
      mensagem: `Orçamento estourado em R$ ${Math.abs(orcamento.saldo).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
      icone: '💸',
      dados: orcamento,
    });
  } else if (percentualOrcamento > 90) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'danger',
      mensagem: `Orçamento crítico: ${percentualOrcamento}% utilizado`,
      icone: '🔴',
      dados: orcamento,
    });
  } else if (percentualOrcamento > 75) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'warning',
      mensagem: `Atenção ao orçamento: ${percentualOrcamento}% utilizado`,
      icone: '⚠️',
      dados: orcamento,
    });
  }
  
  // 4. Alertas de documentação (se tiver dados financeiros)
  if (financeiro) {
    const taxaDoc = financeiro.taxa_documentacao || 0;
    
    if (taxaDoc < 70) {
      alertas.push({
        tipo: 'documentacao',
        nivel: 'warning',
        mensagem: `Taxa de documentação baixa: ${taxaDoc}%`,
        icone: '📄',
        dados: { taxa: taxaDoc },
      });
    }
  }
  
  // 5. Alertas de performance
  cidades.forEach(cidade => {
    // Taxa de cancelamento alta
    if (cidade.part2.canceladas > 0 && cidade.part2.realizado > 0) {
      const taxaCancelamento = (cidade.part2.canceladas / cidade.part2.realizado) * 100;
      
      if (taxaCancelamento > 20) {
        alertas.push({
          tipo: 'performance',
          subtipo: 'cancelamento',
          nivel: 'warning',
          cidade: cidade.nome,
          mensagem: `Alta taxa de cancelamento em ${cidade.nome}: ${taxaCancelamento.toFixed(1)}%`,
          icone: '❌',
          dados: { taxa: taxaCancelamento },
        });
      }
    }
    
    // Rating baixo
    if (cidade.part1.rating_medio > 0 && cidade.part1.rating_medio < 4.0) {
      alertas.push({
        tipo: 'performance',
        subtipo: 'rating',
        nivel: 'warning',
        cidade: cidade.nome,
        mensagem: `Rating médio baixo em ${cidade.nome}: ${cidade.part1.rating_medio.toFixed(1)}/5.0`,
        icone: '⭐',
        dados: { rating: cidade.part1.rating_medio },
      });
    }
  });
  
  return alertas;
}

export default useMetasProgress;
