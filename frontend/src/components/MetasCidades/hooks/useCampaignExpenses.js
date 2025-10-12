import { useState, useEffect, useCallback } from 'react';

/**
 * Hook para buscar gastos de campanhas integrado com financeiro
 * Combina dados de /api/campanhas e /api/financeiro
 * 
 * @param {string} fase - Fase da campanha ('Fase 1', 'Fase 2', 'Fase 3', ou null para todas)
 * @param {string} cidade - Cidade (ou null para todas)
 * @param {boolean} autoRefresh - Ativar polling automático (5 minutos)
 * @returns {Object} { data, loading, error, refresh }
 */
export const useCampaignExpenses = (fase = null, cidade = null, autoRefresh = false) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  const fetchExpenses = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      console.log(`[useCampaignExpenses] Buscando dados: fase=${fase}, cidade=${cidade}`);
      
      // Buscar dados financeiros (overview dos últimos 90 dias)
      const financeiroResponse = await fetch(
        `${API_URL}/api/financeiro/overview?periodo=90`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!financeiroResponse.ok) {
        throw new Error(`HTTP ${financeiroResponse.status}: Erro ao buscar dados financeiros`);
      }
      
      const financeiroData = await financeiroResponse.json();
      
      // Buscar campanhas
      const campanhasResponse = await fetch(
        `${API_URL}/api/campanhas`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!campanhasResponse.ok) {
        throw new Error(`HTTP ${campanhasResponse.status}: Erro ao buscar campanhas`);
      }
      
      const campanhasData = await campanhasResponse.json();
      
      // Filtrar campanhas por fase e cidade
      let campanhasFiltradas = Array.isArray(campanhasData) ? campanhasData : [];
      
      if (fase) {
        campanhasFiltradas = campanhasFiltradas.filter(c => c.fase === fase);
      }
      
      if (cidade) {
        campanhasFiltradas = campanhasFiltradas.filter(c => c.cidade === cidade);
      }
      
      // Calcular totais das campanhas
      const orcamento_previsto = campanhasFiltradas.reduce(
        (sum, c) => sum + parseFloat(c.orcamento_previsto || 0), 
        0
      );
      
      const custo_real = campanhasFiltradas.reduce(
        (sum, c) => sum + parseFloat(c.custo_real || 0), 
        0
      );
      
      // Agrupar campanhas por status financeiro
      const campanhasPorStatus = {
        empenhado: campanhasFiltradas.filter(c => c.status_financeiro === 'empenhado'),
        pago: campanhasFiltradas.filter(c => c.status_financeiro === 'pago'),
        liquidado: campanhasFiltradas.filter(c => c.status_financeiro === 'liquidado'),
      };
      
      // Processar gastos do financeiro
      const gastosRelevantes = financeiroData.top_gastos || [];
      
      // Calcular métricas de documentação
      const totalGastos = gastosRelevantes.length;
      const gastosComNF = gastosRelevantes.filter(g => g.possui_nota_fiscal).length;
      const gastosSemNF = totalGastos - gastosComNF;
      
      // Agrupar gastos por categoria
      const gastosPorCategoria = financeiroData.gastos_por_categoria || {};
      
      // Processar dados
      const processedData = {
        fase,
        cidade,
        
        // Campanhas
        campanhas: campanhasFiltradas,
        total_campanhas: campanhasFiltradas.length,
        campanhas_por_status: campanhasPorStatus,
        
        // Orçamento
        orcamento_previsto,
        custo_real,
        saldo: orcamento_previsto - custo_real,
        percentual_utilizado: orcamento_previsto > 0 
          ? ((custo_real / orcamento_previsto) * 100).toFixed(1)
          : 0,
        
        // Valores por status financeiro
        valores_status: {
          empenhado: campanhasPorStatus.empenhado.reduce(
            (sum, c) => sum + parseFloat(c.orcamento_previsto || 0), 0
          ),
          pago: campanhasPorStatus.pago.reduce(
            (sum, c) => sum + parseFloat(c.custo_real || 0), 0
          ),
          liquidado: campanhasPorStatus.liquidado.reduce(
            (sum, c) => sum + parseFloat(c.custo_real || 0), 0
          ),
        },
        
        // Gastos do financeiro
        gastos: gastosRelevantes,
        total_gastos: financeiroData.total_gastos || 0,
        total_despesas: financeiroData.total_despesas || 0,
        media_gastos_dia: financeiroData.media_gastos_dia || 0,
        
        // Categorias
        gastos_por_categoria: gastosPorCategoria,
        categoria_mais_gasta: Object.entries(gastosPorCategoria).reduce(
          (max, [cat, valor]) => valor > max.valor ? { categoria: cat, valor } : max,
          { categoria: 'N/A', valor: 0 }
        ),
        
        // Documentação
        documentacao: {
          total: totalGastos,
          com_nota_fiscal: gastosComNF,
          sem_nota_fiscal: gastosSemNF,
          taxa_documentacao: totalGastos > 0 
            ? ((gastosComNF / totalGastos) * 100).toFixed(1)
            : 0,
        },
        
        // Fornecedores
        gastos_por_fornecedor: financeiroData.gastos_por_fornecedor || {},
        
        // Alertas
        alertas: gerarAlertasFinanceiros({
          saldo: orcamento_previsto - custo_real,
          percentual: (custo_real / orcamento_previsto) * 100,
          gastosSemNF,
          totalGastos,
        }),
        
        // Metadados
        ultima_atualizacao: new Date().toISOString(),
        raw_data: {
          financeiro: financeiroData,
          campanhas: campanhasData,
        },
      };
      
      console.log(`[useCampaignExpenses] ✅ Dados carregados:`, {
        campanhas: processedData.total_campanhas,
        orcamento: processedData.orcamento_previsto,
        custo: processedData.custo_real,
        saldo: processedData.saldo
      });
      
      setData(processedData);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error('[useCampaignExpenses] ❌ Erro:', err);
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [fase, cidade]);
  
  // Efeito inicial
  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);
  
  // Polling automático (5 minutos)
  useEffect(() => {
    if (!autoRefresh) return;
    
    console.log('[useCampaignExpenses] 🔄 Auto-refresh ativado (5 minutos)');
    
    const interval = setInterval(() => {
      console.log('[useCampaignExpenses] 🔄 Atualizando dados automaticamente...');
      fetchExpenses();
    }, 5 * 60 * 1000);
    
    return () => {
      console.log('[useCampaignExpenses] 🛑 Auto-refresh desativado');
      clearInterval(interval);
    };
  }, [autoRefresh, fetchExpenses]);
  
  return {
    data,
    loading,
    error,
    lastUpdate,
    refresh: fetchExpenses,
    
    // Helpers computados
    hasData: data !== null && !error,
    isEmpty: data !== null && data.total_campanhas === 0,
    temAlerta: data && data.alertas.length > 0,
    orcamentoCritico: data && parseFloat(data.percentual_utilizado) > 90,
  };
};

// Função auxiliar para gerar alertas financeiros
function gerarAlertasFinanceiros({ saldo, percentual, gastosSemNF, totalGastos }) {
  const alertas = [];
  
  // Alertas orçamentários
  if (percentual > 95) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'danger',
      mensagem: `Orçamento crítico: ${percentual.toFixed(1)}% utilizado`,
      icone: '🔴',
    });
  } else if (percentual > 85) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'warning',
      mensagem: `Atenção: ${percentual.toFixed(1)}% do orçamento utilizado`,
      icone: '⚠️',
    });
  }
  
  if (saldo < 0) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'danger',
      mensagem: `Orçamento estourado em R$ ${Math.abs(saldo).toFixed(2)}`,
      icone: '💸',
    });
  }
  
  // Alertas de documentação
  const percentualSemNF = totalGastos > 0 ? (gastosSemNF / totalGastos) * 100 : 0;
  
  if (percentualSemNF > 30) {
    alertas.push({
      tipo: 'documentacao',
      nivel: 'warning',
      mensagem: `${gastosSemNF} gastos sem nota fiscal (${percentualSemNF.toFixed(1)}%)`,
      icone: '📄',
    });
  }
  
  return alertas;
}

export default useCampaignExpenses;
