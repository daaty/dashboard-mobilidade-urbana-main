import React, { useEffect, useState } from "react";
import { motion } from 'framer-motion';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Calendar, 
  MapPin, 
  Target, 
  DollarSign,
  Users,
  Activity
} from 'lucide-react';

const initialForm = {
  nome: "",
  fase: "Fase 1",
  cidade: "",
  data_inicio: "",
  data_fim: "",
  tipo_campanha: "aquisicao_motoristas",
  meta_quantidade: 0,
  orcamento_previsto: 0,
  custo_real: 0,
  status: "ativa"
};

const fases = [
  { value: "Fase 1", label: "Fase 1 - Lançamento" },
  { value: "Fase 2", label: "Fase 2 - Crescimento" },
  { value: "Fase 3", label: "Fase 3 - Expansão" }
];

const tipos = [
  { value: "aquisicao_motoristas", label: "Aquisição de Motoristas" },
  { value: "aquisicao_corridas", label: "Aquisição de Corridas" }
];

const statusList = [
  { value: "ativa", label: "Ativa", color: "bg-green-100 text-green-800" },
  { value: "finalizada", label: "Finalizada", color: "bg-gray-100 text-gray-800" },
  { value: "pausada", label: "Pausada", color: "bg-yellow-100 text-yellow-800" }
];

