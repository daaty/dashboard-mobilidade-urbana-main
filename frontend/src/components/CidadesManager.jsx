
import React, { useState } from 'react'
import CampanhasFormList from './CampanhasFormList';
// --- CriarMetaForm: Formulário para criar metas progressivas ---
const CriarMetaForm = ({ cidade, onClose }) => {
  const [form, setForm] = useState({
    mes: '',
    percentual_penetracao: '',
    meta_corridas: '',
    meta_motoristas: '',
    meta_receita: '',
    tipo_meta: 'media',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_URL}/api/dashboard-executivo/metas-progressivas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          cidade_id: cidade.id || cidade.cidade_id,
          cidade_nome: cidade.cidade || cidade.nome,
        }),
      });
      if (!res.ok) throw new Error('Erro ao criar meta');
      setSuccess(true);
      setTimeout(() => onClose(), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Mês</label>
          <input name="mes" type="number" min="1" max="12" value={form.mes} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">% Penetração</label>
          <input name="percentual_penetracao" type="number" step="0.01" value={form.percentual_penetracao} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Meta Corridas</label>
          <input name="meta_corridas" type="number" value={form.meta_corridas} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Meta Motoristas</label>
          <input name="meta_motoristas" type="number" value={form.meta_motoristas} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium mb-1">Meta Receita (R$)</label>
          <input name="meta_receita" type="number" step="0.01" value={form.meta_receita} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium mb-1">Tipo de Meta</label>
          <select name="tipo_meta" value={form.tipo_meta} onChange={handleChange} className="w-full border rounded p-2">
            <option value="muito_baixa">Muito Baixa</option>
            <option value="baixa">Baixa</option>
            <option value="media">Média</option>
            <option value="alta">Alta</option>
            <option value="agressiva">Agressiva</option>
          </select>
        </div>
      </div>
      {error && <div className="text-red-600 text-sm">{error}</div>}
      {success && <div className="text-green-600 text-sm">Meta criada com sucesso!</div>}
      <div className="flex gap-2 justify-end mt-4">
        <button type="button" onClick={onClose} className="px-4 py-2 rounded bg-gray-200">Cancelar</button>
        <button type="submit" disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition-all">
          {loading ? 'Salvando...' : 'Salvar Meta'}
        </button>
      </div>
    </form>
  );
};
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MapPin, Users, Car, DollarSign, Calendar, TrendingUp, 
  X, Eye, Filter, Search, ArrowRight, Target, Building
} from 'lucide-react'


