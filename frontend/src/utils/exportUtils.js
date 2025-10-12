import axios from 'axios';

/**
 * 📊 UTILITÁRIOS DE EXPORTAÇÃO - EXCEL/CSV
 * 
 * Funções para exportar dados do dashboard em diversos formatos
 */

// ========== HELPER: Formatar Valores ==========
const formatarValor = (valor, tipo = 'numero') => {
  if (valor === null || valor === undefined) return 'N/A';
  
  switch (tipo) {
    case 'dinheiro':
      return `R$ ${valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    case 'percentual':
      return `${valor.toFixed(1)}%`;
    case 'numero':
      return valor.toLocaleString('pt-BR');
    case 'data':
      return new Date(valor).toLocaleDateString('pt-BR');
    default:
      return String(valor);
  }
};

// ========== HELPER: Buscar Dados de Todas as Cidades ==========
const buscarDadosTodasCidades = async (periodoMeses = 3) => {
  const cidades = [
    { id: 1, nome: 'Peixoto de Azevedo' },
    { id: 2, nome: 'Nova Monte Verde' },
    { id: 3, nome: 'Matupá' },
    { id: 4, nome: 'Guarantã do Norte' },
    { id: 5, nome: 'Nova Bandeirantes' },
  ];

  const promessas = cidades.map(cidade =>
    axios.get(`http://localhost:8000/api/metas-estrategicas/consolidado/${cidade.id}`)
      .then(response => ({
        cidade: cidade.nome,
        dados: response.data.filter(meta => meta.periodo_meses === periodoMeses)
      }))
      .catch(error => ({
        cidade: cidade.nome,
        dados: [],
        erro: error.message
      }))
  );

  return await Promise.all(promessas);
};

// ========== EXPORTAR CSV (Nativo do Browser) ==========
/**
 * Exporta dados para CSV sem dependências externas
 * @param {Array} dadosCidades - Dados de todas as cidades
 * @param {number} periodoMeses - Período em meses
 */
export const exportarParaCSV = async (periodoMeses = 3) => {
  try {
    // Buscar dados
    const dadosCidades = await buscarDadosTodasCidades(periodoMeses);

    // Construir cabeçalho
    const cabecalho = [
      'Cidade',
      'Período (meses)',
      'Meta Corridas',
      'Realizado Corridas',
      'Atingimento Corridas (%)',
      'Meta Receita (R$)',
      'Realizado Receita (R$)',
      'Atingimento Receita (%)',
      'Meta Motoristas',
      'Realizado Motoristas',
      'Atingimento Motoristas (%)',
      'Atingimento Médio (%)',
      'Status'
    ];

    // Construir linhas
    const linhas = [];
    
    dadosCidades.forEach(({ cidade, dados }) => {
      if (dados && dados.length > 0) {
        dados.forEach(meta => {
          const atingimentoCorridas = meta.meta_corridas > 0 
            ? (meta.resultados_corridas / meta.meta_corridas) * 100 
            : 0;
          const atingimentoReceita = meta.meta_receita > 0
            ? (meta.resultados_receita / meta.meta_receita) * 100
            : 0;
          const atingimentoMotoristas = meta.meta_motoristas > 0
            ? (meta.resultados_motoristas / meta.meta_motoristas) * 100
            : 0;
          const atingimentoMedio = (atingimentoCorridas + atingimentoReceita + atingimentoMotoristas) / 3;

          const status = atingimentoMedio >= 100 ? 'Atingido' :
                        atingimentoMedio >= 80 ? 'Em Progresso' :
                        atingimentoMedio >= 50 ? 'Requer Atenção' :
                        'Crítico';

          linhas.push([
            cidade,
            meta.periodo_meses,
            meta.meta_corridas,
            meta.resultados_corridas,
            atingimentoCorridas.toFixed(1),
            meta.meta_receita.toFixed(2),
            meta.resultados_receita.toFixed(2),
            atingimentoReceita.toFixed(1),
            meta.meta_motoristas,
            meta.resultados_motoristas,
            atingimentoMotoristas.toFixed(1),
            atingimentoMedio.toFixed(1),
            status
          ]);
        });
      }
    });

    // Converter para CSV
    const csvContent = [
      cabecalho.join(','),
      ...linhas.map(linha => linha.join(','))
    ].join('\n');

    // Adicionar BOM para UTF-8 (necessário para acentos no Excel)
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    
    // Download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `metas-estrategicas-${periodoMeses}meses-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    URL.revokeObjectURL(link.href);
    
    return { sucesso: true, registros: linhas.length };
  } catch (error) {
    console.error('Erro ao exportar CSV:', error);
    return { sucesso: false, erro: error.message };
  }
};

