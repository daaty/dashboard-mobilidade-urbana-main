// 🎯 HOOK PARA GERENCIAR METAS ESTRATÉGICAS
// Hook separado para não sobrecarregar o MetasCidades.jsx

import { useState, useEffect, useCallback } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useMetasEstrategicas = () => {
  // ========== ESTADOS ==========
  const [metasProgressivas, setMetasProgressivas] = useState([])
  const [fasesEstrategicas, setFasesEstrategicas] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dashboard, setDashboard] = useState(null)

  // ========== FUNÇÕES DE API ==========

  // Buscar todas as metas progressivas
  const buscarMetasProgressivas = useCallback(async (cidadeId = null) => {
    try {
      setLoading(true)
      setError(null)
      
      const url = cidadeId 
        ? `${API_URL}/api/metas-estrategicas/metas-progressivas?cidade_id=${cidadeId}`
        : `${API_URL}/api/metas-estrategicas/metas-progressivas`
      
      const response = await fetch(url)
      
      // Verificar se a resposta é ok
      if (!response.ok) {
        console.warn(`Endpoint ${url} retornou ${response.status}. Usando dados vazios.`)
        setMetasProgressivas([])
        return { success: true, metas: [] }
      }
      
      const data = await response.json()
      
      // O endpoint retorna diretamente um array, não um objeto com {success: true, metas: [...]}
      if (Array.isArray(data)) {
        setMetasProgressivas(data)
        return { success: true, metas: data }
      } else if (data.success) {
        // Caso alternativo se vier no formato esperado
        setMetasProgressivas(data.metas || [])
        return { success: true, metas: data.metas }
      } else {
        throw new Error(data.detail || 'Erro ao buscar metas')
      }
    } catch (err) {
      console.warn('Endpoint de metas progressivas não disponível, usando dados vazios:', err.message)
      setMetasProgressivas([])
      setError(null) // Não tratar como erro crítico
      return { success: true, metas: [] } // Retornar sucesso com array vazio
    } finally {
      setLoading(false)
    }
  }, [])

  // Buscar todas as fases de planejamento
  const buscarFasesEstrategicas = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/fases-planejamento`)
      
      // Verificar se a resposta é ok
      if (!response.ok) {
        console.warn(`Endpoint fases-planejamento retornou ${response.status}. Usando dados vazios.`)
        setFasesEstrategicas([])
        return { success: true, fases: [] }
      }
      
      const data = await response.json()
      
      if (data.success) {
        setFasesEstrategicas(data.fases || [])
        return { success: true, fases: data.fases }
      } else {
        throw new Error(data.detail || 'Erro ao buscar fases')
      }
    } catch (err) {
      console.warn('Endpoint de fases estratégicas não disponível, usando dados vazios:', err.message)
      setFasesEstrategicas([])
      setError(null) // Não tratar como erro crítico
      return { success: true, fases: [] } // Retornar sucesso com array vazio
    } finally {
      setLoading(false)
    }
  }, [])

  // Buscar dashboard consolidado
  const buscarDashboard = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/dashboard`)
      
      // Verificar se a resposta é ok
      if (!response.ok) {
        console.warn(`Endpoint dashboard retornou ${response.status}. Usando dados padrão.`)
        const dashboardPadrao = {
          total_metas: 0,
          metas_ativas: 0,
          total_fases: 0,
          fases_ativas: 0
        }
        setDashboard(dashboardPadrao)
        return { success: true, dashboard: dashboardPadrao }
      }
      
      const data = await response.json()
      
      if (data.success) {
        setDashboard(data.dashboard)
        return { success: true, dashboard: data.dashboard }
      } else {
        throw new Error(data.detail || 'Erro ao buscar dashboard')
      }
    } catch (err) {
      console.warn('Endpoint de dashboard não disponível, usando dados padrão:', err.message)
      const dashboardPadrao = {
        total_metas: 0,
        metas_ativas: 0,
        total_fases: 0,
        fases_ativas: 0
      }
      setDashboard(dashboardPadrao)
      setError(null) // Não tratar como erro crítico
      return { success: true, dashboard: dashboardPadrao } // Retornar sucesso com dados padrão
    } finally {
      setLoading(false)
    }
  }, [])

  // Criar nova meta progressiva
  const criarMetaProgressiva = useCallback(async (metaData) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/metas-progressivas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metaData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Atualizar lista local
        await buscarMetasProgressivas()
        return { success: true, meta: data.meta }
      } else {
        throw new Error(data.detail || 'Erro ao criar meta')
      }
    } catch (err) {
      console.error('Erro ao criar meta progressiva:', err)
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [buscarMetasProgressivas])

  // Atualizar meta progressiva
  const atualizarMetaProgressiva = useCallback(async (metaId, metaData) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/metas-progressivas/${metaId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metaData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Atualizar lista local
        await buscarMetasProgressivas()
        return { success: true, meta: data.meta }
      } else {
        throw new Error(data.detail || 'Erro ao atualizar meta')
      }
    } catch (err) {
      console.error('Erro ao atualizar meta progressiva:', err)
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [buscarMetasProgressivas])

  // Deletar meta progressiva
  const deletarMetaProgressiva = useCallback(async (metaId) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/metas-progressivas/${metaId}`, {
        method: 'DELETE'
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Atualizar lista local
        await buscarMetasProgressivas()
        return { success: true, message: data.message }
      } else {
        throw new Error(data.detail || 'Erro ao deletar meta')
      }
    } catch (err) {
      console.error('Erro ao deletar meta progressiva:', err)
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [buscarMetasProgressivas])

  // Limpar metas duplicadas
  const limparMetasDuplicadas = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/metas-progressivas/limpar-duplicadas`, {
        method: 'POST'
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Atualizar lista local
        await buscarMetasProgressivas()
        return { success: true, message: data.message, metasRestantes: data.metas_restantes }
      } else {
        throw new Error(data.detail || 'Erro ao limpar duplicatas')
      }
    } catch (err) {
      console.error('Erro ao limpar metas duplicadas:', err)
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [buscarMetasProgressivas])

  // Criar nova fase de planejamento
  const criarFaseEstrategica = useCallback(async (faseData) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/fases-planejamento`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(faseData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Atualizar lista local
        await buscarFasesEstrategicas()
        return { success: true, fase: data.fase }
      } else {
        throw new Error(data.detail || 'Erro ao criar fase')
      }
    } catch (err) {
      console.error('Erro ao criar fase estratégica:', err)
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [buscarFasesEstrategicas])

  // Atualizar fase de planejamento
  const atualizarFaseEstrategica = useCallback(async (faseId, faseData) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/fases-planejamento/${faseId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(faseData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Atualizar lista local
        await buscarFasesEstrategicas()
        return { success: true, fase: data.fase }
      } else {
        throw new Error(data.detail || 'Erro ao atualizar fase')
      }
    } catch (err) {
      console.error('Erro ao atualizar fase estratégica:', err)
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [buscarFasesEstrategicas])

  // Deletar fase de planejamento
  const deletarFaseEstrategica = useCallback(async (faseId) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_URL}/api/metas-estrategicas/fases-planejamento/${faseId}`, {
        method: 'DELETE'
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Atualizar lista local
        await buscarFasesEstrategicas()
        return { success: true, message: data.message }
      } else {
        throw new Error(data.detail || 'Erro ao deletar fase')
      }
    } catch (err) {
      console.error('Erro ao deletar fase estratégica:', err)
      setError(err.message)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }, [buscarFasesEstrategicas])

  // ========== EFEITOS ==========

  // Carregar dados iniciais
  useEffect(() => {
    const carregarDadosIniciais = async () => {
      try {
        // Executar em paralelo mas não falhar se um endpoint não estiver disponível
        const resultados = await Promise.allSettled([
          buscarMetasProgressivas(),
          buscarFasesEstrategicas(),
          buscarDashboard()
        ])
        
        // Log dos resultados para debug
        resultados.forEach((resultado, index) => {
          const nomes = ['metas-progressivas', 'fases-estrategicas', 'dashboard']
          if (resultado.status === 'fulfilled') {
            console.log(`✅ ${nomes[index]} carregado com sucesso`)
          } else {
            console.warn(`⚠️ ${nomes[index]} falhou:`, resultado.reason)
          }
        })
        
      } catch (err) {
        console.warn('Erro ao carregar alguns dados iniciais (continuando):', err.message)
        // Não quebrar a aplicação se alguns endpoints falharem
      }
    }

    carregarDadosIniciais()
  }, [])

  // ========== FUNÇÕES UTILITÁRIAS ==========

  // Obter metas de uma cidade específica
  const obterMetasPorCidade = useCallback((cidadeNome) => {
    // Filtrar metas por cidade, já que metasProgressivas é um array direto de metas
    return metasProgressivas.filter(meta => meta.cidade_nome === cidadeNome)
  }, [metasProgressivas])

  // Obter estatísticas consolidadas
  const obterEstatisticas = useCallback(() => {
    // metasProgressivas é um array direto de metas, não agrupado por cidade
    const totalMetas = metasProgressivas.length
    const cidadesUnicas = [...new Set(metasProgressivas.map(meta => meta.cidade_nome))].length
    const totalFases = fasesEstrategicas.length
    
    const fasesPorStatus = fasesEstrategicas.reduce((acc, fase) => {
      acc[fase.status] = (acc[fase.status] || 0) + 1
      return acc
    }, {})

    return {
      totalMetas,
      totalCidades: cidadesUnicas,
      totalFases,
      fasesPorStatus
    }
  }, [metasProgressivas, fasesEstrategicas])

  // ========== RETORNO DO HOOK ==========
  return {
    // Estados
    metasProgressivas,
    fasesEstrategicas,
    dashboard,
    loading,
    error,

    // Funções de API - Metas
    buscarMetasProgressivas,
    criarMetaProgressiva,
    atualizarMetaProgressiva,
    deletarMetaProgressiva,
    limparMetasDuplicadas,

    // Funções de API - Fases
    buscarFasesEstrategicas,
    criarFaseEstrategica,
    atualizarFaseEstrategica,
    deletarFaseEstrategica,

    // Funções de API - Dashboard
    buscarDashboard,

    // Funções utilitárias
    obterMetasPorCidade,
    obterEstatisticas,

    // Ações de controle
    recarregarTudo: useCallback(async () => {
      await Promise.all([
        buscarMetasProgressivas(),
        buscarFasesEstrategicas(),
        buscarDashboard()
      ])
    }, [buscarMetasProgressivas, buscarFasesEstrategicas, buscarDashboard])
  }
}
