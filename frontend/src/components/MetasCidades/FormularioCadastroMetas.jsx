import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  X,
  Building2,
  Target,
  Calendar,
  CheckCircle,
  Plus,
  Save
} from 'lucide-react'

/**
 * Formulário wizard multi-step para cadastro dinâmico de metas por cidades
 * 
 * Props:
 * - isOpen: boolean - Controle de visibilidade do modal
 * - onClose: function - Callback para fechar o modal
 * - onSave: function - Callback para salvar os dados do formulário
 * - kpisGerais: object - Dados gerais de KPIs para preview (ex: totalCidades)
 */
const FormularioCadastroMetas = ({ isOpen, onClose, onSave, kpisGerais }) => {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    // DADOS DA CIDADE
    cidade: {
      nome: '',
      populacao: 0,
      publico_alvo: 0,
      regiao: '',
      coordenadas: { lat: 0, lng: 0 }
    },
    // DADOS DA META
    meta: {
      motoristas: 0,
      corridas: 0,
      data_inicio: '',
      data_fim: '',
      orcamento_total: 0,
      responsavel: ''
    },
    // DADOS DA FASE CUSTOMIZADA
    fase: {
      nome: '',
      descricao: '',
      partes: [
        { nome: 'Part 1', tipo: 'motoristas', duracao_dias: 15, meta_especifica: 0 },
        { nome: 'Part 2', tipo: 'corridas', duracao_dias: 30, meta_especifica: 0 }
      ]
    },
    // CAMPANHAS VINCULADAS
    campanhas: []
  })

  const handleInputChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: { ...prev[section], [field]: value }
    }))
  }

  const adicionarParte = () => {
    setFormData(prev => ({
      ...prev,
      fase: {
        ...prev.fase,
        partes: [...prev.fase.partes, { 
          nome: `Part ${prev.fase.partes.length + 1}`, 
          tipo: 'corridas', 
          duracao_dias: 30, 
          meta_especifica: 0 
        }]
      }
    }))
  }

  const removerParte = (index) => {
    setFormData(prev => ({
      ...prev,
      fase: {
        ...prev.fase,
        partes: prev.fase.partes.filter((_, i) => i !== index)
      }
    }))
  }

  const handleSave = async () => {
    try {
      // Aqui vai a chamada para a API
      console.log('📋 SALVANDO DADOS:', formData)
      
      // Simular salvamento
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      onSave(formData)
      onClose()
      
      // Reset form
      setFormData({
        cidade: { nome: '', populacao: 0, publico_alvo: 0, regiao: '', coordenadas: { lat: 0, lng: 0 } },
        meta: { motoristas: 0, corridas: 0, data_inicio: '', data_fim: '', orcamento_total: 0, responsavel: '' },
        fase: { nome: '', descricao: '', partes: [
          { nome: 'Part 1', tipo: 'motoristas', duracao_dias: 15, meta_especifica: 0 },
          { nome: 'Part 2', tipo: 'corridas', duracao_dias: 30, meta_especifica: 0 }
        ]},
        campanhas: []
      })
      setStep(1)
    } catch (error) {
      console.error('Erro ao salvar:', error)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">🚀 Cadastro Dinâmico de Metas</h2>
              <p className="text-blue-100">Sistema escalável para {(kpisGerais?.totalCidades ?? 0)}+ cidades</p>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg">
              <X className="w-6 h-6" />
            </button>
          </div>
          
          {/* Steps */}
          <div className="flex items-center gap-4 mt-6">
            {[1,2,3,4].map(num => (
              <div key={num} className={`flex items-center gap-2 ${step >= num ? 'text-white' : 'text-blue-300'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  step >= num ? 'bg-white text-blue-600' : 'bg-blue-500'
                }`}>
                  {num}
                </div>
                <span className="text-sm">
                  {num === 1 ? 'Cidade' : num === 2 ? 'Metas' : num === 3 ? 'Fases' : 'Campanhas'}
                </span>
                {num < 4 && <div className="w-4 h-px bg-blue-300"></div>}
              </div>
            ))}
          </div>
        </div>

        <div className="p-6">
          
          {/* STEP 1: DADOS DA CIDADE */}
          {step === 1 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-blue-600" />
                Dados da Cidade
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nome da Cidade</label>
                  <input
                    type="text"
                    value={formData.cidade.nome}
                    onChange={(e) => handleInputChange('cidade', 'nome', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Ex: São Paulo"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">População Total</label>
                  <input
                    type="number"
                    value={formData.cidade.populacao}
                    onChange={(e) => handleInputChange('cidade', 'populacao', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Ex: 12000000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Público-Alvo (Estimado)</label>
                  <input
                    type="number"
                    value={formData.cidade.publico_alvo}
                    onChange={(e) => handleInputChange('cidade', 'publico_alvo', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Ex: 5000000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Região</label>
                  <select
                    value={formData.cidade.regiao}
                    onChange={(e) => handleInputChange('cidade', 'regiao', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Selecione a região</option>
                    <option value="Norte">Norte</option>
                    <option value="Nordeste">Nordeste</option>
                    <option value="Centro-Oeste">Centro-Oeste</option>
                    <option value="Sudeste">Sudeste</option>
                    <option value="Sul">Sul</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-800 mb-2">📊 Preview dos Dados Demográficos</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">População:</span>
                    <div className="font-bold">{formData.cidade.populacao.toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Público-Alvo:</span>
                    <div className="font-bold">{formData.cidade.publico_alvo.toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Penetração Inicial:</span>
                    <div className="font-bold">0.5%</div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 2: METAS */}
          {step === 2 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-green-600" />
                Definir Metas para {formData.cidade.nome || 'a Cidade'}
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Meta de Motoristas</label>
                  <input
                    type="number"
                    value={formData.meta.motoristas}
                    onChange={(e) => handleInputChange('meta', 'motoristas', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Ex: 50"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Meta de Corridas</label>
                  <input
                    type="number"
                    value={formData.meta.corridas}
                    onChange={(e) => handleInputChange('meta', 'corridas', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Ex: 1000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Data de Início</label>
                  <input
                    type="date"
                    value={formData.meta.data_inicio}
                    onChange={(e) => handleInputChange('meta', 'data_inicio', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Data de Fim</label>
                  <input
                    type="date"
                    value={formData.meta.data_fim}
                    onChange={(e) => handleInputChange('meta', 'data_fim', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Orçamento Total (R$)</label>
                  <input
                    type="number"
                    value={formData.meta.orcamento_total}
                    onChange={(e) => handleInputChange('meta', 'orcamento_total', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Ex: 50000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Responsável</label>
                  <input
                    type="text"
                    value={formData.meta.responsavel}
                    onChange={(e) => handleInputChange('meta', 'responsavel', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Ex: João Silva"
                  />
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <h4 className="font-medium text-green-800 mb-2">🎯 Preview das Metas</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">CAC por Motorista:</span>
                    <div className="font-bold">
                      R$ {formData.meta.motoristas > 0 ? (formData.meta.orcamento_total / formData.meta.motoristas).toFixed(2) : '0.00'}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Receita Estimada (Anual):</span>
                    <div className="font-bold">
                      R$ {(formData.meta.corridas * 2.5 * 12).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 3: FASES CUSTOMIZADAS */}
          {step === 3 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-600" />
                Configurar Fases Customizadas
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nome da Fase</label>
                  <input
                    type="text"
                    value={formData.fase.nome}
                    onChange={(e) => handleInputChange('fase', 'nome', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Ex: Lançamento Monte Verde"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Descrição</label>
                  <textarea
                    value={formData.fase.descricao}
                    onChange={(e) => handleInputChange('fase', 'descricao', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    rows="3"
                    placeholder="Descreva os objetivos desta fase..."
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-800">Partes da Fase</h4>
                    <button
                      onClick={adicionarParte}
                      className="flex items-center gap-2 px-3 py-1 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
                    >
                      <Plus className="w-4 h-4" />
                      Adicionar Parte
                    </button>
                  </div>
                  
                  {formData.fase.partes.map((parte, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-lg mb-3">
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="font-medium">Parte {index + 1}</h5>
                        {formData.fase.partes.length > 1 && (
                          <button
                            onClick={() => removerParte(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">Nome</label>
                          <input
                            type="text"
                            value={parte.nome}
                            onChange={(e) => {
                              const novasPartes = [...formData.fase.partes]
                              novasPartes[index].nome = e.target.value
                              handleInputChange('fase', 'partes', novasPartes)
                            }}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">Tipo</label>
                          <select
                            value={parte.tipo}
                            onChange={(e) => {
                              const novasPartes = [...formData.fase.partes]
                              novasPartes[index].tipo = e.target.value
                              handleInputChange('fase', 'partes', novasPartes)
                            }}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                          >
                            <option value="motoristas">Motoristas</option>
                            <option value="corridas">Corridas</option>
                            <option value="promocional">Promocional</option>
                            <option value="engajamento">Engajamento</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">Duração (dias)</label>
                          <input
                            type="number"
                            value={parte.duracao_dias}
                            onChange={(e) => {
                              const novasPartes = [...formData.fase.partes]
                              novasPartes[index].duracao_dias = parseInt(e.target.value) || 0
                              handleInputChange('fase', 'partes', novasPartes)
                            }}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 4: RESUMO */}
          {step === 4 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Resumo do Cadastro
              </h3>
              
              <div className="space-y-6">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-800 mb-2">🏙️ Cidade</h4>
                  <div className="text-sm space-y-1">
                    <div><strong>Nome:</strong> {formData.cidade.nome}</div>
                    <div><strong>População:</strong> {formData.cidade.populacao.toLocaleString()}</div>
                    <div><strong>Público-Alvo:</strong> {formData.cidade.publico_alvo.toLocaleString()}</div>
                    <div><strong>Região:</strong> {formData.cidade.regiao}</div>
                  </div>
                </div>

                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">🎯 Metas</h4>
                  <div className="text-sm space-y-1">
                    <div><strong>Motoristas:</strong> {formData.meta.motoristas}</div>
                    <div><strong>Corridas:</strong> {formData.meta.corridas}</div>
                    <div><strong>Período:</strong> {formData.meta.data_inicio} a {formData.meta.data_fim}</div>
                    <div><strong>Orçamento:</strong> R$ {formData.meta.orcamento_total.toLocaleString()}</div>
                    <div><strong>Responsável:</strong> {formData.meta.responsavel}</div>
                  </div>
                </div>

                <div className="p-4 bg-purple-50 rounded-lg">
                  <h4 className="font-medium text-purple-800 mb-2">📅 Fase: {formData.fase.nome}</h4>
                  <div className="text-sm space-y-1">
                    <div><strong>Descrição:</strong> {formData.fase.descricao}</div>
                    <div><strong>Partes:</strong></div>
                    {formData.fase.partes.map((parte, index) => (
                      <div key={index} className="ml-4">
                        • {parte.nome} ({parte.tipo}) - {parte.duracao_dias} dias
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <button
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              ← Anterior
            </button>
            
            <div className="flex gap-2">
              {step < 4 ? (
                <button
                  onClick={() => setStep(Math.min(4, step + 1))}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Próximo →
                </button>
              ) : (
                <button
                  onClick={handleSave}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  Salvar Meta
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FormularioCadastroMetas
