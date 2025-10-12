/**
 * Índice centralizado de todos os hooks customizados
 * Sistema de Integração de Metas
 */

// Hooks individuais
export { useDriversByCidade } from './useDriversByCidade.js';
export { useRidesByCidade } from './useRidesByCidade.js';
export { useCampaignExpenses } from './useCampaignExpenses.js';

// Hook master (recomendado para uso geral)
export { useMetasProgress } from './useMetasProgress.js';

// Hooks existentes
export { default as usePlanoDinamico } from './usePlanoDinamico.js';
export { useCruzamentoDados } from './useCruzamentoDados.js';

/**
 * GUIA DE USO:
 * 
 * 1. Para dados completos integrados (RECOMENDADO):
 *    import { useMetasProgress } from './hooks';
 *    const { data, loading, error } = useMetasProgress('Fase 1', true);
 * 
 * 2. Para dados específicos de motoristas:
 *    import { useDriversByCidade } from './hooks';
 *    const { data } = useDriversByCidade('Matupá', '3_months', true);
 * 
 * 3. Para dados específicos de corridas:
 *    import { useRidesByCidade } from './hooks';
 *    const { data } = useRidesByCidade('Matupá', '3_months', true);
 * 
 * 4. Para dados financeiros/campanhas:
 *    import { useCampaignExpenses } from './hooks';
 *    const { data } = useCampaignExpenses('Fase 1', 'Matupá', true);
 * 
 * PARÂMETROS:
 * - autoRefresh: true = polling automático a cada 5 minutos
 *                false = atualização manual via refresh()
 */
