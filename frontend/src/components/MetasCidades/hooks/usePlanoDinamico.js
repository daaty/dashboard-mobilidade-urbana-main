/**
 * 🎯 USE PLANO DINÂMICO - Hook para gerenciar plano de execução
 * 
 * Hook customizado para construir e gerenciar o plano de execução dinâmico
 * a partir de dados de campanhas da API.
 */

import { useState, useEffect, useMemo } from 'react';
import {
  getFasePeriodo,
  getFaseStatus,
  getPartPeriodo,
  getPartStatus
} from '../../../utils/metasUtils.js';

/**
 * Constrói plano dinâmico a partir de campanhas
 * @param {Array} campanhas - Array de campanhas da API
 * @returns {Object} Objeto com fases estruturadas
 */
const buildPlanoDinamico = (campanhas) => {
  if (!campanhas || campanhas.length === 0) return {};
  
  const fasesPlanejamento = {};
  
  // 🔥 GARANTIR que cidades com dados reais estejam sempre na Fase 1
  const cidadesComDadosReais = ['PEIXOTO', 'MATUPA', 'GUARANTA DO NORTE'];
  
  // Agrupar campanhas por fase
  campanhas.forEach(campanha => {
    const fase = campanha.fase || 'Fase 1';
    
    if (!fasesPlanejamento[fase]) {
      fasesPlanejamento[fase] = {
        periodo: getFasePeriodo(fase),
        status: getFaseStatus(fase),
        cidades: new Set(),
        part1: { 
          periodo: getPartPeriodo(fase, 1),
          metas: {}, 
          tipo: "motoristas", 
          status: getPartStatus(fase, 1) 
        },
        part2: { 
          periodo: getPartPeriodo(fase, 2),
          metas: {}, 
          tipo: "corridas", 
          status: getPartStatus(fase, 2)
        },
        orcamento: { empenhado: 0, pagamento: 0, liquidacao: 0, previsto: 0 }
      };
    }
    
    // Adicionar cidade
    if (campanha.cidade?.nome) {
      fasesPlanejamento[fase].cidades.add(campanha.cidade.nome);
    }
    
    // Adicionar metas por parte
    if (campanha.parte_campanha === "Part 1" && campanha.cidade?.nome) {
      fasesPlanejamento[fase].part1.metas[campanha.cidade.nome] = campanha.meta_quantidade || 0;
    } else if (campanha.parte_campanha === "Part 2" && campanha.cidade?.nome) {
      fasesPlanejamento[fase].part2.metas[campanha.cidade.nome] = campanha.meta_quantidade || 0;
    }
    
    // Somar orçamentos
    fasesPlanejamento[fase].orcamento.empenhado += campanha.orcamento_previsto || 0;
    fasesPlanejamento[fase].orcamento.pagamento += Math.round((campanha.orcamento_previsto || 0) * 0.6);
    fasesPlanejamento[fase].orcamento.liquidacao += Math.round((campanha.orcamento_previsto || 0) * 0.6);
    fasesPlanejamento[fase].orcamento.previsto += Math.round((campanha.orcamento_previsto || 0) * 0.3);
  });
  
  // 🔥 GARANTIR que Fase 1 existe e inclui cidades com dados reais
  if (!fasesPlanejamento['Fase 1']) {
    fasesPlanejamento['Fase 1'] = {
      periodo: getFasePeriodo('Fase 1'),
      status: getFaseStatus('Fase 1'),
      cidades: new Set(),
      part1: { 
        periodo: getPartPeriodo('Fase 1', 1),
        metas: {}, 
        tipo: "motoristas", 
        status: getPartStatus('Fase 1', 1) 
      },
      part2: { 
        periodo: getPartPeriodo('Fase 1', 2),
        metas: {}, 
        tipo: "corridas", 
        status: getPartStatus('Fase 1', 2)
      },
      orcamento: { empenhado: 4060, pagamento: 2240, liquidacao: 2240, previsto: 1820 }
    };
  }
  
  // Adicionar cidades com dados reais na Fase 1
  cidadesComDadosReais.forEach(cidade => {
    fasesPlanejamento['Fase 1'].cidades.add(cidade);
    // Metas padrão para as cidades com dados reais
    if (!fasesPlanejamento['Fase 1'].part1.metas[cidade]) {
      fasesPlanejamento['Fase 1'].part1.metas[cidade] = cidade === 'MATUPA' ? 4 : cidade === 'PEIXOTO' ? 6 : 8;
    }
    if (!fasesPlanejamento['Fase 1'].part2.metas[cidade]) {
      fasesPlanejamento['Fase 1'].part2.metas[cidade] = cidade === 'MATUPA' ? 20 : cidade === 'PEIXOTO' ? 30 : 20;
    }
  });
  
  // Converter Set para Array
  Object.keys(fasesPlanejamento).forEach(fase => {
    fasesPlanejamento[fase].cidades = Array.from(fasesPlanejamento[fase].cidades);
  });
  
  return fasesPlanejamento;
};

/**
 * Hook para gerenciar plano de execução dinâmico
 * @param {Array} campanhas - Array de campanhas
 * @returns {Object} { plano, loading, refresh }
 */
const usePlanoDinamico = (campanhas) => {
  const [loading, setLoading] = useState(true);
  
  // Memoizar o plano para evitar reconstrução desnecessária
  const plano = useMemo(() => {
    if (!campanhas) return {};
    return buildPlanoDinamico(campanhas);
  }, [campanhas]);
  
  // Atualizar loading quando campanhas mudarem
  useEffect(() => {
    if (campanhas !== undefined) {
      setLoading(false);
    }
  }, [campanhas]);
  
  // Função para forçar refresh (caso necessário)
  const refresh = () => {
    setLoading(true);
    // Trigger para recarregar dados (implementar callback se necessário)
    setTimeout(() => setLoading(false), 100);
  };
  
  return {
    plano,
    loading,
    refresh,
    // Helpers
    hasFases: Object.keys(plano).length > 0,
    totalFases: Object.keys(plano).length,
    fases: Object.keys(plano)
  };
};

export default usePlanoDinamico;
export { buildPlanoDinamico };
