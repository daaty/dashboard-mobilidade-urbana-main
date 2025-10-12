import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  Target, 
  TrendingUp, 
  MapPin, 
  DollarSign,
  Calendar,
  Filter,
  Search,
  Star,
  XCircle
} from 'lucide-react';

// 🔥 NOVOS IMPORTS - Constantes e Utils centralizados
import { CIDADES_IDS, API_ENDPOINTS } from '../constants/cidadesConstants';
import { processarDadosCidades, ordenarCidades } from '../utils/processCidadesData';

const TabelaMetasCidades = ({ cidadesData, campanhasData }) => {
  const [filtroFase, setFiltroFase] = useState('all');
  const [ordenacao, setOrdenacao] = useState('populacao');
  const [metasReais, setMetasReais] = useState({});
  const [loading, setLoading] = useState(true);

  // Carregar metas reais da API
  useEffect(() => {
    const carregarMetasReais = async () => {
      if (!cidadesData) return;

      setLoading(true);
      const metasMap = {};

      // Buscar metas consolidadas para cada cidade
      for (const cidade of cidadesData) {
        const cidadeId = CIDADES_IDS[cidade.cidade]; // 🔥 USANDO CONSTANTE IMPORTADA
        if (!cidadeId) continue;

        try {
          const url = API_ENDPOINTS.METAS_CONSOLIDADO(cidadeId); // 🔥 USANDO ENDPOINT CONSTANTE
          const response = await fetch(url);
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              metasMap[cidade.cidade] = data.metas;
            }
          }
        } catch (error) {
          console.error(`Erro ao carregar metas de ${cidade.cidade}:`, error);
        }
      }

      setMetasReais(metasMap);
      setLoading(false);
    };

    carregarMetasReais();
  }, [cidadesData]);

  // 🔥 PROCESSAR DADOS USANDO FUNÇÃO CENTRALIZADA
  const dados = processarDadosCidades(cidadesData, campanhasData, metasReais);

  // Filtrar por fase
  const dadosFiltrados = filtroFase === 'all' ? dados : 
                        dados.filter(d => d.fase_atual === filtroFase);

  // 🔥 ORDENAR USANDO FUNÇÃO CENTRALIZADA
  const dadosOrdenados = ordenarCidades(dadosFiltrados, ordenacao);

  const getStatusBadge = (status) => {
    const variants = {
      'acima': 'bg-green-100 text-green-800',
      'meta': 'bg-blue-100 text-blue-800',
      'atencao': 'bg-yellow-100 text-yellow-800',
      'abaixo': 'bg-red-100 text-red-800'
    };
    const labels = {
      'acima': 'Acima da Meta',
      'meta': 'Na Meta',
      'atencao': 'Atenção',
      'abaixo': 'Abaixo da Meta'
    };
    
    return (
      <Badge className={variants[status]}>
        {labels[status]}
      </Badge>
    );
  };

  const getFaseBadge = (fase) => {
    const colors = {
      'Fase 1': 'bg-blue-100 text-blue-800',
      'Fase 2': 'bg-purple-100 text-purple-800',
      'Fase 3': 'bg-green-100 text-green-800',
      'Planejamento': 'bg-gray-100 text-gray-800'
    };
    
    return (
      <Badge className={colors[fase] || colors['Planejamento']}>
        {fase}
      </Badge>
    );
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <CardTitle className="text-xl font-bold flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Metas por Cidade - Visão Estratégica</span>
          </CardTitle>
          
          <div className="flex flex-wrap gap-2">
            {/* Filtro por Fase */}
            <select 
              value={filtroFase}
              onChange={(e) => setFiltroFase(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
            >
              <option value="all">Todas as Fases</option>
              <option value="Fase 1">Fase 1</option>
              <option value="Fase 2">Fase 2</option>
              <option value="Fase 3">Fase 3</option>
            </select>

            {/* Ordenação */}
            <select 
              value={ordenacao}
              onChange={(e) => setOrdenacao(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
            >
              <option value="populacao">Por População</option>
              <option value="performance">Por Performance</option>
              <option value="receita">Por Receita</option>
            </select>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-500">Carregando dados reais...</p>
          </div>
        )}

        {!loading && (
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Cidade</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">População</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Público-Alvo</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Fase</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Progresso</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Meta Mensal</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Realizado</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Performance</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Satisfação</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Cancelamento</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Receita Real</th>
                </tr>
              </thead>
              <tbody>
                {dadosOrdenados.map((cidade, index) => (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-4 w-4 text-gray-400" />
                        <span className="font-medium text-gray-900">{cidade.cidade}</span>
                        {cidade.tem_dados_reais && (
                          <Badge className="bg-blue-100 text-blue-800 text-xs">REAL</Badge>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-1">
                        <Users className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-700">{cidade.populacao}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-gray-700">{cidade.publico_alvo}</td>
                    <td className="py-4 px-4">
                      {getFaseBadge(cidade.fase_atual)}
                    </td>
                    <td className="py-4 px-4">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900">{cidade.mes_campanha}</div>
                        <div className="text-gray-500">{cidade.usuarios_ativos} usuários ativos</div>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-gray-700">{cidade.meta_mes}</td>
                    <td className="py-4 px-4 text-gray-700">{cidade.realizado}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-gray-900">{cidade.percentual}</span>
                        {getStatusBadge(cidade.status_performance)}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      {cidade.satisfacao > 0 ? (
                        <div className="flex items-center space-x-1">
                          <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          <span className="font-medium text-gray-900">{cidade.satisfacao.toFixed(2)}</span>
                          <span className="text-gray-500 text-sm">/5.00</span>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-4 px-4">
                      {cidade.taxa_cancelamento > 0 ? (
                        <div className="flex items-center space-x-1">
                          <XCircle className="h-4 w-4 text-red-500" />
                          <span className={`font-medium ${cidade.taxa_cancelamento < 5 ? 'text-green-600' : 'text-red-600'}`}>
                            {cidade.taxa_cancelamento.toFixed(2)}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-1">
                        <DollarSign className="h-4 w-4 text-green-600" />
                        <span className="font-medium text-green-700">{cidade.receita_estimada}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && dadosOrdenados.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Target className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>Nenhuma cidade encontrada para os filtros selecionados.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TabelaMetasCidades;