// ========== EXPORTAR EXCEL (HTML Table - compatível com Excel) ==========
/**
 * Exporta dados para formato Excel (HTML table com estilos)
 * @param {number} periodoMeses - Período em meses
 */
export const exportarParaExcel = async (periodoMeses = 3) => {
  try {
    // Buscar dados
    const dadosCidades = await buscarDadosTodasCidades(periodoMeses);

    // Calcular totais
    let totalMetaCorridas = 0;
    let totalRealizadoCorridas = 0;
    let totalMetaReceita = 0;
    let totalRealizadoReceita = 0;
    let totalMetaMotoristas = 0;
    let totalRealizadoMotoristas = 0;

    // Construir HTML com estilos
    let html = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <meta charset="UTF-8">
        <style>
          table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }
          th { background-color: #2563eb; color: white; font-weight: bold; padding: 12px; border: 1px solid #ddd; text-align: center; }
          td { padding: 10px; border: 1px solid #ddd; text-align: center; }
          .cidade-header { background-color: #e0f2fe; font-weight: bold; font-size: 14px; }
          .total-row { background-color: #fef3c7; font-weight: bold; }
          .status-atingido { background-color: #d1fae5; color: #065f46; }
          .status-progresso { background-color: #fef3c7; color: #92400e; }
          .status-atencao { background-color: #fed7aa; color: #9a3412; }
          .status-critico { background-color: #fee2e2; color: #991b1b; }
          .numero { text-align: right; }
          .percentual { font-weight: bold; }
        </style>
      </head>
      <body>
        <h1>📊 Relatório de Metas Estratégicas</h1>
        <h3>Período: ${periodoMeses} meses | Data: ${new Date().toLocaleDateString('pt-BR')}</h3>
        <table>
          <thead>
            <tr>
              <th>Cidade</th>
              <th>Período</th>
              <th colspan="3">Corridas</th>
              <th colspan="3">Receita (R$)</th>
              <th colspan="3">Motoristas</th>
              <th>Atingimento<br/>Médio (%)</th>
              <th>Status</th>
            </tr>
            <tr>
              <th colspan="2"></th>
              <th>Meta</th>
              <th>Realizado</th>
              <th>%</th>
              <th>Meta</th>
              <th>Realizado</th>
              <th>%</th>
              <th>Meta</th>
              <th>Realizado</th>
              <th>%</th>
              <th colspan="2"></th>
            </tr>
          </thead>
          <tbody>
    `;

    // Adicionar dados por cidade
    dadosCidades.forEach(({ cidade, dados }) => {
      if (dados && dados.length > 0) {
        dados.forEach(meta => {
          const atingimentoCorridas = meta.meta_corridas > 0 
            ? (meta.resultados_corridas / meta.meta_corridas) * 100 
            : 0;
          const atingimentoReceita = meta.meta_receita > 0
            ? (meta.resultados_receita / meta.meta_receita) * 100
            : 0;
          const atingimentoMotoristas = meta.meta_motoristas > 0
            ? (meta.resultados_motoristas / meta.meta_motoristas) * 100
            : 0;
          const atingimentoMedio = (atingimentoCorridas + atingimentoReceita + atingimentoMotoristas) / 3;

          const statusClass = atingimentoMedio >= 100 ? 'status-atingido' :
                             atingimentoMedio >= 80 ? 'status-progresso' :
                             atingimentoMedio >= 50 ? 'status-atencao' :
                             'status-critico';

          const statusTexto = atingimentoMedio >= 100 ? '✅ Atingido' :
                             atingimentoMedio >= 80 ? '🟡 Em Progresso' :
                             atingimentoMedio >= 50 ? '🟠 Requer Atenção' :
                             '🔴 Crítico';

          // Acumular totais
          totalMetaCorridas += meta.meta_corridas;
          totalRealizadoCorridas += meta.resultados_corridas;
          totalMetaReceita += meta.meta_receita;
          totalRealizadoReceita += meta.resultados_receita;
          totalMetaMotoristas += meta.meta_motoristas;
          totalRealizadoMotoristas += meta.resultados_motoristas;

          html += `
            <tr>
              <td class="cidade-header">${cidade}</td>
              <td>${meta.periodo_meses} meses</td>
              <td class="numero">${meta.meta_corridas}</td>
              <td class="numero">${meta.resultados_corridas}</td>
              <td class="percentual">${atingimentoCorridas.toFixed(1)}%</td>
              <td class="numero">${meta.meta_receita.toFixed(2)}</td>
              <td class="numero">${meta.resultados_receita.toFixed(2)}</td>
              <td class="percentual">${atingimentoReceita.toFixed(1)}%</td>
              <td class="numero">${meta.meta_motoristas}</td>
              <td class="numero">${meta.resultados_motoristas}</td>
              <td class="percentual">${atingimentoMotoristas.toFixed(1)}%</td>
              <td class="percentual">${atingimentoMedio.toFixed(1)}%</td>
              <td class="${statusClass}">${statusTexto}</td>
            </tr>
          `;
        });
      }
    });

    // Adicionar linha de totais
    const totalAtingimentoCorridas = totalMetaCorridas > 0 
      ? (totalRealizadoCorridas / totalMetaCorridas) * 100 
      : 0;
    const totalAtingimentoReceita = totalMetaReceita > 0
      ? (totalRealizadoReceita / totalMetaReceita) * 100
      : 0;
    const totalAtingimentoMotoristas = totalMetaMotoristas > 0
      ? (totalRealizadoMotoristas / totalMetaMotoristas) * 100
      : 0;
    const totalAtingimentoMedio = (totalAtingimentoCorridas + totalAtingimentoReceita + totalAtingimentoMotoristas) / 3;

    html += `
            <tr class="total-row">
              <td colspan="2"><strong>TOTAL GERAL</strong></td>
              <td class="numero">${totalMetaCorridas}</td>
              <td class="numero">${totalRealizadoCorridas}</td>
              <td class="percentual">${totalAtingimentoCorridas.toFixed(1)}%</td>
              <td class="numero">${totalMetaReceita.toFixed(2)}</td>
              <td class="numero">${totalRealizadoReceita.toFixed(2)}</td>
              <td class="percentual">${totalAtingimentoReceita.toFixed(1)}%</td>
              <td class="numero">${totalMetaMotoristas}</td>
              <td class="numero">${totalRealizadoMotoristas}</td>
              <td class="percentual">${totalAtingimentoMotoristas.toFixed(1)}%</td>
              <td class="percentual">${totalAtingimentoMedio.toFixed(1)}%</td>
              <td>-</td>
            </tr>
          </tbody>
        </table>
        
        <br/><br/>
        <p><strong>Legenda:</strong></p>
        <ul>
          <li>✅ Atingido: ≥ 100% da meta</li>
          <li>🟡 Em Progresso: 80% - 99% da meta</li>
          <li>🟠 Requer Atenção: 50% - 79% da meta</li>
          <li>🔴 Crítico: < 50% da meta</li>
        </ul>
        
        <p><em>Relatório gerado automaticamente em ${new Date().toLocaleString('pt-BR')}</em></p>
      </body>
      </html>
    `;

    // Criar blob e fazer download
    const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `metas-estrategicas-${periodoMeses}meses-${new Date().toISOString().split('T')[0]}.xls`;
    link.click();
    
    URL.revokeObjectURL(link.href);
    
    return { 
      sucesso: true, 
      registros: dadosCidades.reduce((sum, cidade) => sum + cidade.dados.length, 0),
      totais: {
        corridas: { meta: totalMetaCorridas, realizado: totalRealizadoCorridas, percentual: totalAtingimentoCorridas },
        receita: { meta: totalMetaReceita, realizado: totalRealizadoReceita, percentual: totalAtingimentoReceita },
        motoristas: { meta: totalMetaMotoristas, realizado: totalRealizadoMotoristas, percentual: totalAtingimentoMotoristas },
        medio: totalAtingimentoMedio
      }
    };
  } catch (error) {
    console.error('Erro ao exportar Excel:', error);
    return { sucesso: false, erro: error.message };
  }
};

// ========== EXPORTAR JSON (Para APIs ou backup) ==========
/**
 * Exporta dados brutos em JSON
 * @param {number} periodoMeses - Período em meses
 */
export const exportarParaJSON = async (periodoMeses = 3) => {
  try {
    const dadosCidades = await buscarDadosTodasCidades(periodoMeses);
    
    const json = JSON.stringify(dadosCidades, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `metas-estrategicas-${periodoMeses}meses-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(link.href);
    
    return { sucesso: true, cidades: dadosCidades.length };
  } catch (error) {
    console.error('Erro ao exportar JSON:', error);
    return { sucesso: false, erro: error.message };
  }
};

export default {
  exportarParaCSV,
  exportarParaExcel,
  exportarParaJSON
};
