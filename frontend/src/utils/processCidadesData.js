/**
 * 🏙️ PROCESSAMENTO DE DADOS DE CIDADES
 * 
 * Lógica centralizada para processar dados de cidades, combinar com campanhas e metas.
 * Remove duplicação entre componentes e consolida regras de negócio.
 */

import { 
  CIDADES_IDS, 
  PERCENTUAL_PUBLICO_ALVO,
  PERFORMANCE_THRESHOLDS 
} from '../constants/cidadesConstants';

import {
  calcularPercentual,
  formatarNumero,
  formatarMoeda,
  obterStatusPerformance
} from './metasUtils';

// ========== PROCESSAMENTO PRINCIPAL ==========

/**
 * Processa dados de todas as cidades combinando com campanhas e metas
 * @param {Array} cidadesData - Array de objetos cidade da API
 * @param {Array} campanhasData - Array de campanhas da API
 * @param {Object} metasReais - Objeto com metas reais por cidade (key: nome cidade)
 * @returns {Array} Array de objetos processados para exibição
 */
export const processarDadosCidades = (cidadesData, campanhasData = [], metasReais = {}) => {
  if (!cidadesData || !Array.isArray(cidadesData)) {
    console.warn('⚠️ processarDadosCidades: cidadesData inválido');
    return [];
  }

  return cidadesData.map(cidade => {
    try {
      return processarCidade(cidade, campanhasData, metasReais);
    } catch (error) {
      console.error(`❌ Erro ao processar cidade ${cidade.cidade}:`, error);
      return criarCidadeVazia(cidade);
    }
  });
};

/**
 * Processa dados de uma única cidade
 * @param {Object} cidade - Dados da cidade
 * @param {Array} campanhasData - Campanhas disponíveis
 * @param {Object} metasReais - Metas reais por cidade
 * @returns {Object} Dados processados da cidade
 */
const processarCidade = (cidade, campanhasData, metasReais) => {
  // 1. Calcular população e público-alvo
  const populacao = obterPopulacao(cidade);
  const publico_alvo = calcularPublicoAlvo(populacao);

  // 2. Filtrar campanhas da cidade
  const campanhasCidade = filtrarCampanhasCidade(cidade, campanhasData);

  // 3. Determinar fase atual
  const fase_atual = determinarFaseAtual(campanhasCidade);

  // 4. Obter dados reais ou estimados
  const dadosReal = obterDadosReais(cidade, metasReais, publico_alvo, fase_atual);

  // 5. Calcular métricas derivadas
  const metricas = calcularMetricas(dadosReal, campanhasCidade);

  // 6. Retornar objeto consolidado
  return {
    // Identificação
    cidade: cidade.cidade,
    cidade_id: cidade.id,

    // População
    populacao: formatarNumero(populacao),
    populacao_num: populacao,
    publico_alvo: formatarNumero(publico_alvo),
    publico_alvo_num: publico_alvo,

    // Fase e período
    fase_atual,
    mes_campanha: `${dadosReal.periodo_meses}º Mês`,
    periodo_meses: dadosReal.periodo_meses,

    // Metas e realização
    meta_mes: `${formatarNumero(dadosReal.meta_corridas)} corridas`,
    meta_mes_num: dadosReal.meta_corridas,
    realizado: `${formatarNumero(dadosReal.resultado_corridas)} corridas`,
    realizado_num: dadosReal.resultado_corridas,

    // Performance
    percentual: `${dadosReal.progresso_corridas.toFixed(1)}%`,
    percentual_num: dadosReal.progresso_corridas,
    status_performance: obterStatusPerformance(dadosReal.progresso_corridas),

    // Projeções
    projecao_ano: `${formatarNumero(metricas.projecao_ano)} corridas`,
    projecao_ano_num: metricas.projecao_ano,

    // Receita
    meta_receita: dadosReal.meta_receita,
    resultado_receita: dadosReal.resultado_receita,
    receita_estimada: formatarMoeda(dadosReal.resultado_receita),
    progresso_receita: dadosReal.progresso_receita,

    // Motoristas
    meta_motoristas: dadosReal.meta_motoristas,
    resultado_motoristas: dadosReal.resultado_motoristas,
    progresso_motoristas: dadosReal.progresso_motoristas,

    // Qualidade
    satisfacao: dadosReal.satisfacao,
    taxa_cancelamento: dadosReal.taxa_cancelamento,
    usuarios_ativos: dadosReal.usuarios_ativos,

    // Campanhas
    campanhas_ativas: metricas.campanhas_ativas,
    total_campanhas: campanhasCidade.length,
    orcamento_total: metricas.orcamento_total,
    orcamento_total_formatado: formatarMoeda(metricas.orcamento_total),

    // Metadados
    tem_dados_reais: dadosReal.eh_real,
    ultima_atualizacao: new Date().toISOString(),
    
    // Dados brutos para análises
    _raw: {
      cidade_obj: cidade,
      campanhas: campanhasCidade,
      metas: metasReais[cidade.cidade]
    }
  };
};

