import React, { useState } from 'react';
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
  Search
} from 'lucide-react';

const TabelaMetasCidades = ({ cidadesData, campanhasData }) => {
  const [filtroFase, setFiltroFase] = useState('all');
  const [ordenacao, setOrdenacao] = useState('populacao');

  // Processar dados das cidades com campanhas
  const processarDadosCidades = () => {
    if (!cidadesData || !campanhasData) return [];

    return cidadesData.map(cidade => {
      // Filtrar campanhas desta cidade
      const campanhasCidade = campanhasData.filter(c => c.cidade.id === cidade.id);
      
      // Calcular métricas
      const populacao = cidade.populacao_estimada_2024 || cidade.populacao_censo_2022 || 0;
      const publico_alvo = Math.round(populacao * 0.45); // 45% entre 15-44 anos
      
      // Determinar fase atual baseada nas campanhas
      const fases = campanhasCidade.map(c => c.fase);
      const fase_atual = fases.includes('Fase 3') ? 'Fase 3' : 
                        fases.includes('Fase 2') ? 'Fase 2' : 
                        fases.includes('Fase 1') ? 'Fase 1' : 'Planejamento';

      // Simular progresso baseado na fase (dados reais viriam da API)
      const progressoMes = fase_atual === 'Fase 1' ? 1 : 
                          fase_atual === 'Fase 2' ? 2 : 
                          fase_atual === 'Fase 3' ? 3 : 0;

      const meta_mes = Math.round(publico_alvo * (progressoMes === 1 ? 0.005 : progressoMes === 2 ? 0.01 : 0.02));
      const realizado = Math.round(meta_mes * (1 + (Math.random() * 0.4 - 0.2))); // Simular variação ±20%
      const percentual = Math.round((realizado / meta_mes) * 100);
      
      const projecao_ano = Math.round(publico_alvo * 0.1 * 12); // 10% ao ano
      const receita_estimada = projecao_ano * 2.5; // R$ 2,50 por corrida

      return {
        cidade: cidade.cidade,
        populacao: populacao.toLocaleString(),
        publico_alvo: publico_alvo.toLocaleString(),
        fase_atual,
        mes_campanha: `${progressoMes}º Mês`,
        meta_mes: `${meta_mes.toLocaleString()} corridas`,
        realizado: `${realizado.toLocaleString()} corridas`,
        percentual: `${percentual}%`,
        projecao_ano: `${projecao_ano.toLocaleString()} corridas`,
        receita_estimada: `R$ ${receita_estimada.toLocaleString()}`,
        campanhas_ativas: campanhasCidade.filter(c => c.status === 'ativa').length,
        orcamento_total: campanhasCidade.reduce((sum, c) => sum + c.orcamento_previsto, 0),
        status_performance: percentual >= 100 ? 'acima' : percentual >= 90 ? 'meta' : 'abaixo',
        populacao_num: populacao, // Para ordenação
        percentual_num: percentual
      };
    });
  };

  const dados = processarDadosCidades();

  // Filtrar por fase
  const dadosFiltrados = filtroFase === 'all' ? dados : 
                        dados.filter(d => d.fase_atual === filtroFase);

  // Ordenar dados
  const dadosOrdenados = [...dadosFiltrados].sort((a, b) => {
    if (ordenacao === 'populacao') return b.populacao_num - a.populacao_num;
    if (ordenacao === 'performance') return b.percentual_num - a.percentual_num;
    if (ordenacao === 'receita') return parseFloat(b.receita_estimada.replace(/[R$\s.]/g, '').replace(',', '.')) - 
                                         parseFloat(a.receita_estimada.replace(/[R$\s.]/g, '').replace(',', '.'));
    return 0;
  });

  const getStatusBadge = (status) => {
    const variants = {
      'acima': 'bg-green-100 text-green-800',
      'meta': 'bg-blue-100 text-blue-800', 
      'abaixo': 'bg-red-100 text-red-800'
    };
    const labels = {
      'acima': 'Acima da Meta',
      'meta': 'Na Meta',
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
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Projeção Anual</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Receita Estimada</th>
              </tr>
            </thead>
            <tbody>
              {dadosOrdenados.map((cidade, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-4">
                    <div className="flex items-center space-x-2">
                      <MapPin className="h-4 w-4 text-gray-400" />
                      <span className="font-medium text-gray-900">{cidade.cidade}</span>
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
                      <div className="text-gray-500">{cidade.campanhas_ativas} campanhas ativas</div>
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
                  <td className="py-4 px-4 text-gray-700">{cidade.projecao_ano}</td>
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

        {dadosOrdenados.length === 0 && (
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
