import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Download, 
  Calendar, 
  Filter,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Car,
  Star,
  MapPin,
  Clock,
  Target,
  BarChart3,
  PieChart,
  Award,
  AlertTriangle
} from 'lucide-react';

const RelatoriosExecutivos = ({ data }) => {
  const [periodoRelatorio, setPeriodoRelatorio] = useState('mensal');
  const [tipoRelatorio, setTipoRelatorio] = useState('executivo');
  const [generatingReport, setGeneratingReport] = useState(false);

  // Dados mockados para o relatório
  const dadosRelatorio = {
    periodo: {
      inicio: '01/01/2024',
      fim: '31/01/2024',
      tipo: 'Janeiro 2024'
    },
    metricas_principais: {
      corridas_totais: 2847,
      receita_total: 45678.90,
      motoristas_ativos: 127,
      avaliacao_media: 4.3,
      taxa_conversao: 87.5,
      tempo_medio_espera: 4.2
    },
    comparacao_anterior: {
      corridas_totais: 12.5,
      receita_total: 8.3,
      motoristas_ativos: -2.1,
      avaliacao_media: 0.2,
      taxa_conversao: 3.2,
      tempo_medio_espera: -8.7
    },
    top_motoristas: [
      { nome: 'João Silva', corridas: 189, receita: 3456.78, avaliacao: 4.9 },
      { nome: 'Maria Santos', corridas: 165, receita: 2987.45, avaliacao: 4.8 },
      { nome: 'Pedro Costa', corridas: 158, receita: 2654.32, avaliacao: 4.7 },
      { nome: 'Ana Oliveira', corridas: 142, receita: 2398.67, avaliacao: 4.6 },
      { nome: 'Carlos Lima', corridas: 138, receita: 2245.89, avaliacao: 4.5 }
    ],
    cidades_performance: [
      { cidade: 'São Paulo', corridas: 1245, receita: 18765.43, crescimento: 15.2 },
      { cidade: 'Rio de Janeiro', corridas: 876, receita: 13456.78, crescimento: 8.7 },
      { cidade: 'Belo Horizonte', corridas: 432, receita: 7654.32, crescimento: -3.4 },
      { cidade: 'Salvador', corridas: 294, receita: 5802.37, crescimento: 22.1 }
    ],
    insights_principais: [
      'Crescimento de 12.5% no número total de corridas',
      'Receita aumentou 8.3% comparado ao mês anterior',
      'Avaliação média dos motoristas melhorou para 4.3',
      'Tempo de espera reduziu em 8.7% (4.2 minutos)',
      'Salvador foi a cidade com maior crescimento (22.1%)'
    ],
    alertas_executivos: [
      { tipo: 'critico', titulo: 'Meta de Belo Horizonte não atingida', impacto: 'Alto' },
      { tipo: 'atencao', titulo: 'Queda no número de motoristas ativos', impacto: 'Médio' },
      { tipo: 'positivo', titulo: 'Superação da meta de satisfação', impacto: 'Positivo' }
    ]
  };

  const gerarRelatorio = async () => {
    setGeneratingReport(true);
    
    // Simular tempo de geração
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Em uma implementação real, aqui seria feita a requisição para o backend
    // para gerar o PDF do relatório
    
    // Simular download
    const blob = new Blob(['Relatório Executivo - Dashboard'], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `relatorio-executivo-${periodoRelatorio}-${Date.now()}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    setGeneratingReport(false);
  };

  const MetricaCard = ({ titulo, valor, variacao, icone: Icon, formato = '' }) => {
    const isPositive = variacao > 0;
    return (
      <div className="bg-white p-4 rounded-lg border shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <Icon className="h-5 w-5 text-gray-600" />
          <span className={`text-xs font-medium ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {isPositive ? '+' : ''}{variacao.toFixed(1)}%
          </span>
        </div>
        <h3 className="text-sm font-medium text-gray-600">{titulo}</h3>
        <p className="text-xl font-bold text-gray-900">
          {formato}{typeof valor === 'number' ? valor.toLocaleString('pt-BR') : valor}
        </p>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="h-6 w-6 text-indigo-600" />
          <h2 className="text-2xl font-bold text-gray-900">Relatórios Executivos</h2>
        </div>
        
        <div className="flex gap-3">
          <select
            value={periodoRelatorio}
            onChange={(e) => setPeriodoRelatorio(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="semanal">Semanal</option>
            <option value="mensal">Mensal</option>
            <option value="trimestral">Trimestral</option>
            <option value="anual">Anual</option>
          </select>
          
          <select
            value={tipoRelatorio}
            onChange={(e) => setTipoRelatorio(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="executivo">Executivo</option>
            <option value="operacional">Operacional</option>
            <option value="financeiro">Financeiro</option>
            <option value="completo">Completo</option>
          </select>
          
          <button
            onClick={gerarRelatorio}
            disabled={generatingReport}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
          >
            {generatingReport ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Gerando...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Baixar PDF
              </>
            )}
          </button>
        </div>
      </div>

      {/* Período do Relatório */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border">
        <div className="flex items-center gap-2 mb-2">
          <Calendar className="h-5 w-5 text-indigo-600" />
          <span className="font-semibold text-gray-900">Período: {dadosRelatorio.periodo.tipo}</span>
        </div>
        <p className="text-sm text-gray-600">
          De {dadosRelatorio.periodo.inicio} até {dadosRelatorio.periodo.fim}
        </p>
      </div>

      {/* Métricas Principais */}
      <div>
        <h3 className="text-lg font-semibold mb-4">📊 Indicadores Principais</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <MetricaCard
            titulo="Corridas Realizadas"
            valor={dadosRelatorio.metricas_principais.corridas_totais}
            variacao={dadosRelatorio.comparacao_anterior.corridas_totais}
            icone={Car}
          />
          <MetricaCard
            titulo="Receita Total"
            valor={dadosRelatorio.metricas_principais.receita_total}
            variacao={dadosRelatorio.comparacao_anterior.receita_total}
            icone={DollarSign}
            formato="R$ "
          />
          <MetricaCard
            titulo="Motoristas Ativos"
            valor={dadosRelatorio.metricas_principais.motoristas_ativos}
            variacao={dadosRelatorio.comparacao_anterior.motoristas_ativos}
            icone={Users}
          />
          <MetricaCard
            titulo="Avaliação Média"
            valor={dadosRelatorio.metricas_principais.avaliacao_media}
            variacao={dadosRelatorio.comparacao_anterior.avaliacao_media}
            icone={Star}
          />
          <MetricaCard
            titulo="Taxa de Conversão"
            valor={dadosRelatorio.metricas_principais.taxa_conversao}
            variacao={dadosRelatorio.comparacao_anterior.taxa_conversao}
            icone={Target}
            formato=""
          />
          <MetricaCard
            titulo="Tempo Médio (min)"
            valor={dadosRelatorio.metricas_principais.tempo_medio_espera}
            variacao={dadosRelatorio.comparacao_anterior.tempo_medio_espera}
            icone={Clock}
          />
        </div>
      </div>

      {/* Top Motoristas */}
      <div className="bg-white rounded-lg p-6 border shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Award className="h-5 w-5 text-yellow-600" />
          Top 5 Motoristas do Período
        </h3>
        
        <div className="space-y-3">
          {dadosRelatorio.top_motoristas.map((motorista, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                  index === 0 ? 'bg-yellow-500' : 
                  index === 1 ? 'bg-gray-400' : 
                  index === 2 ? 'bg-orange-500' : 'bg-blue-500'
                }`}>
                  {index + 1}
                </div>
                <div>
                  <h4 className="font-medium">{motorista.nome}</h4>
                  <p className="text-sm text-gray-600">
                    {motorista.corridas} corridas • ⭐ {motorista.avaliacao}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold">R$ {motorista.receita.toLocaleString('pt-BR')}</p>
                <p className="text-sm text-gray-600">receita</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance por Cidade */}
      <div className="bg-white rounded-lg p-6 border shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MapPin className="h-5 w-5 text-green-600" />
          Performance por Cidade
        </h3>
        
        <div className="space-y-3">
          {dadosRelatorio.cidades_performance.map((cidade, index) => (
            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center gap-3">
                <MapPin className="h-4 w-4 text-gray-400" />
                <div>
                  <h4 className="font-medium">{cidade.cidade}</h4>
                  <p className="text-sm text-gray-600">
                    {cidade.corridas} corridas
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="font-semibold">R$ {cidade.receita.toLocaleString('pt-BR')}</p>
                  <p className="text-sm text-gray-600">receita</p>
                </div>
                
                <div className="flex items-center gap-1">
                  {cidade.crescimento > 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className={`text-sm font-medium ${
                    cidade.crescimento > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {cidade.crescimento > 0 ? '+' : ''}{cidade.crescimento}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Insights Principais */}
        <div className="bg-white rounded-lg p-6 border shadow-sm">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            Principais Insights
          </h3>
          
          <div className="space-y-3">
            {dadosRelatorio.insights_principais.map((insight, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-gray-700">{insight}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Alertas Executivos */}
        <div className="bg-white rounded-lg p-6 border shadow-sm">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
            Alertas Executivos
          </h3>
          
          <div className="space-y-3">
            {dadosRelatorio.alertas_executivos.map((alerta, index) => (
              <div key={index} className={`flex items-center justify-between p-3 rounded-lg border-l-4 ${
                alerta.tipo === 'critico' ? 'bg-red-50 border-red-500' :
                alerta.tipo === 'atencao' ? 'bg-yellow-50 border-yellow-500' :
                'bg-green-50 border-green-500'
              }`}>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{alerta.titulo}</h4>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                    alerta.tipo === 'critico' ? 'bg-red-100 text-red-700' :
                    alerta.tipo === 'atencao' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {alerta.impacto}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Resumo Executivo */}
      <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">📋 Resumo Executivo</h3>
        
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-700 mb-3">
            <strong>Desempenho Geral:</strong> O período analisado ({dadosRelatorio.periodo.tipo}) apresentou 
            resultados positivos com crescimento de 12.5% no número de corridas e aumento de 8.3% na receita total.
          </p>
          
          <p className="text-gray-700 mb-3">
            <strong>Destaques Positivos:</strong> A avaliação média dos motoristas melhorou para 4.3 estrelas, 
            indicando alta satisfação dos clientes. O tempo médio de espera foi reduzido em 8.7%, 
            demonstrando maior eficiência operacional.
          </p>
          
          <p className="text-gray-700 mb-3">
            <strong>Pontos de Atenção:</strong> Observou-se uma ligeira queda de 2.1% no número de motoristas ativos. 
            A cidade de Belo Horizonte apresentou decréscimo de 3.4% nas corridas, requerendo atenção especial.
          </p>
          
          <p className="text-gray-700">
            <strong>Recomendações:</strong> Investir em recrutamento de novos motoristas, implementar estratégias 
            específicas para Belo Horizonte, e manter o foco na qualidade do serviço que tem gerado 
            excelentes avaliações.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RelatoriosExecutivos;