// ========== FUNÇÕES AUXILIARES ==========

/**
 * Obtém população da cidade (prioriza 2024, fallback 2022)
 * @param {Object} cidade 
 * @returns {number} População
 */
const obterPopulacao = (cidade) => {
  return cidade.populacao_estimada_2024 || 
         cidade.populacao_censo_2022 || 
         cidade.populacao || 
         0;
};

/**
 * Calcula público-alvo (faixa etária 15-44 anos)
 * @param {number} populacao 
 * @returns {number} Público-alvo estimado
 */
const calcularPublicoAlvo = (populacao) => {
  return Math.round(populacao * PERCENTUAL_PUBLICO_ALVO);
};

/**
 * Filtra campanhas que pertencem a uma cidade
 * @param {Object} cidade 
 * @param {Array} campanhasData 
 * @returns {Array} Campanhas da cidade
 */
const filtrarCampanhasCidade = (cidade, campanhasData) => {
  if (!campanhasData || !Array.isArray(campanhasData)) return [];

  return campanhasData.filter(campanha => {
    // Comparar por ID se disponível
    if (campanha.cidade?.id && cidade.id) {
      return campanha.cidade.id === cidade.id;
    }

    // Fallback: comparar por nome
    const nomeCampanha = campanha.cidade?.nome || campanha.cidade_nome || '';
    const nomeCidade = cidade.cidade || cidade.nome || '';
    
    return normalizarNome(nomeCampanha) === normalizarNome(nomeCidade);
  });
};

/**
 * Normaliza nome para comparação (remove acentos, lowercase, trim)
 * @param {string} nome 
 * @returns {string} Nome normalizado
 */
const normalizarNome = (nome) => {
  if (!nome) return '';
  
  return nome
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();
};

/**
 * Determina fase atual baseada nas campanhas ativas
 * @param {Array} campanhas 
 * @returns {string} Fase atual (ex: "Fase 1", "Fase 2", "Planejamento")
 */
const determinarFaseAtual = (campanhas) => {
  if (!campanhas || campanhas.length === 0) return 'Planejamento';

  const fases = campanhas.map(c => c.fase).filter(Boolean);

  // Retornar a fase mais avançada
  if (fases.includes('Fase 3')) return 'Fase 3';
  if (fases.includes('Fase 2')) return 'Fase 2';
  if (fases.includes('Fase 1')) return 'Fase 1';

  return 'Planejamento';
};

/**
 * Obtém dados reais da API ou cria estimativa
 * @param {Object} cidade 
 * @param {Object} metasReais 
 * @param {number} publico_alvo 
 * @param {string} fase_atual 
 * @returns {Object} Dados reais ou estimados
 */
const obterDadosReais = (cidade, metasReais, publico_alvo, fase_atual) => {
  const nomeCidade = cidade.cidade || cidade.nome;
  const metasCidade = metasReais[nomeCidade];

  // Se tiver dados reais da API, usar
  if (metasCidade && Array.isArray(metasCidade) && metasCidade.length > 0) {
    return extrairDadosReais(metasCidade[0]);
  }

  // Caso contrário, criar estimativa baseada na fase
  return criarDadosEstimados(publico_alvo, fase_atual);
};

/**
 * Extrai dados reais da resposta da API
 * @param {Object} metaAPI - Objeto meta da API
 * @returns {Object} Dados estruturados
 */
