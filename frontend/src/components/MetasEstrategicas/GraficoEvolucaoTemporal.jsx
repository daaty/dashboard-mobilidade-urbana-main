import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import axios from 'axios';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const GraficoEvolucaoTemporal = ({ cidadeId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [metricaSelecionada, setMetricaSelecionada] = useState('corridas');
  const [cidadeNome, setCidadeNome] = useState('');

  useEffect(() => {
    fetchDados();
  }, [cidadeId, metricaSelecionada]);

  const fetchDados = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!cidadeId) {
        setError('Selecione uma cidade para visualizar a evolução temporal');
        setLoading(false);
        return;
      }

      const response = await axios.get(`http://localhost:8000/api/metas-estrategicas/consolidado/${cidadeId}`);
      
      if (!response.data.success || !response.data.metas || response.data.metas.length === 0) {
        setError('Nenhum dado disponível para esta cidade');
        setLoading(false);
        return;
      }

      setCidadeNome(response.data.cidade_nome);

      // Ordenar por período (2, 3, 6, 12 meses)
      const metasOrdenadas = response.data.metas
        .sort((a, b) => a.periodo_meses - b.periodo_meses);

      // Remover duplicatas mantendo apenas um registro por período
      const metasUnicas = [];
      const periodosVistos = new Set();
      
      for (const meta of metasOrdenadas) {
        if (!periodosVistos.has(meta.periodo_meses)) {
          metasUnicas.push(meta);
          periodosVistos.add(meta.periodo_meses);
        }
      }

      // Preparar labels (períodos)
      const labels = metasUnicas.map(m => `${m.periodo_meses} ${m.periodo_meses === 1 ? 'mês' : 'meses'}`);

      let metasValues, resultadosValues, titulo, cor;

      switch (metricaSelecionada) {
        case 'corridas':
          metasValues = metasUnicas.map(m => m.metas?.corridas || 0);
          resultadosValues = metasUnicas.map(m => m.resultados?.corridas || 0);
          titulo = `Evolução de Corridas - ${response.data.cidade_nome}`;
          cor = { meta: 'rgba(59, 130, 246, 0.6)', realizado: 'rgba(34, 197, 94, 0.6)' };
          break;
        case 'receita':
          metasValues = metasUnicas.map(m => m.metas?.receita || 0);
          resultadosValues = metasUnicas.map(m => m.resultados?.receita || 0);
          titulo = `Evolução de Receita - ${response.data.cidade_nome}`;
          cor = { meta: 'rgba(251, 191, 36, 0.6)', realizado: 'rgba(34, 197, 94, 0.6)' };
          break;
        case 'motoristas':
          metasValues = metasUnicas.map(m => m.metas?.motoristas || 0);
          resultadosValues = metasUnicas.map(m => m.resultados?.motoristas || 0);
          titulo = `Evolução de Motoristas - ${response.data.cidade_nome}`;
          cor = { meta: 'rgba(168, 85, 247, 0.6)', realizado: 'rgba(34, 197, 94, 0.6)' };
          break;
        default:
          metasValues = metasUnicas.map(m => m.metas?.corridas || 0);
          resultadosValues = metasUnicas.map(m => m.resultados?.corridas || 0);
          titulo = `Evolução de Corridas - ${response.data.cidade_nome}`;
          cor = { meta: 'rgba(59, 130, 246, 0.6)', realizado: 'rgba(34, 197, 94, 0.6)' };
      }

      setChartData({
        labels,
        datasets: [
          {
            label: 'Meta Planejada',
            data: metasValues,
            borderColor: cor.meta.replace('0.6', '1'),
            backgroundColor: cor.meta,
            borderWidth: 3,
            pointRadius: 6,
            pointHoverRadius: 8,
            pointBackgroundColor: cor.meta.replace('0.6', '1'),
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            fill: true,
            tension: 0.4 // Curva suave
          },
          {
            label: 'Realizado',
            data: resultadosValues,
            borderColor: cor.realizado.replace('0.6', '1'),
            backgroundColor: cor.realizado,
            borderWidth: 3,
            pointRadius: 6,
            pointHoverRadius: 8,
            pointBackgroundColor: cor.realizado.replace('0.6', '1'),
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            fill: true,
            tension: 0.4
          }
        ],
        titulo
      });

      setLoading(false);
    } catch (err) {
      console.error('Erro ao buscar dados:', err);
      setError('Erro ao carregar dados. Verifique se o backend está rodando.');
      setLoading(false);
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
            family: "'Inter', 'Segoe UI', sans-serif"
          },
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      title: {
        display: true,
        text: chartData?.titulo || 'Evolução Temporal',
        font: {
          size: 18,
          weight: 'bold',
          family: "'Inter', 'Segoe UI', sans-serif"
        },
        padding: {
          top: 10,
          bottom: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (metricaSelecionada === 'receita') {
              label += 'R$ ' + context.parsed.y.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
            } else {
              label += context.parsed.y.toLocaleString('pt-BR');
            }
            
            // Calcular percentual de atingimento para linha "Realizado"
            if (context.dataset.label === 'Realizado' && context.datasetIndex === 1) {
              const metaValue = context.chart.data.datasets[0].data[context.dataIndex];
              if (metaValue > 0) {
                const percentual = ((context.parsed.y / metaValue) * 100).toFixed(1);
                label += ` (${percentual}% da meta)`;
              }
            }
            
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          font: {
            size: 12
          },
          callback: function(value) {
            if (metricaSelecionada === 'receita') {
              return 'R$ ' + value.toLocaleString('pt-BR');
            }
            return value.toLocaleString('pt-BR');
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        ticks: {
          font: {
            size: 12
          }
        },
        grid: {
          display: false
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Carregando evolução temporal...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600 font-medium">❌ {error}</p>
        <button
          onClick={fetchDados}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Título com nome da cidade */}
      <div className="mb-4 text-center">
        <h3 className="text-xl font-bold text-gray-800">{cidadeNome}</h3>
        <p className="text-sm text-gray-500">Evolução ao longo dos períodos</p>
      </div>

      {/* Seletor de Métrica */}
      <div className="mb-6 flex gap-3 justify-center flex-wrap">
        <button
          onClick={() => setMetricaSelecionada('corridas')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            metricaSelecionada === 'corridas'
              ? 'bg-blue-600 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          🚗 Corridas
        </button>
        <button
          onClick={() => setMetricaSelecionada('receita')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            metricaSelecionada === 'receita'
              ? 'bg-yellow-500 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          💰 Receita
        </button>
        <button
          onClick={() => setMetricaSelecionada('motoristas')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            metricaSelecionada === 'motoristas'
              ? 'bg-purple-600 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          👤 Motoristas
        </button>
      </div>

      {/* Gráfico */}
      <div style={{ height: '400px' }}>
        {chartData && <Line data={chartData} options={options} />}
      </div>

      {/* Indicadores de tendência */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded">
          <span className="font-medium text-blue-700">📈 Tendência:</span>
          <span className="ml-2 text-gray-700">
            {chartData && chartData.datasets[1].data.length > 1 && (
              chartData.datasets[1].data[chartData.datasets[1].data.length - 1] >
              chartData.datasets[1].data[0]
                ? 'Crescimento'
                : 'Declínio'
            )}
          </span>
        </div>
        <div className="bg-green-50 p-3 rounded">
          <span className="font-medium text-green-700">🎯 Atingimento Médio:</span>
          <span className="ml-2 text-gray-700">
            {chartData && (() => {
              const metas = chartData.datasets[0].data;
              const resultados = chartData.datasets[1].data;
              const percentuais = metas.map((meta, i) => 
                meta > 0 ? (resultados[i] / meta) * 100 : 0
              );
              const media = percentuais.reduce((a, b) => a + b, 0) / percentuais.length;
              return `${media.toFixed(1)}%`;
            })()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default GraficoEvolucaoTemporal;
