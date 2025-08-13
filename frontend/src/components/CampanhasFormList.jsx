import React, { useEffect, useState } from "react";

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

const fases = ["Fase 1", "Fase 2", "Fase 3"];
const tipos = ["aquisicao_motoristas", "aquisicao_corridas"];
const statusList = ["ativa", "finalizada", "pausada"];

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

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-4 rounded shadow">
        <h2 className="font-bold text-lg mb-2">{editId ? "Editar Campanha" : "Nova Campanha"}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input name="nome" value={form.nome} onChange={handleChange} required placeholder="Nome da campanha" className="border p-2 rounded" />
          <select name="fase" value={form.fase} onChange={handleChange} className="border p-2 rounded">
            {fases.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
          <input name="cidade" value={form.cidade} onChange={handleChange} required placeholder="Cidade" className="border p-2 rounded" />
          <select name="tipo_campanha" value={form.tipo_campanha} onChange={handleChange} className="border p-2 rounded">
            {tipos.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          <input name="data_inicio" type="date" value={form.data_inicio} onChange={handleChange} required className="border p-2 rounded" />
          <input name="data_fim" type="date" value={form.data_fim} onChange={handleChange} required className="border p-2 rounded" />
          <input name="meta_quantidade" type="number" value={form.meta_quantidade} onChange={handleChange} required placeholder="Meta Quantidade" className="border p-2 rounded" />
          <input name="orcamento_previsto" type="number" step="0.01" value={form.orcamento_previsto} onChange={handleChange} required placeholder="Orçamento Previsto" className="border p-2 rounded" />
          <input name="custo_real" type="number" step="0.01" value={form.custo_real} onChange={handleChange} placeholder="Custo Real" className="border p-2 rounded" />
          <select name="status" value={form.status} onChange={handleChange} className="border p-2 rounded">
            {statusList.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="flex gap-2 mt-2">
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">{editId ? "Salvar" : "Cadastrar"}</button>
          {editId && <button type="button" onClick={() => { setForm(initialForm); setEditId(null); }} className="bg-gray-400 text-white px-4 py-2 rounded">Cancelar</button>}
        </div>
      </form>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-bold text-lg mb-2">Campanhas Cadastradas</h2>
        {loading ? <div>Carregando...</div> : (
          <table className="min-w-full text-sm">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Fase</th>
                <th>Cidade</th>
                <th>Tipo</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Meta</th>
                <th>Orçamento</th>
                <th>Custo Real</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {campanhas.map(c => (
                <tr key={c.id} className="border-t">
                  <td>{c.nome}</td>
                  <td>{c.fase}</td>
                  <td>{c.cidade}</td>
                  <td>{c.tipo_campanha}</td>
                  <td>{c.data_inicio?.slice(0,10)}</td>
                  <td>{c.data_fim?.slice(0,10)}</td>
                  <td>{c.meta_quantidade}</td>
                  <td>R$ {Number(c.orcamento_previsto).toLocaleString('pt-BR', {minimumFractionDigits:2})}</td>
                  <td>R$ {Number(c.custo_real).toLocaleString('pt-BR', {minimumFractionDigits:2})}</td>
                  <td>{c.status}</td>
                  <td>
                    <button onClick={() => handleEdit(c)} className="text-blue-600 mr-2">Editar</button>
                    <button onClick={() => handleDelete(c.id)} className="text-red-600">Excluir</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