const extrairDadosReais = (metaAPI) => {
  return {
    eh_real: true,
    periodo_meses: metaAPI.periodo_meses || 3,
    
    // Corridas
    meta_corridas: metaAPI.metas?.corridas || 0,
    resultado_corridas: metaAPI.resultados?.corridas || 0,
    progresso_corridas: metaAPI.progresso?.corridas || 0,
    
    // Receita
    meta_receita: metaAPI.metas?.receita || 0,
    resultado_receita: metaAPI.resultados?.receita || 0,
    progresso_receita: metaAPI.progresso?.receita || 0,
    
    // Motoristas
    meta_motoristas: metaAPI.metas?.motoristas || 0,
    resultado_motoristas: metaAPI.resultados?.motoristas || 0,
    progresso_motoristas: metaAPI.progresso?.motoristas || 0,
    
    // Qualidade
    usuarios_ativos: metaAPI.resultados?.usuarios_ativos || 0,
    satisfacao: metaAPI.resultados?.satisfacao || 0,
    taxa_cancelamento: metaAPI.resultados?.taxa_cancelamento || 0
  };
};

/**
 * Cria dados estimados quando não há dados reais
 * @param {number} publico_alvo 
 * @param {string} fase_atual 
 * @returns {Object} Dados estimados
 */
const criarDadosEstimados = (publico_alvo, fase_atual) => {
  // Determinar mês de campanha baseado na fase
  const progressoMes = fase_atual === 'Fase 1' ? 1 : 
                       fase_atual === 'Fase 2' ? 2 : 
                       fase_atual === 'Fase 3' ? 3 : 0;

  // Calcular meta estimada baseada em percentual do público-alvo
  const percentualMeta = progressoMes === 1 ? 0.005 : // 0.5%
                         progressoMes === 2 ? 0.010 : // 1.0%
                         progressoMes === 3 ? 0.020 : // 2.0%
                         0;

  const meta_corridas = Math.round(publico_alvo * percentualMeta);
  const meta_receita = meta_corridas * 2.5; // R$ 2.50 por corrida

  return {
    eh_real: false,
    periodo_meses: progressoMes,
    
    // Todas as métricas zeradas (sem dados)
    meta_corridas,
    resultado_corridas: 0,
    progresso_corridas: 0,
    
    meta_receita,
    resultado_receita: 0,
    progresso_receita: 0,
    
    meta_motoristas: 0,
    resultado_motoristas: 0,
    progresso_motoristas: 0,
    
    usuarios_ativos: 0,
    satisfacao: 0,
    taxa_cancelamento: 0
  };
};

/**
 * Calcula métricas derivadas
 * @param {Object} dadosReal 
 * @param {Array} campanhas 
 * @returns {Object} Métricas calculadas
 */
const calcularMetricas = (dadosReal, campanhas) => {
  // Projeção anual baseada no período atual
  const meses_periodo = dadosReal.periodo_meses || 1;
  const projecao_ano = Math.round(dadosReal.meta_corridas * (12 / meses_periodo));

  // Campanhas ativas
  const campanhas_ativas = campanhas.filter(c => c.status === 'ativa').length;

  // Orçamento total
  const orcamento_total = campanhas.reduce((sum, c) => sum + (c.orcamento_previsto || 0), 0);

  return {
    projecao_ano,
    campanhas_ativas,
    orcamento_total
  };
};

/**
 * Cria objeto de cidade vazio (fallback para erros)
 * @param {Object} cidade 
 * @returns {Object} Cidade com valores padrão
 */
const criarCidadeVazia = (cidade) => {
  return {
    cidade: cidade.cidade || cidade.nome || 'Desconhecida',
    cidade_id: cidade.id || null,
    populacao: '0',
    populacao_num: 0,
    publico_alvo: '0',
    publico_alvo_num: 0,
    fase_atual: 'Desconhecido',
    mes_campanha: 'N/A',
    periodo_meses: 0,
    meta_mes: '0 corridas',
    meta_mes_num: 0,
    realizado: '0 corridas',
    realizado_num: 0,
    percentual: '0,0%',
    percentual_num: 0,
    status_performance: 'neutro',
    projecao_ano: '0 corridas',
    projecao_ano_num: 0,
    receita_estimada: 'R$ 0,00',
    satisfacao: 0,
    taxa_cancelamento: 0,
    usuarios_ativos: 0,
    campanhas_ativas: 0,
    total_campanhas: 0,
    orcamento_total: 0,
    orcamento_total_formatado: 'R$ 0,00',
    tem_dados_reais: false,
    erro: true
  };
};

// ========== FUNÇÕES DE FILTRAGEM E ORDENAÇÃO ==========

