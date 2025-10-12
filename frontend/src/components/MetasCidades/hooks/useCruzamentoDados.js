import { useMemo } from 'react'

/**
 * Hook para cruzamento de dados entre Campanhas, Demografia e Plano Financeiro
 * 
 * @param {Object} params - Parâmetros do hook
 * @param {Object} params.planoExecucao - Plano dinâmico de execução por fases
 * @param {Array} params.campanhas - Lista de campanhas ativas
 * @param {Array} params.cidadesData - Dados demográficos das cidades
 * @param {Object} params.corridasReais - Dados reais de corridas por cidade
 * @param {Object} params.motoristasReais - Dados reais de motoristas por cidade
 * 
 * @returns {Object} { dadosCruzados, hasDados }
 */
export const useCruzamentoDados = ({
  planoExecucao = {},
  campanhas = [],
  cidadesData = [],
  corridasReais = {},
  motoristasReais = {}
}) => {
  
  const dadosCruzados = useMemo(() => {
    const resultado = []
    
    // 🔥 USAR PLANO DINÂMICO para cruzar com dados reais
    Object.entries(planoExecucao).forEach(([fase, dadosFase]) => {
      if (!dadosFase.cidades) return
      
      dadosFase.cidades.forEach(cidade => {
        // 1. DADOS REAIS DAS CAMPANHAS (API) - BUSCAR POR CIDADE REAL
        const campanhasCidade = campanhas.filter(c => (c.cidade?.nome || c.cidade) === cidade)
        
        // 2. DADOS DEMOGRÁFICOS DA TABELA CidadesDemografia
        const demograficos = cidadesData.find(c => (c.nome || c.cidade) === cidade) || {}
        
        // 3. DADOS DO PLANO FINANCEIRO DINÂMICO
        const metaMotoristas = dadosFase.part1?.metas?.[cidade] || 0
        const metaCorridas = dadosFase.part2?.metas?.[cidade] || 0
        
        // 4. 🔥 BUSCAR DADOS REAIS DE CORRIDAS E MOTORISTAS
        const cidadeNormalizada = cidade.toLowerCase().trim()
        
        const corridasReaisCidade = corridasReais[cidadeNormalizada]?.concluidas || 0
        const motoristasRealCidade = motoristasReais[cidadeNormalizada]?.ativos || 0
        
        // Calcular realizado baseado nos dados reais
        const realizadoMotoristas = motoristasRealCidade
        const realizadoCorridas = corridasReaisCidade
        
        // 5. 🔥 STATUS EXECUÇÃO BASEADO EM DADOS REAIS
        let statusExecucao = 'Aguardando início'
        const campanhasAtivas = campanhasCidade.length
        
        if (corridasReaisCidade > 0) {
          const percentualCorridas = metaCorridas > 0 ? (corridasReaisCidade / metaCorridas) * 100 : 0
          statusExecucao = `${Math.round(percentualCorridas)}% concluído (${corridasReaisCidade}/${metaCorridas})`
        } else if (campanhasAtivas > 0) {
          statusExecucao = 'Campanhas ativas - aguardando dados'
        }
        
        // 6. CRUZAMENTO FINANCEIRO DINÂMICO
        const orcamentoEmpenhado = dadosFase.orcamento?.empenhado || 0
        const orcamentoPago = dadosFase.orcamento?.pagamento || 0
        const orcamentoPrevisto = dadosFase.orcamento?.previsto || 0
        
        // 7. 🔥 DADOS DEMOGRÁFICOS + PENETRAÇÃO REAL
        const populacao = demograficos.populacao_estimada_2024 || demograficos.populacao || 15000
        const publicoAlvo = demograficos.publico_alvo_15_44_anos || demograficos.publico_alvo || 6500
        const penetracaoAtual = publicoAlvo > 0 ? (realizadoCorridas / publicoAlvo * 100) : 0
        
        // 8. 🎯 RECEITA BASEADA EM DADOS REAIS
        // Corridas dos últimos 45 dias (1,5 mês) -> calcular receita mensal
        const corridasRealizadas45Dias = realizadoCorridas
        const receitaMensal = (corridasRealizadas45Dias / 1.5) * 2.5 // Corridas/mês * R$ 2,50
        const receitaReal = Math.round(receitaMensal)
        
        resultado.push({
          fase,
          cidade,
          populacao,
          publico_alvo: publicoAlvo,
          campanhas_ativas: campanhasAtivas,
          // PLANO DINÂMICO
          meta_motoristas: metaMotoristas,
          meta_corridas: metaCorridas,
          // EXECUÇÃO REAL
          realizado_motoristas: realizadoMotoristas,
          realizado_corridas: realizadoCorridas,
          percentual_motoristas: metaMotoristas > 0 ? (realizadoMotoristas / metaMotoristas * 100) : 0,
          percentual_corridas: metaCorridas > 0 ? (realizadoCorridas / metaCorridas * 100) : 0,
          // FINANCEIRO DINÂMICO
          orcamento_empenhado: orcamentoEmpenhado,
          orcamento_pago: orcamentoPago,
          orcamento_previsto: orcamentoPrevisto,
          // PENETRAÇÃO
          penetracao_atual: penetracaoAtual,
          receita_estimada: receitaReal,
          // STATUS
          status_execucao: statusExecucao,
          periodo: dadosFase.periodo,
          fase_status: dadosFase.status
        })
      })
    })
    
    return resultado
  }, [planoExecucao, campanhas, cidadesData, corridasReais, motoristasReais])
  
  return {
    dadosCruzados,
    hasDados: dadosCruzados.length > 0,
    totalCidades: dadosCruzados.length,
    totalCampanhasAtivas: dadosCruzados.reduce((sum, d) => sum + d.campanhas_ativas, 0)
  }
}

export default useCruzamentoDados
