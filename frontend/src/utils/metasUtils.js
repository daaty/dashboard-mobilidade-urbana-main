/**
 * 🧮 UTILIDADES PARA METAS ESTRATÉGICAS
 * 
 * Funções helper para cálculos, formatação e lógica de negócio do sistema de metas.
 * Centraliza toda lógica reutilizável entre componentes.
 */

import { PERFORMANCE_THRESHOLDS, FASES_CONFIG } from '../constants/cidadesConstants';

// ========== FORMATAÇÃO ==========

/**
 * Formata número como moeda brasileira
 * @param {number} valor - Valor numérico
 * @param {boolean} showPrefix - Se deve mostrar "R$"
 * @returns {string} Valor formatado (ex: "R$ 1.234,56")
 */
export const formatarMoeda = (valor, showPrefix = true) => {
  if (valor === null || valor === undefined || isNaN(valor)) {
    return showPrefix ? 'R$ 0,00' : '0,00';
  }
  
  const formatted = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(valor);
  
  return showPrefix ? formatted : formatted.replace('R$', '').trim();
};

/**
 * Formata número com separadores de milhar
 * @param {number} valor - Valor numérico
 * @param {number} decimais - Casas decimais (default: 0)
 * @returns {string} Número formatado (ex: "1.234,56")
 */
export const formatarNumero = (valor, decimais = 0) => {
  if (valor === null || valor === undefined || isNaN(valor)) {
    return '0';
  }
  
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: decimais,
    maximumFractionDigits: decimais
  }).format(valor);
};

/**
 * Formata percentual com símbolo
 * @param {number} valor - Valor percentual (0-100)
 * @param {number} decimais - Casas decimais (default: 1)
 * @returns {string} Percentual formatado (ex: "85,5%")
 */
export const formatarPercentual = (valor, decimais = 1) => {
  if (valor === null || valor === undefined || isNaN(valor)) {
    return '0,0%';
  }
  
  return `${formatarNumero(valor, decimais)}%`;
};

/**
 * Formata data para formato brasileiro
 * @param {Date|string} data - Data a ser formatada
 * @returns {string} Data formatada (ex: "01/08/2025")
 */
export const formatarData = (data) => {
  if (!data) return 'N/A';
  
  const date = typeof data === 'string' ? new Date(data) : data;
  
  if (isNaN(date.getTime())) return 'Data inválida';
  
  return new Intl.DateTimeFormat('pt-BR').format(date);
};

/**
 * Formata período de data (ex: "01/ago a 14/set")
 * @param {Date|string} dataInicio 
 * @param {Date|string} dataFim 
 * @returns {string} Período formatado
 */
export const formatarPeriodo = (dataInicio, dataFim) => {
  if (!dataInicio || !dataFim) return 'A definir';
  
  const inicio = typeof dataInicio === 'string' ? new Date(dataInicio) : dataInicio;
  const fim = typeof dataFim === 'string' ? new Date(dataFim) : dataFim;
  
  const formatShort = (date) => {
    const day = String(date.getDate()).padStart(2, '0');
    const months = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
    const month = months[date.getMonth()];
    return `${day}/${month}`;
  };
  
  return `${formatShort(inicio)} a ${formatShort(fim)}`;
};

// ========== CÁLCULOS ==========

/**
 * Calcula percentual de realização
 * @param {number} realizado - Valor realizado
 * @param {number} meta - Valor da meta
 * @returns {number} Percentual (0-100+)
 */
export const calcularPercentual = (realizado, meta) => {
  if (!meta || meta === 0) return 0;
  if (!realizado) return 0;
  
  return (realizado / meta) * 100;
};

/**
 * Calcula diferença absoluta entre meta e realizado
 * @param {number} realizado 
 * @param {number} meta 
 * @returns {number} Diferença (positiva = acima da meta)
 */
export const calcularDiferenca = (realizado, meta) => {
  if (!realizado) return -meta;
  if (!meta) return realizado;
  
  return realizado - meta;
};

/**
 * Calcula projeção baseada em tendência
 * @param {number} realizado - Valor realizado até o momento
 * @param {number} diasDecorridos - Dias já passados
 * @param {number} diasTotais - Total de dias do período
 * @returns {number} Valor projetado para o fim do período
 */
export const calcularProjecao = (realizado, diasDecorridos, diasTotais) => {
  if (!diasDecorridos || diasDecorridos === 0) return realizado;
  if (!diasTotais || diasTotais === 0) return realizado;
  
  const mediaDiaria = realizado / diasDecorridos;
  return mediaDiaria * diasTotais;
};

/**
 * Calcula média de um array de valores
 * @param {number[]} valores 
 * @returns {number} Média aritmética
 */
export const calcularMedia = (valores) => {
  if (!valores || valores.length === 0) return 0;
  
  const soma = valores.reduce((acc, val) => acc + (val || 0), 0);
  return soma / valores.length;
};

