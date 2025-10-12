/**
 * 🏙️ CONSTANTES DE CIDADES - Sistema de Metas Estratégicas
 * 
 * Centraliza todos os valores fixos relacionados a cidades, fases e configurações.
 * Evita hardcoding espalhado pelo código.
 */

// ========== MAPEAMENTO DE CIDADES ==========

/**
 * Mapa de nomes de cidades para IDs do banco de dados
 */
export const CIDADES_IDS = {
  'Peixoto de Azevedo': 1,
  'Nova Monte Verde': 2,
  'Matupá': 3,
  'Guarantã do Norte': 4,
  'Nova Bandeirantes': 5
};

/**
 * Mapa reverso: IDs para nomes de cidades
 */
export const CIDADES_NOMES = {
  1: 'Peixoto de Azevedo',
  2: 'Nova Monte Verde',
  3: 'Matupá',
  4: 'Guarantã do Norte',
  5: 'Nova Bandeirantes'
};

/**
 * Siglas das cidades para exibição compacta
 */
export const CIDADES_SIGLAS = {
  1: 'PXT',
  2: 'NMV',
  3: 'MTP',
  4: 'GTN',
  5: 'NBD'
};

/**
 * Nomes alternativos/variações encontradas nos dados (para normalização)
 */
export const CIDADES_ALIASES = {
  'PEIXOTO': 'Peixoto de Azevedo',
  'PEIXOTO DE AZEVEDO': 'Peixoto de Azevedo',
  'MATUPA': 'Matupá',
  'MATUPÁ': 'Matupá',
  'GUARANTA': 'Guarantã do Norte',
  'GUARANTA DO NORTE': 'Guarantã do Norte',
  'GUARANTÃ DO NORTE': 'Guarantã do Norte',
  'NOVA MONTE VERDE': 'Nova Monte Verde',
  'NOVA BANDEIRANTES': 'Nova Bandeirantes'
};

// ========== CONFIGURAÇÃO DE FASES ==========

/**
 * Configuração padrão para cada fase de planejamento
 */
export const FASES_CONFIG = {
  'Fase 1': {
    periodo: '01/ago a 14/set',
    status: 'em_execucao',
    part1: { 
      duracao: 15, 
      tipo: 'motoristas',
      descricao: 'Recrutamento e ativação de motoristas'
    },
    part2: { 
      duracao: 30, 
      tipo: 'corridas',
      descricao: 'Geração de demanda e corridas'
    }
  },
  'Fase 2': {
    periodo: '15/set a 30/out',
    status: 'planejada',
    part1: { 
      duracao: 15, 
      tipo: 'motoristas',
      descricao: 'Expansão de motoristas'
    },
    part2: { 
      duracao: 30, 
      tipo: 'corridas',
      descricao: 'Crescimento de corridas'
    }
  },
  'Fase 3': {
    periodo: '01/nov a 14/dez',
    status: 'planejada',
    part1: { 
      duracao: 15, 
      tipo: 'motoristas',
      descricao: 'Consolidação de motoristas'
    },
    part2: { 
      duracao: 30, 
      tipo: 'corridas',
      descricao: 'Sustentação de corridas'
    }
  }
};

// ========== STATUS E CORES ==========

/**
 * Cores Tailwind para diferentes status de performance
 */
export const STATUS_CORES = {
  'acima': {
    text: 'text-green-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
    badge: 'bg-green-100 text-green-800'
  },
  'meta': {
    text: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    badge: 'bg-blue-100 text-blue-800'
  },
  'atencao': {
    text: 'text-yellow-600',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    badge: 'bg-yellow-100 text-yellow-800'
  },
  'abaixo': {
    text: 'text-red-600',
    bg: 'bg-red-50',
    border: 'border-red-200',
    badge: 'bg-red-100 text-red-800'
  },
  'neutro': {
    text: 'text-gray-600',
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    badge: 'bg-gray-100 text-gray-800'
  }
};

/**
 * Cores para status de fases
 */
export const STATUS_FASE_CORES = {
  'planejada': {
    text: 'text-gray-600',
    bg: 'bg-gray-50',
    badge: 'bg-gray-100 text-gray-800',
    icon: 'text-gray-500'
  },
  'em_execucao': {
    text: 'text-blue-600',
    bg: 'bg-blue-50',
    badge: 'bg-blue-100 text-blue-800',
    icon: 'text-blue-500'
  },
  'pausada': {
    text: 'text-yellow-600',
    bg: 'bg-yellow-50',
    badge: 'bg-yellow-100 text-yellow-800',
    icon: 'text-yellow-500'
  },
  'concluida': {
    text: 'text-green-600',
    bg: 'bg-green-50',
    badge: 'bg-green-100 text-green-800',
    icon: 'text-green-500'
  },
  'cancelada': {
    text: 'text-red-600',
    bg: 'bg-red-50',
    badge: 'bg-red-100 text-red-800',
    icon: 'text-red-500'
  }
};

