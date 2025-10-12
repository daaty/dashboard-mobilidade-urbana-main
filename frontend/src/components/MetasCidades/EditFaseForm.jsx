/**
 * 📝 EDIT FASE FORM - Formulário de Edição de Fase
 * 
 * Componente para editar informações de uma fase estratégica.
 * Permite alterar nome, período, status e orçamento.
 */

import React, { useState } from 'react';
import { Save, DollarSign } from 'lucide-react';

/**
 * Formulário de edição de fase
 * @param {Object} props
 * @param {Object} props.fase - Dados da fase a editar
 * @param {Function} props.onSave - Callback ao salvar (recebe formData)
 * @param {Function} props.onCancel - Callback ao cancelar
 */
const EditFaseForm = ({ fase, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    nome: fase.nome,
    periodo: fase.periodo,
    status: fase.status,
    orcamento: {
      empenhado: fase.orcamento?.empenhado || 0,
      pagamento: fase.orcamento?.pagamento || 0,
      liquidacao: fase.orcamento?.liquidacao || 0,
      previsto: fase.orcamento?.previsto || 0
    }
  });

  const handleInputChange = (section, field, value) => {
    if (section) {
      setFormData(prev => ({
        ...prev,
        [section]: { ...prev[section], [field]: value }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Informações Básicas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nome da Fase
          </label>
          <input
            type="text"
            value={formData.nome}
            onChange={(e) => handleInputChange(null, 'nome', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            value={formData.status}
            onChange={(e) => handleInputChange(null, 'status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="planejada">Planejada</option>
            <option value="em_execucao">Em Execução</option>
            <option value="pausada">Pausada</option>
            <option value="concluida">Concluída</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Período da Fase
        </label>
        <input
          type="text"
          value={formData.periodo}
          onChange={(e) => handleInputChange(null, 'periodo', e.target.value)}
          placeholder="Ex: 01/ago a 14/set"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Orçamento simplificado */}
      <div className="bg-purple-50 rounded-lg p-4">
        <h4 className="font-medium text-purple-800 mb-3 flex items-center gap-2">
          <DollarSign className="w-4 h-4" />
          Orçamento da Fase
        </h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Empenhado (R$)
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.orcamento.empenhado}
              onChange={(e) => handleInputChange('orcamento', 'empenhado', parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pago (R$)
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.orcamento.pagamento}
              onChange={(e) => handleInputChange('orcamento', 'pagamento', parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
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
  );
};

export default EditFaseForm;
