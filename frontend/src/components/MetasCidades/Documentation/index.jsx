/**
 * Índice de Componentes de Documentação Financeira
 * 
 * FASE 3: Sistema de Documentação Financeira
 * 
 * Componentes exportados:
 * - ExpenseDocumentation: Upload e gerenciamento de comprovantes
 * - BudgetTracker: Acompanhamento visual do orçamento (Previsto→Empenhado→Pago→Liquidado)
 * - ProgressIndicator: Indicador de progresso de metas (4 modos: bar/circle/card/inline)
 * - MultiProgressIndicator: Múltiplos indicadores de progresso
 * - AlertsPanel: Painel de alertas do sistema com filtros
 * 
 * @example
 * import { ExpenseDocumentation, BudgetTracker, ProgressIndicator, AlertsPanel } from './Documentation';
 * 
 * @example
 * // Integração com hooks
 * import { useMetasProgress } from './hooks';
 * const { data, loading } = useMetasProgress('Fase 1', true);
 */

// Componentes principais
export { default as ExpenseDocumentation } from './ExpenseDocumentation';
export { default as BudgetTracker } from './BudgetTracker';
export { default as ProgressIndicator, MultiProgressIndicator } from './ProgressIndicator';
export { default as AlertsPanel } from './AlertsPanel';

// Re-export tudo como objeto nomeado para conveniência
import ExpenseDocumentation from './ExpenseDocumentation';
import BudgetTracker from './BudgetTracker';
import ProgressIndicator, { MultiProgressIndicator } from './ProgressIndicator';
import AlertsPanel from './AlertsPanel';

export const Documentation = {
  ExpenseDocumentation,
  BudgetTracker,
  ProgressIndicator,
  MultiProgressIndicator,
  AlertsPanel,
};

export default Documentation;