/**
 * Filtra cidades por fase
 * @param {Array} cidades - Array de cidades processadas
 * @param {string} fase - Fase para filtrar ('all', 'Fase 1', etc.)
 * @returns {Array} Cidades filtradas
 */
export const filtrarPorFase = (cidades, fase) => {
  if (!cidades || !Array.isArray(cidades)) return [];
  if (fase === 'all' || fase === 'todas') return cidades;

  return cidades.filter(cidade => cidade.fase_atual === fase);
};

/**
 * Filtra cidades por status de performance
 * @param {Array} cidades 
 * @param {string} status - 'acima', 'meta', 'atencao', 'abaixo'
 * @returns {Array} Cidades filtradas
 */
export const filtrarPorStatus = (cidades, status) => {
  if (!cidades || !Array.isArray(cidades)) return [];
  if (status === 'all' || status === 'todos') return cidades;

  return cidades.filter(cidade => cidade.status_performance === status);
};

/**
 * Ordena cidades por campo específico
 * @param {Array} cidades 
 * @param {string} ordenacao - 'alfabetica', 'populacao', 'performance', 'meta'
 * @returns {Array} Cidades ordenadas
 */
export const ordenarCidades = (cidades, ordenacao) => {
  if (!cidades || !Array.isArray(cidades)) return [];

  const sorted = [...cidades];

  switch (ordenacao) {
    case 'alfabetica':
      return sorted.sort((a, b) => a.cidade.localeCompare(b.cidade));
    
    case 'populacao':
      return sorted.sort((a, b) => b.populacao_num - a.populacao_num);
    
    case 'performance':
      return sorted.sort((a, b) => b.percentual_num - a.percentual_num);
    
    case 'meta':
      return sorted.sort((a, b) => b.meta_mes_num - a.meta_mes_num);
    
    case 'realizado':
      return sorted.sort((a, b) => b.realizado_num - a.realizado_num);
    
    default:
      return sorted;
  }
};

/**
 * Busca cidades por nome (search)
 * @param {Array} cidades 
 * @param {string} termo - Termo de busca
 * @returns {Array} Cidades que correspondem à busca
 */
export const buscarCidades = (cidades, termo) => {
  if (!cidades || !Array.isArray(cidades)) return [];
  if (!termo || termo.trim() === '') return cidades;

  const termoNormalizado = normalizarNome(termo);

  return cidades.filter(cidade => {
    const nomeNormalizado = normalizarNome(cidade.cidade);
    return nomeNormalizado.includes(termoNormalizado);
  });
};

// ========== AGREGAÇÕES ==========

/**
 * Calcula totais agregados de todas as cidades
 * @param {Array} cidades 
 * @returns {Object} Totais agregados
 */
export const calcularTotais = (cidades) => {
  if (!cidades || cidades.length === 0) {
    return {
      total_cidades: 0,
      populacao_total: 0,
      publico_alvo_total: 0,
      meta_total: 0,
      realizado_total: 0,
      percentual_medio: 0,
      receita_total: 0,
      campanhas_ativas_total: 0,
      orcamento_total: 0
    };
  }

  const totais = cidades.reduce((acc, cidade) => {
    acc.populacao_total += cidade.populacao_num || 0;
    acc.publico_alvo_total += cidade.publico_alvo_num || 0;
    acc.meta_total += cidade.meta_mes_num || 0;
    acc.realizado_total += cidade.realizado_num || 0;
    acc.receita_total += cidade.resultado_receita || 0;
    acc.campanhas_ativas_total += cidade.campanhas_ativas || 0;
    acc.orcamento_total += cidade.orcamento_total || 0;
    
    return acc;
  }, {
    total_cidades: cidades.length,
    populacao_total: 0,
    publico_alvo_total: 0,
    meta_total: 0,
    realizado_total: 0,
    receita_total: 0,
    campanhas_ativas_total: 0,
    orcamento_total: 0
  });

  // Calcular percentual médio
  totais.percentual_medio = totais.meta_total > 0 
    ? (totais.realizado_total / totais.meta_total) * 100 
    : 0;

  return totais;
};

// ========== EXPORTS ==========

export default {
  processarDadosCidades,
  filtrarPorFase,
  filtrarPorStatus,
  ordenarCidades,
  buscarCidades,
  calcularTotais
};
