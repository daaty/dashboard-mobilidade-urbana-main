// 🎯 COMPONENTE SEPARADO PARA GERENCIAR METAS ESTRATÉGICAS
// Interface completa de CRUD para metas progressivas e fases

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, Edit, Trash2, Save, X, Calendar, Target, TrendingUp, 
  BarChart3, MapPin, DollarSign, Users, Building2, AlertCircle,
  CheckCircle, Clock, Pause, Play, RotateCcw
} from 'lucide-react'
import { useMetasEstrategicas } from '../hooks/useMetasEstrategicas'

const GerenciadorMetasEstrategicas = ({ isOpen, onClose }) => {
  const {
    metasProgressivas,
    fasesEstrategicas,
    loading,
    error,
    criarMetaProgressiva,
    atualizarMetaProgressiva,
    deletarMetaProgressiva,
    limparMetasDuplicadas,
    criarFaseEstrategica,
    atualizarFaseEstrategica,
    deletarFaseEstrategica,
    obterEstatisticas,
    recarregarTudo
  } = useMetasEstrategicas()

  // Verificar se os dados estão prontos
  if (!metasProgressivas || !fasesEstrategicas) {
    return (
      <AnimatePresence>
        {isOpen && (
          <motion.div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-8">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p>Carregando dados estratégicos...</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    )
  }

  // Estados locais
  const [abaSelecionada, setAbaSelecionada] = useState('metas') // 'metas' | 'fases' | 'estatisticas'
  const [itemEditando, setItemEditando] = useState(null)
  const [showFormulario, setShowFormulario] = useState(false)
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)
  const [itemParaDeletar, setItemParaDeletar] = useState(null)
  const [filtros, setFiltros] = useState({ cidade: '', tipo: '', mes: '' })

  // Estados do formulário
  const [formData, setFormData] = useState({
    // Para metas progressivas
    cidade_id: '',
    cidade_nome: '',
    mes: 1,
    percentual_penetracao: 0,
    meta_corridas: 0,
    meta_motoristas: 0,
    meta_receita: 0,
    tipo_meta: 'media',
    // Para fases
    nome: '',
    descricao: '',
    data_inicio: '',
    data_fim: '',
    status: 'planejada',
    meta_cidades: 0,
    orcamento_previsto: 0,
    progresso_percentual: 0,
    ordem: 1
  })

  const estadisticas = obterEstatisticas ? obterEstatisticas() : {
    totalMetas: 0,
    totalCidades: 0, 
    totalFases: 0,
    fasesPorStatus: {}
  }

  // ========== FUNÇÕES DE FORMULÁRIO ==========

  const resetForm = () => {
    setFormData({
      cidade_id: '',
      cidade_nome: '',
      mes: 1,
      percentual_penetracao: 0,
      meta_corridas: 0,
      meta_motoristas: 0,
      meta_receita: 0,
      tipo_meta: 'media',
      nome: '',
      descricao: '',
      data_inicio: '',
      data_fim: '',
      status: 'planejada',
      meta_cidades: 0,
      orcamento_previsto: 0,
      progresso_percentual: 0,
      ordem: 1
    })
    setItemEditando(null)
  }

  const handleEdit = (item, tipo) => {
    setItemEditando({ ...item, tipo })
    if (tipo === 'meta') {
      setFormData({
        ...formData,
        cidade_id: item.cidade_id,
        cidade_nome: item.cidade_nome,
        mes: item.mes,
        percentual_penetracao: item.percentual_penetracao,
        meta_corridas: item.meta_corridas,
        meta_motoristas: item.meta_motoristas,
        meta_receita: item.meta_receita,
        tipo_meta: item.tipo_meta
      })
    } else {
      setFormData({
        ...formData,
        nome: item.nome,
        descricao: item.descricao,
        data_inicio: item.data_inicio,
        data_fim: item.data_fim,
        status: item.status,
        meta_cidades: item.meta_cidades,
        orcamento_previsto: item.orcamento_previsto,
        progresso_percentual: item.progresso_percentual,
        ordem: item.ordem
      })
    }
    setShowFormulario(true)
  }

  const handleSave = async () => {
    try {
      let resultado
      
      if (abaSelecionada === 'metas') {
        const metaData = {
          cidade_id: parseInt(formData.cidade_id),
          cidade_nome: formData.cidade_nome,
          mes: parseInt(formData.mes),
          percentual_penetracao: parseFloat(formData.percentual_penetracao),
          meta_corridas: parseInt(formData.meta_corridas),
          meta_motoristas: parseInt(formData.meta_motoristas),
          meta_receita: parseFloat(formData.meta_receita),
          tipo_meta: formData.tipo_meta
        }

        if (itemEditando) {
          resultado = await atualizarMetaProgressiva(itemEditando.id, metaData)
        } else {
          resultado = await criarMetaProgressiva(metaData)
        }
      } else {
        const faseData = {
          nome: formData.nome,
          descricao: formData.descricao,
          data_inicio: formData.data_inicio,
          data_fim: formData.data_fim,
          status: formData.status,
          meta_cidades: parseInt(formData.meta_cidades),
          orcamento_previsto: parseFloat(formData.orcamento_previsto),
          progresso_percentual: parseFloat(formData.progresso_percentual),
          ordem: parseInt(formData.ordem)
        }

        if (itemEditando) {
          resultado = await atualizarFaseEstrategica(itemEditando.id, faseData)
        } else {
          resultado = await criarFaseEstrategica(faseData)
        }
      }

      if (resultado.success) {
        setShowFormulario(false)
        resetForm()
      } else {
        alert(`Erro: ${resultado.error}`)
      }
    } catch (err) {
      alert(`Erro ao salvar: ${err.message}`)
    }
  }

  const handleDelete = async () => {
    try {
      let resultado
      
      if (itemParaDeletar.tipo === 'meta') {
        resultado = await deletarMetaProgressiva(itemParaDeletar.id)
      } else {
        resultado = await deletarFaseEstrategica(itemParaDeletar.id)
      }

      if (resultado.success) {
        setShowConfirmDelete(false)
        setItemParaDeletar(null)
      } else {
        alert(`Erro: ${resultado.error}`)
      }
    } catch (err) {
      alert(`Erro ao deletar: ${err.message}`)
    }
  }

  const handleLimparDuplicadas = async () => {
    if (confirm('Tem certeza que deseja limpar todas as metas duplicadas?')) {
      const resultado = await limparMetasDuplicadas()
      if (resultado.success) {
        alert(`${resultado.message}. Restam ${resultado.metasRestantes} metas únicas.`)
      } else {
        alert(`Erro: ${resultado.error}`)
      }
    }
  }

  // ========== FUNÇÕES DE FILTRO ==========

  const metasFiltradas = metasProgressivas.filter(meta => {
    // Filtrar por cidade
    if (filtros.cidade && !meta.cidade_nome.toLowerCase().includes(filtros.cidade.toLowerCase())) return false
    
    // Filtrar por tipo de meta
    if (filtros.tipo && meta.tipo_meta !== filtros.tipo) return false
    
    // Filtrar por mês
    if (filtros.mes && meta.mes !== parseInt(filtros.mes)) return false
    
    return true
  })

  // Agrupar metas por cidade
  const metasAgrupadasPorCidade = metasFiltradas.reduce((acc, meta) => {
    const cidadeNome = meta.cidade_nome
    if (!acc[cidadeNome]) {
      acc[cidadeNome] = {
        cidade_id: meta.cidade_id,
        cidade_nome: cidadeNome,
        metas: []
      }
    }
    acc[cidadeNome].metas.push(meta)
    return acc
  }, {})

  const cidadesComMetas = Object.values(metasAgrupadasPorCidade)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-7xl w-full mx-4 max-h-[95vh] overflow-hidden">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">🎯 Gerenciador de Metas Estratégicas</h2>
              <p className="text-purple-100">Interface completa de CRUD para metas progressivas e fases</p>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Abas */}
          <div className="flex gap-4 mt-6">
            {[
              { id: 'metas', label: 'Metas Progressivas', icon: Target },
              { id: 'fases', label: 'Fases Estratégicas', icon: Calendar },
              { id: 'estatisticas', label: 'Estatísticas', icon: BarChart3 }
            ].map(aba => (
              <button
                key={aba.id}
                onClick={() => setAbaSelecionada(aba.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  abaSelecionada === aba.id 
                    ? 'bg-white text-purple-600' 
                    : 'bg-purple-500/30 text-white hover:bg-purple-500/50'
                }`}
              >
                <aba.icon className="w-4 h-4" />
                {aba.label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(95vh-200px)]">
          
          {/* ABA: METAS PROGRESSIVAS */}
          {abaSelecionada === 'metas' && (
            <div className="space-y-6">
              
              {/* Controles */}
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => {
                      resetForm()
                      setShowFormulario(true)
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    <Plus className="w-4 h-4" />
                    Nova Meta
                  </button>
                  
                  <button
                    onClick={handleLimparDuplicadas}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Limpar Duplicadas
                  </button>
                </div>

                {/* Filtros */}
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    placeholder="Filtrar por cidade..."
                    value={filtros.cidade}
                    onChange={(e) => setFiltros({...filtros, cidade: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  
                  <select
                    value={filtros.tipo}
                    onChange={(e) => setFiltros({...filtros, tipo: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="">Todos os tipos</option>
                    <option value="muito_baixa">Muito Baixa</option>
                    <option value="baixa">Baixa</option>
                    <option value="media">Média</option>
                    <option value="alta">Alta</option>
                    <option value="agressiva">Agressiva</option>
                  </select>
                </div>
              </div>

              {/* Lista de Metas */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cidadesComMetas.length > 0 ? (
                  cidadesComMetas.map(cidade => (
                    <div key={cidade.cidade_id} className="bg-gray-50 rounded-xl p-4">
                      <h3 className="font-bold text-lg text-gray-800 mb-3">{cidade.cidade_nome}</h3>
                      
                      <div className="space-y-3">
                        {cidade.metas.map(meta => (
                          <div key={meta.id} className="bg-white rounded-lg p-3 border border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-600">Mês {meta.mes}</span>
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                meta.tipo_meta === 'agressiva' ? 'bg-red-100 text-red-700' :
                                meta.tipo_meta === 'alta' ? 'bg-orange-100 text-orange-700' :
                                meta.tipo_meta === 'media' ? 'bg-yellow-100 text-yellow-700' :
                                meta.tipo_meta === 'baixa' ? 'bg-blue-100 text-blue-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {meta.tipo_meta}
                              </span>
                            </div>
                            
                            <div className="text-sm text-gray-600 space-y-1">
                              <div>📊 {meta.percentual_penetracao}% penetração</div>
                              <div>🚕 {meta.meta_corridas} corridas</div>
                              <div>👨‍💼 {meta.meta_motoristas} motoristas</div>
                              <div>💰 R$ {meta.meta_receita?.toLocaleString()}</div>
                            </div>

                            <div className="flex gap-2 mt-3">
                              <button
                                onClick={() => handleEdit(meta, 'meta')}
                                className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => {
                                  setItemParaDeletar({...meta, tipo: 'meta'})
                                  setShowConfirmDelete(true)
                                }}
                                className="p-1 text-red-600 hover:bg-red-100 rounded"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="col-span-full text-center py-12">
                    <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg">Nenhuma meta encontrada</p>
                    <p className="text-gray-400">Ajuste os filtros ou adicione novas metas</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ABA: FASES ESTRATÉGICAS */}
          {abaSelecionada === 'fases' && (
            <div className="space-y-6">
              
              {/* Controles */}
              <div className="flex items-center justify-between">
                <button
                  onClick={() => {
                    resetForm()
                    setShowFormulario(true)
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <Plus className="w-4 h-4" />
                  Nova Fase
                </button>
              </div>

              {/* Lista de Fases */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {fasesEstrategicas.map(fase => (
                  <div key={fase.id} className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-bold text-lg text-gray-800">{fase.nome}</h3>
                      <div className={`px-3 py-1 rounded-full text-white text-sm ${
                        fase.status === 'em_execucao' ? 'bg-green-500' :
                        fase.status === 'planejada' ? 'bg-blue-500' :
                        fase.status === 'concluida' ? 'bg-gray-500' : 'bg-yellow-500'
                      }`}>
                        {fase.status === 'em_execucao' ? 'Em Execução' :
                         fase.status === 'planejada' ? 'Planejada' :
                         fase.status === 'concluida' ? 'Concluída' : 'Pausada'}
                      </div>
                    </div>

                    <p className="text-gray-600 text-sm mb-4">{fase.descricao}</p>

                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {fase.data_inicio ? new Date(fase.data_inicio).toLocaleDateString() : 'Sem data'} - 
                          {fase.data_fim ? new Date(fase.data_fim).toLocaleDateString() : 'Sem data'}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Building2 className="w-4 h-4" />
                        <span>Meta: {fase.meta_cidades} cidades</span>
                      </div>

                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <DollarSign className="w-4 h-4" />
                        <span>R$ {fase.orcamento_previsto?.toLocaleString()}</span>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Progresso</span>
                          <span className="font-bold">{fase.progresso_percentual?.toFixed(1) || 0}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                            style={{ width: `${fase.progresso_percentual || 0}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-4">
                      <button
                        onClick={() => handleEdit(fase, 'fase')}
                        className="p-2 text-blue-600 hover:bg-blue-100 rounded"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          setItemParaDeletar({...fase, tipo: 'fase'})
                          setShowConfirmDelete(true)
                        }}
                        className="p-2 text-red-600 hover:bg-red-100 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ABA: ESTATÍSTICAS */}
          {abaSelecionada === 'estatisticas' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-blue-50 rounded-xl p-6">
                  <div className="flex items-center gap-3">
                    <Target className="w-8 h-8 text-blue-600" />
                    <div>
                      <div className="text-2xl font-bold text-blue-800">{estadisticas.totalMetas}</div>
                      <div className="text-sm text-blue-600">Total de Metas</div>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 rounded-xl p-6">
                  <div className="flex items-center gap-3">
                    <MapPin className="w-8 h-8 text-green-600" />
                    <div>
                      <div className="text-2xl font-bold text-green-800">{estadisticas.totalCidades}</div>
                      <div className="text-sm text-green-600">Cidades Ativas</div>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 rounded-xl p-6">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-8 h-8 text-purple-600" />
                    <div>
                      <div className="text-2xl font-bold text-purple-800">{estadisticas.totalFases}</div>
                      <div className="text-sm text-purple-600">Fases Criadas</div>
                    </div>
                  </div>
                </div>

                <div className="bg-orange-50 rounded-xl p-6">
                  <div className="flex items-center gap-3">
                    <TrendingUp className="w-8 h-8 text-orange-600" />
                    <div>
                      <div className="text-2xl font-bold text-orange-800">
                        {estadisticas.fasesPorStatus?.em_execucao || 0}
                      </div>
                      <div className="text-sm text-orange-600">Em Execução</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Detalhamento por status */}
              <div className="bg-white rounded-xl p-6 border border-gray-200">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Fases por Status</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(estadisticas.fasesPorStatus).map(([status, quantidade]) => (
                    <div key={status} className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-bold text-gray-800">{quantidade}</div>
                      <div className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Botão de recarregar */}
              <div className="text-center">
                <button
                  onClick={recarregarTudo}
                  disabled={loading}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 mx-auto"
                >
                  <RotateCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  Recarregar Dados
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="absolute top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Modal de Formulário */}
      <AnimatePresence>
        {showFormulario && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6">
                <h3 className="text-xl font-bold mb-4">
                  {itemEditando ? 'Editar' : 'Criar'} {abaSelecionada === 'metas' ? 'Meta Progressiva' : 'Fase Estratégica'}
                </h3>

                {abaSelecionada === 'metas' ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Cidade ID</label>
                        <input
                          type="number"
                          value={formData.cidade_id}
                          onChange={(e) => setFormData({...formData, cidade_id: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Nome da Cidade</label>
                        <input
                          type="text"
                          value={formData.cidade_nome}
                          onChange={(e) => setFormData({...formData, cidade_nome: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Mês</label>
                        <input
                          type="number"
                          min="1"
                          max="24"
                          value={formData.mes}
                          onChange={(e) => setFormData({...formData, mes: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Penetração (%)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={formData.percentual_penetracao}
                          onChange={(e) => setFormData({...formData, percentual_penetracao: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Meta</label>
                        <select
                          value={formData.tipo_meta}
                          onChange={(e) => setFormData({...formData, tipo_meta: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        >
                          <option value="muito_baixa">Muito Baixa</option>
                          <option value="baixa">Baixa</option>
                          <option value="media">Média</option>
                          <option value="alta">Alta</option>
                          <option value="agressiva">Agressiva</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Meta Corridas</label>
                        <input
                          type="number"
                          value={formData.meta_corridas}
                          onChange={(e) => setFormData({...formData, meta_corridas: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Meta Motoristas</label>
                        <input
                          type="number"
                          value={formData.meta_motoristas}
                          onChange={(e) => setFormData({...formData, meta_motoristas: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Meta Receita (R$)</label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.meta_receita}
                          onChange={(e) => setFormData({...formData, meta_receita: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Nome da Fase</label>
                      <input
                        type="text"
                        value={formData.nome}
                        onChange={(e) => setFormData({...formData, nome: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Descrição</label>
                      <textarea
                        value={formData.descricao}
                        onChange={(e) => setFormData({...formData, descricao: e.target.value})}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Data Início</label>
                        <input
                          type="date"
                          value={formData.data_inicio}
                          onChange={(e) => setFormData({...formData, data_inicio: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Data Fim</label>
                        <input
                          type="date"
                          value={formData.data_fim}
                          onChange={(e) => setFormData({...formData, data_fim: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                        <select
                          value={formData.status}
                          onChange={(e) => setFormData({...formData, status: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        >
                          <option value="planejada">Planejada</option>
                          <option value="em_execucao">Em Execução</option>
                          <option value="pausada">Pausada</option>
                          <option value="concluida">Concluída</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Meta Cidades</label>
                        <input
                          type="number"
                          value={formData.meta_cidades}
                          onChange={(e) => setFormData({...formData, meta_cidades: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Orçamento (R$)</label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.orcamento_previsto}
                          onChange={(e) => setFormData({...formData, orcamento_previsto: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Progresso (%)</label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="100"
                          value={formData.progresso_percentual}
                          onChange={(e) => setFormData({...formData, progresso_percentual: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex justify-end gap-3 mt-6">
                  <button
                    onClick={() => {
                      setShowFormulario(false)
                      resetForm()
                    }}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleSave}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <Save className="w-4 h-4" />
                    Salvar
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal de Confirmação de Exclusão */}
      <AnimatePresence>
        {showConfirmDelete && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4"
            >
              <div className="p-6">
                <h3 className="text-xl font-bold text-red-600 mb-4">Confirmar Exclusão</h3>
                <p className="text-gray-600 mb-6">
                  Tem certeza que deseja excluir{' '}
                  {itemParaDeletar?.tipo === 'meta' 
                    ? `a meta do mês ${itemParaDeletar?.mes} de ${itemParaDeletar?.cidade_nome}`
                    : `a fase "${itemParaDeletar?.nome}"`
                  }?
                </p>
                <div className="flex justify-end gap-3">
                  <button
                    onClick={() => {
                      setShowConfirmDelete(false)
                      setItemParaDeletar(null)
                    }}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleDelete}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                    Excluir
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default GerenciadorMetasEstrategicas