export default function CampanhasFormList() {
  const [form, setForm] = useState(initialForm);
  const [campanhas, setCampanhas] = useState([]);
  const [editId, setEditId] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchCampanhas = async () => {
    setLoading(true);
    const resp = await fetch("/api/campanhas");
    const data = await resp.json();
    setCampanhas(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchCampanhas();
  }, []);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    const method = editId ? "PUT" : "POST";
    const url = editId ? `/api/campanhas/${editId}` : "/api/campanhas";
    const body = { ...form };
    if (body.meta_quantidade) body.meta_quantidade = parseInt(body.meta_quantidade);
    if (body.orcamento_previsto) body.orcamento_previsto = parseFloat(body.orcamento_previsto);
    if (body.custo_real) body.custo_real = parseFloat(body.custo_real);
    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    setForm(initialForm);
    setEditId(null);
    fetchCampanhas();
  };

  const handleEdit = campanha => {
    setForm({ ...campanha, data_inicio: campanha.data_inicio?.slice(0,10), data_fim: campanha.data_fim?.slice(0,10) });
    setEditId(campanha.id);
  };

  const handleDelete = async id => {
    if (!window.confirm("Confirma remover esta campanha?")) return;
    await fetch(`/api/campanhas/${id}`, { method: "DELETE" });
    fetchCampanhas();
  };

  const handleCancel = () => {
    setForm(initialForm);
    setEditId(null);
  };

  return (
    <div className="space-y-8">
      {/* Formulário de Campanha - Estilo Executivo */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200 rounded-2xl shadow-xl overflow-hidden"
      >
        {/* Header do Formulário */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-xl">
              {editId ? <Edit className="w-6 h-6 text-white" /> : <Plus className="w-6 h-6 text-white" />}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">
                {editId ? "Editar Campanha" : "Nova Campanha"}
              </h2>
              <p className="text-blue-100">
                {editId ? "Atualize os dados da campanha existente" : "Cadastre uma nova campanha de marketing"}
              </p>
            </div>
          </div>
        </div>

        {/* Formulário */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Nome da Campanha */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <Target className="w-4 h-4 inline mr-2" />
                Nome da Campanha *
              </label>
              <input 
                name="nome" 
                value={form.nome} 
                onChange={handleChange} 
                required 
                placeholder="Ex: Lançamento Motoristas - Guaranta do Norte"
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200" 
              />
            </div>

            {/* Fase */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Fase da Campanha *
              </label>
              <select 
                name="fase" 
                value={form.fase} 
                onChange={handleChange} 
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
              >
                {fases.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
              </select>
            </div>

            {/* Cidade */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <MapPin className="w-4 h-4 inline mr-2" />
                Cidade de Atuação *
              </label>
              <input 
                name="cidade" 
                value={form.cidade} 
                onChange={handleChange} 
                required 
                placeholder="Ex: Guaranta do Norte"
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200" 
              />
            </div>

            {/* Tipo de Campanha */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <Activity className="w-4 h-4 inline mr-2" />
                Tipo de Campanha *
              </label>
              <select 
                name="tipo_campanha" 
                value={form.tipo_campanha} 
                onChange={handleChange} 
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
              >
                {tipos.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>

            {/* Data de Início */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Data de Início *
              </label>
              <input 
                name="data_inicio" 
                type="date" 
                value={form.data_inicio} 
                onChange={handleChange} 
                required 
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200" 
              />
            </div>

            {/* Data de Fim */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Data de Encerramento *
              </label>
              <input 
                name="data_fim" 
                type="date" 
                value={form.data_fim} 
                onChange={handleChange} 
                required 
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200" 
              />
            </div>

            {/* Meta Quantidade */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <Users className="w-4 h-4 inline mr-2" />
                Meta de Quantidade *
              </label>
              <input 
                name="meta_quantidade" 
                type="number" 
                value={form.meta_quantidade} 
                onChange={handleChange} 
                required 
                placeholder="Ex: 50 motoristas"
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200" 
              />
            </div>

            {/* Orçamento Previsto */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <DollarSign className="w-4 h-4 inline mr-2" />
                Orçamento Previsto (R$) *
              </label>
              <input 
                name="orcamento_previsto" 
                type="number" 
                step="0.01" 
                value={form.orcamento_previsto} 
                onChange={handleChange} 
                required 
                placeholder="Ex: 15000.00"
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200" 
              />
            </div>

            {/* Custo Real */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                <DollarSign className="w-4 h-4 inline mr-2" />
                Custo Realizado (R$)
              </label>
              <input 
                name="custo_real" 
                type="number" 
                step="0.01" 
                value={form.custo_real} 
                onChange={handleChange} 
                placeholder="Ex: 12500.00"
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200" 
              />
              <p className="text-xs text-slate-500 mt-1">Deixe em branco se ainda não houver gastos</p>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Status da Campanha *
              </label>
              <select 
                name="status" 
                value={form.status} 
                onChange={handleChange} 
                className="w-full border border-slate-300 p-3 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
              >
                {statusList.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
          </div>

          {/* Botões de Ação */}
          <div className="flex gap-4 mt-8 pt-6 border-t border-slate-200">
            <button 
              type="submit" 
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Save className="w-4 h-4" />
              {editId ? "Salvar Alterações" : "Cadastrar Campanha"}
            </button>
            
            {editId && (
              <button 
                type="button" 
                onClick={handleCancel}
                className="flex items-center gap-2 bg-gradient-to-r from-gray-400 to-gray-500 text-white px-6 py-3 rounded-xl font-semibold hover:from-gray-500 hover:to-gray-600 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <X className="w-4 h-4" />
                Cancelar Edição
              </button>
            )}
          </div>
        </form>
      </motion.div>
      {/* Tabela de Campanhas - Estilo Executivo */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-br from-slate-50 to-gray-100 border border-slate-200 rounded-2xl shadow-xl overflow-hidden"
      >
        {/* Header da Tabela */}
        <div className="bg-gradient-to-r from-slate-600 to-gray-600 p-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-xl">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Campanhas Cadastradas</h2>
              <p className="text-slate-100">Gerencie e acompanhe todas as campanhas ativas</p>
            </div>
          </div>
        </div>

        {/* Conteúdo da Tabela */}
        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-flex items-center gap-2 text-slate-600">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-slate-600"></div>
                Carregando campanhas...
              </div>
            </div>
          ) : campanhas.length === 0 ? (
            <div className="text-center py-12">
              <div className="p-4 bg-slate-100 rounded-xl inline-block mb-4">
                <Activity className="w-8 h-8 text-slate-400" />
              </div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">Nenhuma campanha cadastrada</h3>
              <p className="text-slate-500">Cadastre sua primeira campanha usando o formulário acima.</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Campanha
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Fase / Cidade
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Período
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Meta
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Orçamento
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {campanhas.map((c, index) => (
                      <motion.tr
                        key={c.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="hover:bg-slate-50 transition-colors duration-200"
                      >
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-semibold text-slate-900">{c.nome}</div>
                            <div className="text-xs text-slate-500 capitalize">
                              {tipos.find(t => t.value === c.tipo_campanha)?.label || c.tipo_campanha}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-medium text-slate-900">{c.fase}</div>
                            <div className="text-xs text-slate-500 flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              {c.cidade}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-xs text-slate-600">
                            <div className="flex items-center gap-1 mb-1">
                              <Calendar className="w-3 h-3" />
                              {c.data_inicio?.slice(0,10).split('-').reverse().join('/')}
                            </div>
                            <div className="text-slate-400">
                              até {c.data_fim?.slice(0,10).split('-').reverse().join('/')}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-semibold text-slate-900">
                            {c.meta_quantidade.toLocaleString('pt-BR')}
                          </div>
                          <div className="text-xs text-slate-500">
                            {c.tipo_campanha === 'aquisicao_motoristas' ? 'motoristas' : 'corridas'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-semibold text-green-600">
                              R$ {Number(c.orcamento_previsto).toLocaleString('pt-BR', {minimumFractionDigits:2})}
                            </div>
                            <div className="text-xs text-slate-500">
                              Gasto: R$ {Number(c.custo_real).toLocaleString('pt-BR', {minimumFractionDigits:2})}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
                            statusList.find(s => s.value === c.status)?.color || 'bg-gray-100 text-gray-800'
                          }`}>
                            {statusList.find(s => s.value === c.status)?.label || c.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center justify-center gap-2">
                            <button 
                              onClick={() => handleEdit(c)} 
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                              title="Editar campanha"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => handleDelete(c.id)} 
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
                              title="Excluir campanha"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