// ========== TEXTO E LABELS ==========

/**
 * Labels amigáveis para status de performance
 */
export const STATUS_LABELS = {
  'acima': '✅ Acima da Meta',
  'meta': '🎯 Na Meta',
  'atencao': '⚠️ Atenção',
  'abaixo': '🔴 Abaixo da Meta',
  'neutro': '➖ Sem Dados'
};

/**
 * Labels para status de fases
 */
export const STATUS_FASE_LABELS = {
  'planejada': '📅 Planejada',
  'em_execucao': '▶️ Em Execução',
  'pausada': '⏸️ Pausada',
  'concluida': '✅ Concluída',
  'cancelada': '❌ Cancelada'
};

// ========== MÉTRICAS E THRESHOLDS ==========

/**
 * Thresholds para classificação de performance
 */
export const PERFORMANCE_THRESHOLDS = {
  ACIMA: 100,        // >= 100%
  META: 90,          // >= 90%
  ATENCAO: 70,       // >= 70%
  ABAIXO: 0          // < 70%
};

/**
 * Percentuais de público-alvo por tipo de meta
 */
export const META_PERCENTUAIS_PUBLICO = {
  'muito_baixa': 0.5,   // 0.5% do público
  'baixa': 1.0,         // 1% do público
  'media': 2.0,         // 2% do público
  'alta': 10.0          // 10% do público
};

/**
 * Multiplicadores para cálculo de receita estimada
 */
export const MULTIPLICADORES_RECEITA = {
  corrida_media: 2.5,        // R$ 2.50 por corrida (média)
  corrida_min: 1.5,          // R$ 1.50 (mínimo)
  corrida_max: 5.0           // R$ 5.00 (máximo)
};

// ========== CONFIGURAÇÕES DE POPULAÇÃO ==========

/**
 * Percentual da população na faixa etária 15-44 anos (público-alvo)
 */
export const PERCENTUAL_PUBLICO_ALVO = 0.45; // 45%

/**
 * Percentual masculino/feminino do público-alvo
 */
export const PERCENTUAL_GENERO = {
  homens: 0.52,   // 52%
  mulheres: 0.48  // 48%
};

// ========== PERÍODOS E DURAÇÕES ==========

/**
 * Períodos disponíveis para análise (em meses)
 */
export const PERIODOS_DISPONIVEIS = [2, 3, 6, 12];

/**
 * Duração padrão de campanhas (em dias)
 */
export const DURACAO_CAMPANHAS = {
  part1_motoristas: 15,
  part2_corridas: 30,
  total: 45
};

// ========== URLS DA API ==========

/**
 * Base URL da API (pode ser sobrescrita por env var)
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Endpoints da API
 */
export const API_ENDPOINTS = {
  METAS_CONSOLIDADO: (cidadeId) => `${API_BASE_URL}/api/metas-estrategicas/consolidado/${cidadeId}`,
  METAS_DASHBOARD: `${API_BASE_URL}/api/metas-estrategicas/dashboard`,
  CAMPANHAS: `${API_BASE_URL}/api/dashboard-executivo/campanhas`,
  DRIVERS_BY_CITY: (cidade) => `${API_BASE_URL}/api/drivers/by-city?cidade=${encodeURIComponent(cidade)}`,
  METRICS_OVERVIEW: `${API_BASE_URL}/api/metrics/overview`
};

// ========== FUNÇÕES HELPER ==========

/**
 * Normaliza nome de cidade para padrão
 */
export const normalizarNomeCidade = (nomeRaw) => {
  const nomeUpper = nomeRaw.toUpperCase();
  return CIDADES_ALIASES[nomeUpper] || nomeRaw;
};

/**
 * Obtém ID da cidade pelo nome
 */
export const obterCidadeId = (nomeCidade) => {
  const nomeNormalizado = normalizarNomeCidade(nomeCidade);
  return CIDADES_IDS[nomeNormalizado] || null;
};

/**
 * Obtém nome da cidade pelo ID
 */
export const obterCidadeNome = (cidadeId) => {
  return CIDADES_NOMES[cidadeId] || 'Desconhecida';
};

/**
 * Obtém sigla da cidade pelo ID
 */
