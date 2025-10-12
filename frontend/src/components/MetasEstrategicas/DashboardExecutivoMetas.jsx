import React, { useState } from 'react';
import { FileDown, FileSpreadsheet, FileText } from 'lucide-react';
import CardsKPIs from './CardsKPIs';
import GraficoMetasVsRealizado from './GraficoMetasVsRealizado';
import GraficoEvolucaoTemporal from './GraficoEvolucaoTemporal';
import FiltrosAvancados from './FiltrosAvancados';
import { exportarParaCSV, exportarParaExcel, exportarParaJSON } from '../../utils/exportUtils';
import { exportarRelatorioCompleto } from '../../utils/pdfExportUtils';

const DashboardExecutivoMetas = () => {
  const [periodoSelecionado, setPeriodoSelecionado] = useState(3);
  const [cidadeSelecionada, setCidadeSelecionada] = useState(3); // Matupá por padrão
  const [filtrosAtivos, setFiltrosAtivos] = useState({
    cidades: [],
    periodos: [],
    dataInicio: '',
    dataFim: '',
    metricas: ['corridas', 'receita', 'motoristas'],
    atingimentoMin: 0,
  });
  const [exportando, setExportando] = useState(false);

  const cidades = [
    { id: 1, nome: 'Peixoto de Azevedo' },
    { id: 2, nome: 'Nova Monte Verde' },
    { id: 3, nome: 'Matupá' },
    { id: 4, nome: 'Guarantã do Norte' },
    { id: 5, nome: 'Nova Bandeirantes' }
  ];

  const periodos = [
    { valor: 2, label: '2 meses' },
    { valor: 3, label: '3 meses' },
    { valor: 6, label: '6 meses' },
    { valor: 12, label: '12 meses' }
  ];

  // Handler para mudanças nos filtros
  const handleFilterChange = (novosFiltros) => {
    setFiltrosAtivos(novosFiltros);
    
    // Se filtro de períodos tiver apenas 1 valor, usar como padrão
    if (novosFiltros.periodos.length === 1) {
      setPeriodoSelecionado(novosFiltros.periodos[0]);
    }
    
    // Se filtro de cidades tiver apenas 1 valor, usar como padrão para evolução
    if (novosFiltros.cidades.length === 1) {
      setCidadeSelecionada(novosFiltros.cidades[0]);
    }
  };

  // Handlers de exportação
  const handleExportarCSV = async () => {
    setExportando(true);
    try {
      const resultado = await exportarParaCSV(periodoSelecionado);
      if (resultado.sucesso) {
        alert(`✅ CSV exportado com sucesso! ${resultado.registros} registros.`);
      } else {
        alert(`❌ Erro ao exportar: ${resultado.erro}`);
      }
    } catch (error) {
      alert(`❌ Erro inesperado: ${error.message}`);
    } finally {
      setExportando(false);
    }
  };

  const handleExportarExcel = async () => {
    setExportando(true);
    try {
      const resultado = await exportarParaExcel(periodoSelecionado);
      if (resultado.sucesso) {
        alert(`✅ Excel exportado com sucesso! ${resultado.registros} registros.`);
      } else {
        alert(`❌ Erro ao exportar: ${resultado.erro}`);
      }
    } catch (error) {
      alert(`❌ Erro inesperado: ${error.message}`);
    } finally {
      setExportando(false);
    }
  };

  const handleExportarPDF = async () => {
    setExportando(true);
    try {
      const resultado = await exportarRelatorioCompleto(periodoSelecionado);
      if (resultado.sucesso) {
        alert(`✅ PDF aberto para impressão! Use "Salvar como PDF" no diálogo.`);
      } else {
        alert(`❌ Erro ao exportar: ${resultado.erro}`);
      }
    } catch (error) {
      alert(`❌ Erro inesperado: ${error.message}`);
    } finally {
      setExportando(false);
    }
  };

  const handleExportarJSON = async () => {
    setExportando(true);
    try {
      const resultado = await exportarParaJSON(periodoSelecionado);
      if (resultado.sucesso) {
        alert(`✅ JSON exportado com sucesso! ${resultado.cidades} cidades.`);
      } else {
        alert(`❌ Erro ao exportar: ${resultado.erro}`);
      }
    } catch (error) {
      alert(`❌ Erro inesperado: ${error.message}`);
    } finally {
      setExportando(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          📊 Dashboard Executivo - Metas Estratégicas
        </h1>
        <p className="text-gray-600">
          Acompanhamento em tempo real do atingimento de metas por cidade
        </p>
      </div>

      {/* Filtros */}
      <FiltrosAvancados 
        onFilterChange={handleFilterChange}
        initialFilters={filtrosAtivos}
      />

      {/* Barra de Ferramentas - Exportação */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <FileDown className="w-5 h-5 text-gray-600" />
            <span className="font-medium text-gray-700">Exportar Dados:</span>
          </div>
          
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={handleExportarExcel}
              disabled={exportando}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-md"
            >
              <FileSpreadsheet className="w-4 h-4" />
              Excel (.xls)
            </button>
            
            <button
              onClick={handleExportarCSV}
              disabled={exportando}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-md"
            >
              <FileText className="w-4 h-4" />
              CSV
            </button>
            
            <button
              onClick={handleExportarPDF}
              disabled={exportando}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-md"
            >
              <FileText className="w-4 h-4" />
              PDF (Imprimir)
            </button>
            
            <button
              onClick={handleExportarJSON}
              disabled={exportando}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-md"
            >
              <FileDown className="w-4 h-4" />
              JSON
            </button>
          </div>
        </div>
        
        {exportando && (
          <div className="mt-3 flex items-center gap-2 text-sm text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
            <span>Exportando dados...</span>
          </div>
        )}
      </div>

      {/* Seletores Rápidos (mantidos para compatibilidade) */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Seletor de Período */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📅 Período
            </label>
            <select
              value={periodoSelecionado}
              onChange={(e) => setPeriodoSelecionado(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {periodos.map(periodo => (
                <option key={periodo.valor} value={periodo.valor}>
                  {periodo.label}
                </option>
              ))}
            </select>
          </div>

          {/* Seletor de Cidade (para gráfico de evolução) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🏙️ Cidade (Evolução Temporal)
            </label>
            <select
              value={cidadeSelecionada}
              onChange={(e) => setCidadeSelecionada(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {cidades.map(cidade => (
                <option key={cidade.id} value={cidade.id}>
                  {cidade.nome}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Seção 1: KPIs Principais */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          🎯 Indicadores Principais
        </h2>
        <CardsKPIs periodoMeses={periodoSelecionado} />
      </div>

      {/* Seção 2: Gráfico de Barras (Todas as Cidades) */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          📊 Comparativo por Cidade - Metas vs Realizado
        </h2>
        <GraficoMetasVsRealizado 
          cidadeId={null} 
          periodoMeses={periodoSelecionado} 
        />
      </div>

      {/* Seção 3: Gráfico de Evolução Temporal */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          📈 Evolução Temporal
        </h2>
        <GraficoEvolucaoTemporal 
          cidadeId={cidadeSelecionada} 
        />
      </div>

      {/* Footer com informações */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800 mb-2">
              ℹ️ Sobre os Dados
            </h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• <strong>Dados em Tempo Real:</strong> Informações extraídas diretamente das tabelas operacionais (rides_data, driver_personal_details, drivers_data)</p>
              <p>• <strong>Atualização:</strong> Os dados são atualizados a cada carregamento da página</p>
              <p>• <strong>Cidades:</strong> Peixoto de Azevedo, Nova Monte Verde, Matupá, Guarantã do Norte, Nova Bandeirantes</p>
              <p>• <strong>Métricas:</strong> Corridas realizadas, Receita gerada, Motoristas ativos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Links rápidos */}
      <div className="mt-6 flex gap-4 justify-center flex-wrap">
        <a
          href="#/metas/cidades"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-md"
        >
          📋 Ver Tabela Detalhada
        </a>
        <a
          href="#/metas/planejamento"
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition shadow-md"
        >
          📅 Fases de Planejamento
        </a>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition shadow-md"
        >
          🔄 Atualizar Dados
        </button>
      </div>
    </div>
  );
};

export default DashboardExecutivoMetas;
