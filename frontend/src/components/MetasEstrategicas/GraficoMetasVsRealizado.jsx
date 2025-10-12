import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import axios from 'axios';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const GraficoMetasVsRealizado = ({ cidadeId = null, periodoMeses = 3 }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [metricaSelecionada, setMetricaSelecionada] = useState('corridas'); // 'corridas', 'receita', 'motoristas'

  useEffect(() => {
    fetchDados();
  }, [cidadeId, periodoMeses, metricaSelecionada]);

  const fetchDados = async () => {
    try {
      setLoading(true);
      setError(null);

      let dados = [];

      if (cidadeId) {
        // Buscar dados de uma cidade específica
        const response = await axios.get(`http://localhost:8000/api/metas-estrategicas/consolidado/${cidadeId}`);
        if (response.data.success) {
          const metasPorPeriodo = response.data.metas.filter(m => m.periodo_meses === periodoMeses);
          dados = [{
            cidade: response.data.cidade_nome,
            cidade_id: response.data.cidade_id,
            metas: metasPorPeriodo[0] || {}
          }];
        }
      } else {
        // Buscar dados de todas as cidades
        const cidades = [1, 2, 3, 4, 5]; // Peixoto, Nova Monte Verde, Matupá, Guarantã, Nova Bandeirantes
        
        for (const id of cidades) {
          try {
            const response = await axios.get(`http://localhost:8000/api/metas-estrategicas/consolidado/${id}`);
            if (response.data.success && response.data.metas.length > 0) {
              const metasPorPeriodo = response.data.metas.find(m => m.periodo_meses === periodoMeses);
              if (metasPorPeriodo) {
                dados.push({
                  cidade: response.data.cidade_nome,
                  cidade_id: response.data.cidade_id,
                  metas: metasPorPeriodo
                });
              }
            }
          } catch (err) {
            console.warn(`Erro ao buscar cidade ${id}:`, err.message);
          }
        }
      }

      if (dados.length === 0) {
        setError('Nenhum dado disponível para o período selecionado');
        setLoading(false);
        return;
      }

      // Preparar dados para o gráfico
      const labels = dados.map(d => d.cidade);
      
      let metasValues, resultadosValues, titulo, cor;

      switch (metricaSelecionada) {
        case 'corridas':
          metasValues = dados.map(d => d.metas.metas?.corridas || 0);
          resultadosValues = dados.map(d => d.metas.resultados?.corridas || 0);
          titulo = 'Corridas: Metas vs Realizado';
          cor = { meta: 'rgba(59, 130, 246, 0.8)', realizado: 'rgba(34, 197, 94, 0.8)' };
          break;
        case 'receita':
          metasValues = dados.map(d => d.metas.metas?.receita || 0);
          resultadosValues = dados.map(d => d.metas.resultados?.receita || 0);
          titulo = 'Receita (R$): Metas vs Realizado';
          cor = { meta: 'rgba(251, 191, 36, 0.8)', realizado: 'rgba(34, 197, 94, 0.8)' };
          break;
        case 'motoristas':
          metasValues = dados.map(d => d.metas.metas?.motoristas || 0);
          resultadosValues = dados.map(d => d.metas.resultados?.motoristas || 0);
          titulo = 'Motoristas: Metas vs Realizado';
          cor = { meta: 'rgba(168, 85, 247, 0.8)', realizado: 'rgba(34, 197, 94, 0.8)' };
          break;
        default:
          metasValues = dados.map(d => d.metas.metas?.corridas || 0);
          resultadosValues = dados.map(d => d.metas.resultados?.corridas || 0);
          titulo = 'Corridas: Metas vs Realizado';
          cor = { meta: 'rgba(59, 130, 246, 0.8)', realizado: 'rgba(34, 197, 94, 0.8)' };
      }

      setChartData({
        labels,
        datasets: [
          {
            label: 'Meta',
            data: metasValues,
            backgroundColor: cor.meta,
            borderColor: cor.meta.replace('0.8', '1'),
            borderWidth: 2,
          },
          {
            label: 'Realizado',
            data: resultadosValues,
            backgroundColor: cor.realizado,
            borderColor: cor.realizado.replace('0.8', '1'),
            borderWidth: 2,
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
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
            family: "'Inter', 'Segoe UI', sans-serif"
          },
          padding: 15
        }
      },
      title: {
        display: true,
        text: chartData?.titulo || 'Metas vs Realizado',
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
            
            // Calcular percentual de atingimento
            if (context.dataset.label === 'Realizado') {
              const metaValue = context.chart.data.datasets[0].data[context.dataIndex];
              if (metaValue > 0) {
                const percentual = ((context.parsed.y / metaValue) * 100).toFixed(1);
                label += ` (${percentual}%)`;
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
        <span className="ml-3 text-gray-600">Carregando dados...</span>
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
        {chartData && <Bar data={chartData} options={options} />}
      </div>

      {/* Legenda adicional */}
      <div className="mt-4 text-center text-sm text-gray-500">
        Período: {periodoMeses} {periodoMeses === 1 ? 'mês' : 'meses'}
      </div>
    </div>
  );
};

export default GraficoMetasVsRealizado;