export const obterCidadeSigla = (cidadeId) => {
  return CIDADES_SIGLAS[cidadeId] || 'N/A';
};

/**
 * Verifica se é uma cidade válida
 */
export const isCidadeValida = (nomeCidade) => {
  const nomeNormalizado = normalizarNomeCidade(nomeCidade);
  return Object.prototype.hasOwnProperty.call(CIDADES_IDS, nomeNormalizado);
};

/**
 * Lista todas as cidades disponíveis
 */
export const listarTodasCidades = () => {
  return Object.keys(CIDADES_IDS).map(nome => ({
    id: CIDADES_IDS[nome],
    nome: nome,
    sigla: CIDADES_SIGLAS[CIDADES_IDS[nome]]
  }));
};

/**
 * PLANO DE EXECUÇÃO - Dados estruturados por fase
 */
export const PLANO_EXECUCAO = {
  'Fase 1': {
    periodo: '01/ago a 14/set',
    status: 'em_execucao',
    cidades: ['Peixoto de Azevedo', 'Matupá', 'Guarantã do Norte'],
    part1: {
      periodo: '01/ago a 15/ago (15 dias)',
      status: 'em_execucao',
      tipo: 'motoristas',
      metas: {
        'Peixoto de Azevedo': 300,
        'Matupá': 250,
        'Guarantã do Norte': 200
      }
    },
    part2: {
      periodo: '16/ago a 14/set (30 dias)',
      status: 'planejada',
      tipo: 'corridas',
      metas: {
        'Peixoto de Azevedo': 5000,
        'Matupá': 4000,
        'Guarantã do Norte': 3500
      }
    },
    orcamento: {
      previsto: 500000,
      empenhado: 500000,
      pago: 300000,
      liquidado: 450000
    }
  },
  'Fase 2': {
    periodo: '15/set a 30/out',
    status: 'planejada',
    cidades: ['Peixoto de Azevedo', 'Nova Monte Verde', 'Matupá'],
    part1: {
      periodo: '15/set a 30/set (15 dias)',
      status: 'planejada',
      tipo: 'motoristas',
      metas: {
        'Peixoto de Azevedo': 350,
        'Nova Monte Verde': 150,
        'Matupá': 280
      }
    },
    part2: {
      periodo: '01/out a 30/out (30 dias)',
      status: 'planejada',
      tipo: 'corridas',
      metas: {
        'Peixoto de Azevedo': 6000,
        'Nova Monte Verde': 2500,
        'Matupá': 4500
      }
    },
    orcamento: {
      previsto: 600000,
      empenhado: 0,
      pago: 0,
      liquidado: 0
    }
  },
  'Fase 3': {
    periodo: '01/nov a 14/dez',
    status: 'planejada',
    cidades: ['Nova Bandeirantes', 'Nova Monte Verde', 'Guarantã do Norte'],
    part1: {
      periodo: '01/nov a 15/nov (15 dias)',
      status: 'planejada',
      tipo: 'motoristas',
      metas: {
        'Nova Bandeirantes': 120,
        'Nova Monte Verde': 180,
        'Guarantã do Norte': 220
      }
    },
    part2: {
      periodo: '16/nov a 14/dez (29 dias)',
      status: 'planejada',
      tipo: 'corridas',
      metas: {
        'Nova Bandeirantes': 2000,
        'Nova Monte Verde': 3000,
        'Guarantã do Norte': 3800
      }
    },
    orcamento: {
      previsto: 450000,
      empenhado: 0,
      pago: 0,
      liquidado: 0
    }
  }
};

// ========== EXPORTS DEFAULT ==========

export default {
  CIDADES_IDS,
  CIDADES_NOMES,
  CIDADES_SIGLAS,
  CIDADES_ALIASES,
  FASES_CONFIG,
  PLANO_EXECUCAO,
  STATUS_CORES,
  STATUS_FASE_CORES,
  STATUS_LABELS,
  STATUS_FASE_LABELS,
  PERFORMANCE_THRESHOLDS,
  META_PERCENTUAIS_PUBLICO,
  MULTIPLICADORES_RECEITA,
  PERCENTUAL_PUBLICO_ALVO,
  PERCENTUAL_GENERO,
  PERIODOS_DISPONIVEIS,
  DURACAO_CAMPANHAS,
  API_BASE_URL,
  API_ENDPOINTS,
  // Funções helper
  normalizarNomeCidade,
  obterCidadeId,
  obterCidadeNome,
  obterCidadeSigla,
  isCidadeValida,
  listarTodasCidades
};