/**
 * Calcula taxa de crescimento percentual
 * @param {number} valorAtual 
 * @param {number} valorAnterior 
 * @returns {number} Taxa de crescimento em % (ex: 25 para 25% de crescimento)
 */
export const calcularTaxaCrescimento = (valorAtual, valorAnterior) => {
  if (!valorAnterior || valorAnterior === 0) {
    return valorAtual > 0 ? 100 : 0;
  }
  
  return ((valorAtual - valorAnterior) / valorAnterior) * 100;
};

// ========== STATUS E PERFORMANCE ==========

/**
 * Determina status de performance baseado em percentual
 * @param {number} percentual - Percentual de realização (0-100+)
 * @returns {string} Status: 'acima', 'meta', 'atencao', 'abaixo'
 */
export const obterStatusPerformance = (percentual) => {
  if (percentual >= PERFORMANCE_THRESHOLDS.ACIMA) return 'acima';
  if (percentual >= PERFORMANCE_THRESHOLDS.META) return 'meta';
  if (percentual >= PERFORMANCE_THRESHOLDS.ATENCAO) return 'atencao';
  return 'abaixo';
};

/**
 * Obtém ícone de emoji baseado em status
 * @param {string} status - 'acima', 'meta', 'atencao', 'abaixo'
 * @returns {string} Emoji correspondente
 */
export const obterIconeStatus = (status) => {
  const icones = {
    'acima': '✅',
    'meta': '🎯',
    'atencao': '⚠️',
    'abaixo': '🔴',
    'neutro': '➖'
  };
  
  return icones[status] || '❓';
};

/**
 * Obtém label descritivo de status
 * @param {string} status 
 * @returns {string} Label amigável
 */
export const obterLabelStatus = (status) => {
  const labels = {
    'acima': 'Acima da Meta',
    'meta': 'Na Meta',
    'atencao': 'Atenção',
    'abaixo': 'Abaixo da Meta',
    'neutro': 'Sem Dados'
  };
  
  return labels[status] || 'Desconhecido';
};

// ========== FUNÇÕES DE FASES ==========

/**
 * Obtém período de uma fase específica
 * @param {string} fase - Nome da fase (ex: "Fase 1")
 * @returns {string} Período formatado (ex: "01/ago a 14/set")
 */
export const getFasePeriodo = (fase) => {
  const config = FASES_CONFIG[fase];
  return config ? config.periodo : 'A definir';
};

/**
 * Calcula status atual de uma fase baseado em datas
 * @param {string} fase - Nome da fase
 * @returns {string} Status: 'planejada', 'em_execucao', 'concluida'
 */
export const getFaseStatus = (fase) => {
  const hoje = new Date();
  
  // Datas de referência (hardcoded por enquanto, pode vir da API futuramente)
  const periodos = {
    'Fase 1': { inicio: new Date('2025-08-01'), fim: new Date('2025-09-14') },
    'Fase 2': { inicio: new Date('2025-09-15'), fim: new Date('2025-10-29') },
    'Fase 3': { inicio: new Date('2025-10-30'), fim: new Date('2025-12-15') }
  };
  
  const periodo = periodos[fase];
  if (!periodo) return 'planejada';
  
  if (hoje >= periodo.inicio && hoje <= periodo.fim) return 'em_execucao';
  if (hoje > periodo.fim) return 'concluida';
  
  return 'planejada';
};

/**
 * Obtém período de uma parte específica da fase
 * @param {string} fase - Nome da fase
 * @param {number} part - Número da parte (1 ou 2)
 * @returns {string} Período da parte
 */
export const getPartPeriodo = (fase, part) => {
  const periodos = {
    'Fase 1': {
      1: '01/ago a 15/ago',
      2: '16/ago a 14/set'
    },
    'Fase 2': {
      1: '15/set a 29/set',
      2: '30/set a 29/out'
    },
    'Fase 3': {
      1: '30/out a 14/nov',
      2: '15/nov a 15/dez'
    }
  };
  
  return periodos[fase]?.[part] || 'A definir';
};

/**
 * Calcula status de uma parte específica da fase
 * @param {string} fase - Nome da fase
 * @param {number} part - Número da parte
 * @returns {string} Status da parte
 */
export const getPartStatus = (fase, part) => {
  const faseStatus = getFaseStatus(fase);
  
  if (faseStatus === 'em_execucao') {
    // Se fase está em execução, determinar qual parte está ativa
    // Por simplicidade, vamos assumar que part 1 é primeira metade
    return part === 1 ? 'concluindo' : 'iniciando';
  }
  
  if (faseStatus === 'concluida') return 'concluida';
  
  return 'aguardando';
};

// ========== VALIDAÇÕES ==========

/**
 * Valida se um valor é número válido
 * @param {any} valor 
 * @returns {boolean}
 */
export const isNumeroValido = (valor) => {
  return valor !== null && valor !== undefined && !isNaN(Number(valor));
};

/**
 * Valida se percentual está em range válido
 * @param {number} percentual 
 * @returns {boolean}
 */
