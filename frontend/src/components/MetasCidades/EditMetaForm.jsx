import React, { useState } from 'react'
import { Save, Users, DollarSign, Car } from 'lucide-react'

/**
 * Formulário de edição de meta progressiva
 * Permite editar metas mensais de corridas, motoristas e receita
 * 
 * Props:
 * - meta: object - Meta a ser editada
 * - onSave: function - Callback para salvar alterações
 * - onCancel: function - Callback para cancelar edição
 */
const EditMetaForm = ({ meta, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    id: meta.id,
    cidade_nome: meta.cidade_nome,
    tipo_meta: meta.tipo_meta,
    meta_corridas: meta.meta_corridas || 0,
    meta_motoristas: meta.meta_motoristas || 0,
    meta_receita: meta.meta_receita || 0,
    mes: meta.mes || 1,
    ano: meta.ano || new Date().getFullYear(),
    observacoes: meta.observacoes || ''
  })

  const [errors, setErrors] = useState({})

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.cidade_nome?.trim()) {
      newErrors.cidade_nome = 'Nome da cidade é obrigatório'
    }
    if (!formData.tipo_meta) {
      newErrors.tipo_meta = 'Tipo de meta é obrigatório'
    }
    if (formData.meta_corridas < 0) {
      newErrors.meta_corridas = 'Meta de corridas deve ser maior ou igual a 0'
    }
    if (formData.meta_motoristas < 0) {
      newErrors.meta_motoristas = 'Meta de motoristas deve ser maior ou igual a 0'
    }
    if (formData.meta_receita < 0) {
      newErrors.meta_receita = 'Meta de receita deve ser maior ou igual a 0'
    }
    if (formData.mes < 1 || formData.mes > 12) {
      newErrors.mes = 'Mês deve estar entre 1 e 12'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validateForm()) {
      onSave(formData)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Informações Básicas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cidade
          </label>
          <input
            type="text"
            value={formData.cidade_nome}
            onChange={(e) => handleInputChange('cidade_nome', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.cidade_nome ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.cidade_nome && (
            <p className="text-red-500 text-xs mt-1">{errors.cidade_nome}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Meta
          </label>
          <select
            value={formData.tipo_meta}
            onChange={(e) => handleInputChange('tipo_meta', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.tipo_meta ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Selecione...</option>
            <option value="muito_baixa">Muito Baixa</option>
            <option value="baixa">Baixa</option>
            <option value="media">Média</option>
            <option value="alta">Alta</option>
            <option value="agressiva">Agressiva</option>
          </select>
          {errors.tipo_meta && (
            <p className="text-red-500 text-xs mt-1">{errors.tipo_meta}</p>
          )}
        </div>
      </div>

      {/* Metas Numéricas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center gap-2">
              <Car className="w-4 h-4" />
              Meta de Corridas
            </div>
          </label>
          <input
            type="number"
            min="0"
            value={formData.meta_corridas}
            onChange={(e) => handleInputChange('meta_corridas', parseInt(e.target.value) || 0)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.meta_corridas ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.meta_corridas && (
            <p className="text-red-500 text-xs mt-1">{errors.meta_corridas}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Meta de Motoristas
            </div>
          </label>
          <input
            type="number"
            min="0"
            value={formData.meta_motoristas}
            onChange={(e) => handleInputChange('meta_motoristas', parseInt(e.target.value) || 0)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.meta_motoristas ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.meta_motoristas && (
            <p className="text-red-500 text-xs mt-1">{errors.meta_motoristas}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Meta de Receita (R$)
            </div>
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            value={formData.meta_receita}
            onChange={(e) => handleInputChange('meta_receita', parseFloat(e.target.value) || 0)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.meta_receita ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.meta_receita && (
            <p className="text-red-500 text-xs mt-1">{errors.meta_receita}</p>
          )}
        </div>
      </div>

      {/* Período */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mês
          </label>
          <select
            value={formData.mes}
            onChange={(e) => handleInputChange('mes', parseInt(e.target.value))}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.mes ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                {new Date(2025, i, 1).toLocaleDateString('pt-BR', { month: 'long' })}
              </option>
            ))}
          </select>
          {errors.mes && (
            <p className="text-red-500 text-xs mt-1">{errors.mes}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ano
          </label>
          <input
            type="number"
            min="2024"
            max="2030"
            value={formData.ano}
            onChange={(e) => handleInputChange('ano', parseInt(e.target.value) || new Date().getFullYear())}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Observações */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Observações
        </label>
        <textarea
          rows="3"
          value={formData.observacoes}
          onChange={(e) => handleInputChange('observacoes', e.target.value)}
          placeholder="Adicione observações sobre esta meta..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Prévia dos dados calculados */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-800 mb-3">Prévia dos Resultados</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Eficiência:</span>
            <span className="font-medium ml-2">
              {formData.meta_motoristas > 0 
                ? `${(formData.meta_corridas / formData.meta_motoristas).toFixed(1)} corridas/motorista`
                : 'N/A'
              }
            </span>
          </div>
          <div>
            <span className="text-gray-600">ROI Estimado:</span>
            <span className="font-medium ml-2">
              {formData.meta_corridas > 0 
                ? `${((formData.meta_receita / (formData.meta_corridas * 10)) * 100).toFixed(0)}%`
                : '0%'
              }
            </span>
          </div>
          <div>
            <span className="text-gray-600">Receita por Corrida:</span>
            <span className="font-medium ml-2">
              {formData.meta_corridas > 0 
                ? `R$ ${(formData.meta_receita / formData.meta_corridas).toFixed(2)}`
                : 'R$ 0,00'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Botões de Ação */}
      <div className="flex gap-3 pt-4 border-t border-gray-200">
        <button 
          type="button"
          onClick={onCancel}
          className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Cancelar
        </button>
        <button 
          type="submit"
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
        >
          <Save className="w-4 h-4" />
          Salvar Alterações
        </button>
      </div>
    </form>
  )
}

export default EditMetaForm