const CidadeDetailModal = ({ cidade, isOpen, onClose, corridasReais, motoristasReais }) => {
  const [showCriarMeta, setShowCriarMeta] = React.useState(false)
  const [showRelatorio, setShowRelatorio] = React.useState(false)
  const [showCampanhas, setShowCampanhas] = React.useState(false)

  if (!isOpen || !cidade) return null

  // Verificar se cidade é string ou objeto
  const cidadeNome = typeof cidade === 'string' ? cidade : cidade.cidade
  if (!cidadeNome) return null

  const cidadeNormalizada = cidadeNome.toLowerCase().trim()
  const dadosCoridas = corridasReais[cidadeNormalizada] || { concluidas: 0, canceladas: 0, perdidas: 0 }
  const dadosMotoristas = motoristasReais[cidadeNormalizada] || { total: 0, ativos: 0, inativos: 0 }
  
  // Dados da cidade (usar os dados do objeto cidade quando disponível)
  const corridasTotal = cidade.realizado_corridas || dadosCoridas.concluidas || 0
  const motoristasTotal = cidade.realizado_motoristas || dadosMotoristas.ativos || 0
  const populacao = cidade.populacao || 0

  // Handlers para os botões de ação
  const handleCriarMeta = () => setShowCriarMeta(true)
  const handleVerRelatorio = () => setShowRelatorio(true)
  const handleCampanhas = () => setShowCampanhas(true)
  const handleCloseModal = () => {
    setShowCriarMeta(false)
    setShowRelatorio(false)
    setShowCampanhas(false)
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <MapPin className="w-8 h-8" />
                <div>
                  <h2 className="text-2xl font-bold">{cidadeNome}</h2>
                  <p className="text-blue-100">Detalhes completos da cidade</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-all"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Conteúdo */}
          <div className="p-6 space-y-6">
            {/* Métricas Principais */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200">
                <div className="flex items-center gap-3 mb-2">
                  <Car className="w-6 h-6 text-green-600" />
                  <h3 className="font-semibold text-green-800">Corridas</h3>
                </div>
                <div className="text-2xl font-bold text-green-600">{dadosCoridas.concluidas}</div>
                <div className="text-sm text-green-600">
                  {dadosCoridas.canceladas} canceladas • {dadosCoridas.perdidas} perdidas
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4 border border-blue-200">
                <div className="flex items-center gap-3 mb-2">
                  <Users className="w-6 h-6 text-blue-600" />
                  <h3 className="font-semibold text-blue-800">Motoristas</h3>
                </div>
                <div className="text-2xl font-bold text-blue-600">{dadosMotoristas.ativos}</div>
                <div className="text-sm text-blue-600">
                  {dadosMotoristas.total} cadastrados • {dadosMotoristas.inativos} inativos
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-200">
                <div className="flex items-center gap-3 mb-2">
                  <DollarSign className="w-6 h-6 text-purple-600" />
                  <h3 className="font-semibold text-purple-800">Receita</h3>
                </div>
                <div className="text-2xl font-bold text-purple-600">
                  R$ {Math.round((dadosCoridas.concluidas / 1.5) * 2.5)}
                </div>
                <div className="text-sm text-purple-600">Últimos 45 dias</div>
              </div>
            </div>

            {/* Timeline da Cidade */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Roadmap & Evolução da Cidade
              </h3>
              <div className="space-y-3">
                <div className="flex items-center gap-4 p-3 bg-white rounded-lg border border-gray-200">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-800">Fase Atual</div>
                    <div className="text-sm text-gray-600">
                      {corridasTotal > 0 ? 'Em operação • Coletando dados reais' : 'Preparação • Aguardando início'}
                    </div>
                  </div>
                  <div className="text-sm text-green-600 font-medium">
                    {corridasTotal > 0 ? 'ATIVO' : 'PREPARANDO'}
                  </div>
                </div>
                
                <div className="flex items-center gap-4 p-3 bg-white rounded-lg border border-gray-200">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-800">Próximas Campanhas</div>
                    <div className="text-sm text-gray-600">
                      {corridasTotal > 0 ? 'Expansão de motoristas • Set/2025' : 'Lançamento oficial • Set/2025'}
                    </div>
                  </div>
                  <div className="text-sm text-blue-600 font-medium">PLANEJADO</div>
                </div>
                
                {/* Nova seção de metas */}
                <div className="flex items-center gap-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-800">Meta para 30 dias</div>
                    <div className="text-sm text-gray-600">
                      {corridasTotal > 0 ? 
                        `${Math.round(corridasTotal * 1.5)} corridas • ${Math.round(motoristasTotal * 1.2)} motoristas` :
                        '50 corridas • 25 motoristas iniciais'
                      }
                    </div>
                  </div>
                  <div className="text-sm text-yellow-600 font-medium">META</div>
                </div>
              </div>
            </div>

            {/* Seção de análise comparativa */}
            <div className="bg-blue-50 rounded-xl p-4">
              <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Análise Comparativa
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="font-medium text-gray-700 mb-2">Performance vs Meta</div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Corridas/dia:</span>
                      <span className="font-medium">{(corridasTotal / 45).toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Motoristas/1000 hab:</span>
                      <span className="font-medium">{((motoristasTotal / populacao) * 1000).toFixed(1)}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <div className="font-medium text-gray-700 mb-2">Potencial de Crescimento</div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Saturação estimada:</span>
                      <span className="font-medium">{((motoristasTotal / (populacao * 0.001)) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Potencial restante:</span>
                      <span className="font-medium text-green-600">
                        {Math.max(0, Math.round((populacao * 0.001) - motoristasTotal))} motoristas
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Ações Disponíveis - Melhoradas */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Ações Disponíveis
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <button onClick={handleCriarMeta} className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all group">
                  <Target className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  <div className="text-left">
                    <div className="font-medium">Criar Meta</div>
                    <div className="text-xs text-blue-200">Definir objetivos</div>
                  </div>
                </button>
                <button onClick={handleVerRelatorio} className="flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all group">
                  <TrendingUp className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  <div className="text-left">
                    <div className="font-medium">Ver Relatório</div>
                    <div className="text-xs text-green-200">Análise completa</div>
                  </div>
                </button>
                <button onClick={handleCampanhas} className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all group">
                  <Building className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  <div className="text-left">
                    <div className="font-medium">Campanhas</div>
                    <div className="text-xs text-purple-200">Gerenciar ações</div>
                  </div>
                </button>
              </div>
              
              {/* Ações secundárias */}
              <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-200">
                <button className="flex items-center gap-2 px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-sm">
                  <DollarSign className="w-3 h-3" />
                  Exportar dados
                </button>
                <button className="flex items-center gap-2 px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-sm">
                  <Calendar className="w-3 h-3" />
                  Agendar reunião
                </button>
                <button className="flex items-center gap-2 px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-sm">
                  <Users className="w-3 h-3" />
                  Contatar equipe
                </button>
              </div>
            </div>
            {/* Modais das ações */}
            {showCriarMeta && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                <div className="bg-white rounded-xl p-8 max-w-lg w-full shadow-xl">
                  <h2 className="text-lg font-bold mb-4">Criar Meta para {cidadeNome}</h2>
                  <CriarMetaForm cidade={cidade} onClose={handleCloseModal} />
                </div>
              </div>
            )}
            {showRelatorio && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                <div className="bg-white rounded-xl p-8 max-w-lg w-full shadow-xl">
                  <h2 className="text-lg font-bold mb-4">Relatório de {cidadeNome}</h2>
                  <p>Relatório detalhado da cidade (implementar)...</p>
                  <button onClick={handleCloseModal} className="mt-6 px-4 py-2 bg-gray-200 rounded-lg">Fechar</button>
                </div>
              </div>
            )}
            {showCampanhas && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                <div className="bg-white rounded-xl p-8 max-w-4xl w-full shadow-xl max-h-[90vh] overflow-y-auto relative">
                  <button onClick={handleCloseModal} className="absolute top-4 right-4 px-3 py-1 bg-gray-200 rounded-lg z-10">Fechar</button>
                  <h2 className="text-2xl font-bold mb-6">Campanhas de {cidadeNome}</h2>
                  {/* Gestão real de campanhas filtradas por cidade */}
                  <CampanhasFormList cidadeFiltro={cidadeNome} />
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

const GruposCidadesManager = ({ dadosCidades = [], corridasReais, motoristasReais, onVerDetalhes, onEditar }) => {
  const [filtroAtivo, setFiltroAtivo] = useState('todos')
  const [busca, setBusca] = useState('')

  // 🎯 AGRUPAR CIDADES DE FORMA DINÂMICA (SEM HARDCODE)
  // Lógica: Agrupar por FASE PRIORITÁRIA de cada cidade
  const grupos = {
    'operacionais': {
      nome: '🟢 Cidades Operacionais',
      cor: 'from-green-500 to-emerald-600',
      cidades: dadosCidades.filter(cidade => {
        // Cidade tem Fase 1 OU lançamento E está ativa
        const temFase1 = cidade.fase === 'Fase 1' || cidade.fase === 'lançamento';
        const estaAtiva = cidade.status === 'ativa' || cidade.realizado_corridas > 0 || cidade.realizado_motoristas > 0;
        return temFase1 && estaAtiva;
      })
    },
    'expansao_fase2': {
      nome: '🔵 Expansão Fase 2',
      cor: 'from-blue-500 to-cyan-600', 
      cidades: dadosCidades.filter(cidade => cidade.fase === 'Fase 2')
    },
    'expansao_fase3': {
      nome: '🟣 Expansão Fase 3',
      cor: 'from-purple-500 to-pink-600',
      cidades: dadosCidades.filter(cidade => cidade.fase === 'Fase 3')
    },
    'planejamento': {
      nome: '🟡 Em Planejamento',
      cor: 'from-yellow-500 to-orange-600',
      cidades: dadosCidades.filter(cidade => {
        // Cidades planejadas mas sem fase definida ou status planejada
        const semFase = !cidade.fase || cidade.fase === 'A definir';
        const statusPlanejada = cidade.status === 'planejada' || cidade.status === 'pendente';
        return semFase || statusPlanejada;
      })
    }
  }

  const cidadesFiltradas = grupos[filtroAtivo] ? grupos[filtroAtivo].cidades : dadosCidades

  return (
    <div className="space-y-6">
      {/* Controles */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFiltroAtivo('todos')}
            className={`px-4 py-2 rounded-lg transition-all ${
              filtroAtivo === 'todos' 
                ? 'bg-gray-800 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Todas as Cidades
          </button>
          {Object.entries(grupos).map(([key, grupo]) => (
            <button
              key={key}
              onClick={() => setFiltroAtivo(key)}
              className={`px-4 py-2 rounded-lg transition-all ${
                filtroAtivo === key
                  ? 'bg-gray-800 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {grupo.nome.split(' ').slice(1).join(' ')}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {/* Busca melhorada */}
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar cidade..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="pl-10 pr-4 py-2 w-64 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
            {busca && (
              <button
                onClick={() => setBusca('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          
          {/* Contador de resultados */}
          <div className="text-sm text-gray-500 bg-gray-100 px-3 py-2 rounded-lg">
            {busca ? 
              `${cidadesFiltradas.filter(cidade => cidade.cidade.toLowerCase().includes(busca.toLowerCase())).length} resultado(s)` :
              `${cidadesFiltradas.length} cidade(s)`
            }
          </div>
        </div>
      </div>

      {/* Cards de Cidades Agrupados */}
      {filtroAtivo === 'todos' ? (
        // Mostrar todos os grupos
        Object.entries(grupos).map(([key, grupo]) => (
          <div key={key} className="space-y-4">
            <div className={`bg-gradient-to-r ${grupo.cor} rounded-xl p-4 text-white`}>
              <h3 className="text-xl font-bold mb-2">{grupo.nome}</h3>
              <p className="text-white text-opacity-90">
                {grupo.cidades.length} cidade{grupo.cidades.length !== 1 ? 's' : ''}
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {grupo.cidades
                .filter(cidade => cidade.cidade.toLowerCase().includes(busca.toLowerCase()))
                .map((cidade, index) => (
                <CidadeCard 
                  key={`${key}-${index}`}
                  cidade={cidade}
                  onClick={() => onVerDetalhes(cidade)}
                />
              ))}
            </div>
          </div>
        ))
      ) : (
        // Mostrar grupo específico
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cidadesFiltradas
            .filter(cidade => cidade.cidade.toLowerCase().includes(busca.toLowerCase()))
            .map((cidade, index) => (
            <CidadeCard 
              key={index}
              cidade={cidade}
              onClick={() => onVerDetalhes(cidade)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

const CidadeCard = ({ cidade, onClick }) => {
  const corridasTotal = cidade.realizado_corridas || 0
  const motoristasTotal = cidade.realizado_motoristas || 0
  const populacao = cidade.populacao || 0
  const campanhasAtivas = cidade.campanhas_ativas || 0
  
  // Calcular métricas avançadas
  const penetracao = cidade.percentual_motoristas || 0
  const corridasPorMotorista = motoristasTotal > 0 ? (corridasTotal / motoristasTotal).toFixed(1) : '0'
  const receitaEstimada = Math.round(corridasTotal * 12.5) // R$ 12,50 por corrida média
  
  // Determinar status e nível da cidade
  const getStatusInfo = () => {
    if (corridasTotal > 50) return { 
      label: 'Muito Ativa', 
      color: 'from-green-500 to-emerald-600', 
      icon: '🚀',
      textColor: 'text-green-600',
      bgColor: 'bg-green-100'
    }
    if (corridasTotal > 20) return { 
      label: 'Ativa', 
      color: 'from-blue-500 to-cyan-600', 
      icon: '⚡',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-100'
    }
    if (corridasTotal > 0) return { 
      label: 'Iniciando', 
      color: 'from-yellow-500 to-orange-600', 
      icon: '🌱',
      textColor: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    }
    
    // Cidades por fase quando não têm dados
    if (['Colíder', 'Alta Floresta', 'Paranaíta'].includes(cidade.cidade)) {
      return { 
        label: 'Fase 2/3', 
        color: 'from-purple-500 to-pink-600', 
        icon: '🔮',
        textColor: 'text-purple-600',
        bgColor: 'bg-purple-100'
      }
    }
    
    return { 
      label: 'Aguardando', 
      color: 'from-gray-500 to-slate-600', 
      icon: '⏳',
      textColor: 'text-gray-600',
      bgColor: 'bg-gray-100'
    }
  }
  
  const status = getStatusInfo()

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-lg hover:shadow-xl transition-all cursor-pointer"
      onClick={onClick}
    >
      {/* Header melhorado */}
      <div className={`bg-gradient-to-r ${status.color} p-4 text-white relative`}>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="font-bold text-lg truncate">{cidade.cidade}</h3>
            <p className="text-white text-opacity-90 text-sm">{cidade.fase} • {cidade.periodo}</p>
          </div>
          <div className="flex flex-col items-end">
            <span className={`text-xs px-2 py-1 rounded-full ${status.bgColor} ${status.textColor} mb-1`}>
              {status.icon} {status.label}
            </span>
            <Eye className="w-5 h-5" />
          </div>
        </div>
        
        {/* Indicador de progresso da meta */}
        {penetracao > 0 && (
          <div className="mt-2">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-white text-opacity-75">Meta de Penetração</span>
              <span className="text-xs font-bold">{penetracao.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-white bg-opacity-20 rounded-full h-1.5">
              <div 
                className="bg-white h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(penetracao, 100)}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Conteúdo melhorado */}
      <div className="p-4 space-y-3">
        {/* Métricas principais com mais detalhes */}
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center bg-blue-50 rounded-lg p-2">
            <div className="text-2xl font-bold text-blue-600">{corridasTotal}</div>
            <div className="text-xs text-gray-600">Corridas</div>
            {corridasPorMotorista !== '0' && corridasTotal > 0 && (
              <div className="text-xs text-blue-500 font-medium">{corridasPorMotorista}/motorista</div>
            )}
          </div>
          <div className="text-center bg-green-50 rounded-lg p-2">
            <div className="text-2xl font-bold text-green-600">{motoristasTotal}</div>
            <div className="text-xs text-gray-600">Motoristas</div>
            {penetracao > 0 && (
              <div className="text-xs text-green-500 font-medium">{penetracao.toFixed(1)}% pop.</div>
            )}
          </div>
        </div>

        {/* Informações da cidade */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-600 flex items-center">
              <Users className="w-3 h-3 mr-1" />
              População:
            </span>
            <span className="font-medium">{populacao.toLocaleString()}</span>
          </div>
          
          {receitaEstimada > 0 && (
            <div className="flex items-center justify-between">
              <span className="text-gray-600 flex items-center">
                <DollarSign className="w-3 h-3 mr-1" />
                Receita Est.:
              </span>
              <span className="font-medium text-green-600">R$ {receitaEstimada.toLocaleString()}</span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <span className="text-gray-600 flex items-center">
              <Target className="w-3 h-3 mr-1" />
              Campanhas:
            </span>
            <span className={`font-medium ${campanhasAtivas > 0 ? 'text-purple-600' : 'text-gray-400'}`}>
              {campanhasAtivas} ativa{campanhasAtivas !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {/* Footer com call-to-action */}
        <div className="pt-2 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">
              {corridasTotal > 0 ? 'Dados atualizados' : 'Aguardando dados'}
            </span>
            <div className="flex items-center text-blue-600 text-xs font-medium">
              <span className="mr-1">Ver detalhes</span>
              <ArrowRight className="w-3 h-3" />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// 🚀 COMPONENTE PRINCIPAL: CidadesManager
const CidadesManager = ({ dadosCruzados = [], onEditar }) => {
  const [cidadeSelecionada, setCidadeSelecionada] = useState(null)
  const [showModal, setShowModal] = useState(false)

  const handleVerDetalhes = (cidade) => {
    setCidadeSelecionada(cidade)
    setShowModal(true)
  }

  const handleFecharModal = () => {
    setShowModal(false)
    setCidadeSelecionada(null)
  }

  // Calcular estatísticas gerais
  const estatisticasGerais = {
    totalCidades: dadosCruzados.length,
    cidadesAtivas: dadosCruzados.filter(c => (c.realizado_corridas || 0) > 0).length,
    totalCorridas: dadosCruzados.reduce((sum, c) => sum + (c.realizado_corridas || 0), 0),
    totalMotoristas: dadosCruzados.reduce((sum, c) => sum + (c.realizado_motoristas || 0), 0),
    receitaTotal: dadosCruzados.reduce((sum, c) => sum + ((c.realizado_corridas || 0) * 12.5), 0),
    populacaoTotal: dadosCruzados.reduce((sum, c) => sum + (c.populacao || 0), 0)
  }

  return (
    <div className="space-y-6">
      {/* Header com estatísticas */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold">🏙️ Gerenciamento de Cidades</h2>
            <p className="text-purple-100">Organize e visualize dados por grupos inteligentes</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-2xl font-bold">{estatisticasGerais.totalCidades}</div>
              <div className="text-purple-100 text-sm">cidades monitoradas</div>
            </div>
            
            {/* Ações rápidas */}
            <div className="flex gap-2">
              <button className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-2 transition-all"
                      title="Exportar dados">
                <DollarSign className="w-5 h-5" />
              </button>
              <button className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-2 transition-all"
                      title="Atualizar dados">
                <TrendingUp className="w-5 h-5" />
              </button>
              <button className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-2 transition-all"
                      title="Configurações">
                <Filter className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Métricas rápidas */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold">{estatisticasGerais.cidadesAtivas}</div>
            <div className="text-purple-100 text-sm">Cidades Ativas</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold">{estatisticasGerais.totalCorridas}</div>
            <div className="text-purple-100 text-sm">Total Corridas</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold">{estatisticasGerais.totalMotoristas}</div>
            <div className="text-purple-100 text-sm">Motoristas</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold">R$ {Math.round(estatisticasGerais.receitaTotal).toLocaleString()}</div>
            <div className="text-purple-100 text-sm">Receita Est.</div>
          </div>
        </div>
      </div>

      {/* Sistema de grupos de cidades */}
      <GruposCidadesManager 
        dadosCidades={dadosCruzados} 
        onVerDetalhes={handleVerDetalhes}
        onEditar={onEditar}
      />

      {/* Modal de detalhes */}
      <CidadeDetailModal
        cidade={cidadeSelecionada}
        isOpen={showModal}
        onClose={handleFecharModal}
        corridasReais={{}}
        motoristasReais={{}}
      />
    </div>
  )
}

export { CidadeDetailModal, GruposCidadesManager }
export default CidadesManager