export const isPercentualValido = (percentual) => {
  return isNumeroValido(percentual) && percentual >= 0 && percentual <= 1000; // Até 1000% para casos extremos
};

/**
 * Valida se data é válida
 * @param {Date|string} data 
 * @returns {boolean}
 */
export const isDataValida = (data) => {
  if (!data) return false;
  
  const date = typeof data === 'string' ? new Date(data) : data;
  return !isNaN(date.getTime());
};

// ========== MANIPULAÇÃO DE DADOS ==========

/**
 * Remove acentos de string (para normalização)
 * @param {string} str 
 * @returns {string} String sem acentos
 */
export const removerAcentos = (str) => {
  if (!str) return '';
  
  return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
};

/**
 * Normaliza nome de cidade (remove acentos, espaços extras, lowercase)
 * @param {string} nome 
 * @returns {string} Nome normalizado
 */
export const normalizarNomeCidade = (nome) => {
  if (!nome) return '';
  
  return removerAcentos(nome)
    .toLowerCase()
    .replace(/\s+/g, '')
    .trim();
};

/**
 * Agrupa array de objetos por chave
 * @param {Array} array 
 * @param {string} key - Chave para agrupar
 * @returns {Object} Objeto com arrays agrupados
 */
export const agruparPor = (array, key) => {
  if (!array || !Array.isArray(array)) return {};
  
  return array.reduce((result, item) => {
    const groupKey = item[key];
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {});
};

/**
 * Ordena array de objetos por campo
 * @param {Array} array 
 * @param {string} campo - Campo para ordenar
 * @param {string} ordem - 'asc' ou 'desc'
 * @returns {Array} Array ordenado
 */
export const ordenarPor = (array, campo, ordem = 'asc') => {
  if (!array || !Array.isArray(array)) return [];
  
  const sorted = [...array].sort((a, b) => {
    const valorA = a[campo];
    const valorB = b[campo];
    
    if (valorA === valorB) return 0;
    
    if (ordem === 'asc') {
      return valorA > valorB ? 1 : -1;
    } else {
      return valorA < valorB ? 1 : -1;
    }
  });
  
  return sorted;
};

/**
 * Filtra valores nulos/undefined de objeto
 * @param {Object} obj 
 * @returns {Object} Objeto sem valores nulos
 */
export const removerNulos = (obj) => {
  if (!obj || typeof obj !== 'object') return obj;
  
  return Object.fromEntries(
    Object.entries(obj).filter(([_, value]) => value !== null && value !== undefined)
  );
};

// ========== HELPERS DE COMPARAÇÃO ==========

/**
 * Compara dois valores numéricos com tolerância
 * @param {number} a 
 * @param {number} b 
 * @param {number} tolerancia - Tolerância percentual (default: 0.1%)
 * @returns {string} 'igual', 'maior', 'menor'
 */
export const compararValores = (a, b, tolerancia = 0.001) => {
  if (!isNumeroValido(a) || !isNumeroValido(b)) return 'indefinido';
  
  const diff = Math.abs(a - b);
  const maxVal = Math.max(Math.abs(a), Math.abs(b));
  const diffPercentual = maxVal > 0 ? diff / maxVal : 0;
  
  if (diffPercentual <= tolerancia) return 'igual';
  
  return a > b ? 'maior' : 'menor';
};

/**
 * Determina tendência baseado em série temporal
 * @param {number[]} valores - Array de valores em ordem cronológica
 * @returns {string} 'crescente', 'decrescente', 'estavel'
 */
export const calcularTendencia = (valores) => {
  if (!valores || valores.length < 2) return 'estavel';
  
  // Calcular média da primeira e segunda metade
  const meio = Math.floor(valores.length / 2);
  const primeiraMetade = valores.slice(0, meio);
  const segundaMetade = valores.slice(meio);
  
  const mediaPrimeira = calcularMedia(primeiraMetade);
  const mediaSegunda = calcularMedia(segundaMetade);
  
  const comparacao = compararValores(mediaSegunda, mediaPrimeira, 0.05); // 5% de tolerância
  
  if (comparacao === 'maior') return 'crescente';
  if (comparacao === 'menor') return 'decrescente';
  return 'estavel';
};

// ========== EXPORTS DEFAULT ==========

export default {
  // Formatação
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
  formatarData,
  formatarPeriodo,
  
  // Cálculos
  calcularPercentual,
  calcularDiferenca,
  calcularProjecao,
  calcularMedia,
  calcularTaxaCrescimento,
  
  // Status
  obterStatusPerformance,
  obterIconeStatus,
  obterLabelStatus,
  
  // Fases
  getFasePeriodo,
  getFaseStatus,
  getPartPeriodo,
  getPartStatus,
  
  // Validações
  isNumeroValido,
  isPercentualValido,
  isDataValida,
  
  // Manipulação
  removerAcentos,
  normalizarNomeCidade,
  agruparPor,
  ordenarPor,
  removerNulos,
  
  // Comparação
  compararValores,
  calcularTendencia
};
