import axios from 'axios';

/**
 * 📄 UTILITÁRIOS DE EXPORTAÇÃO - PDF
 * 
 * Funções para exportar dashboard em PDF usando browser print API
 * Não requer jsPDF ou html2canvas
 */

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
        cidadeId: cidade.id,
        dados: response.data.filter(meta => meta.periodo_meses === periodoMeses)
      }))
      .catch(error => ({
        cidade: cidade.nome,
        cidadeId: cidade.id,
        dados: [],
        erro: error.message
      }))
  );

  return await Promise.all(promessas);
};

// ========== EXPORTAR PDF (Browser Print API) ==========
/**
 * Gera PDF usando window.print() com HTML customizado
 * @param {number} periodoMeses - Período em meses
 * @param {object} options - Opções de exportação
 */
export const exportarParaPDF = async (periodoMeses = 3, options = {}) => {
  try {
    const {
      incluirGraficos = false, // Se true, tenta incluir gráficos (experimental)
      incluirKPIs = true,
      incluirTabela = true,
      incluirLegenda = true
    } = options;

    // Buscar dados
    const dadosCidades = await buscarDadosTodasCidades(periodoMeses);

    // Calcular KPIs globais
    let totalMetaCorridas = 0;
    let totalRealizadoCorridas = 0;
    let totalMetaReceita = 0;
    let totalRealizadoReceita = 0;
    let totalMetaMotoristas = 0;
    let totalRealizadoMotoristas = 0;

    dadosCidades.forEach(({ dados }) => {
      dados.forEach(meta => {
        totalMetaCorridas += meta.meta_corridas;
        totalRealizadoCorridas += meta.resultados_corridas;
        totalMetaReceita += meta.meta_receita;
        totalRealizadoReceita += meta.resultados_receita;
        totalMetaMotoristas += meta.meta_motoristas;
        totalRealizadoMotoristas += meta.resultados_motoristas;
      });
    });

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

    // Identificar melhor e pior cidade
    let melhorCidade = { nome: 'N/A', percentual: 0 };
    let piorCidade = { nome: 'N/A', percentual: 100 };

    dadosCidades.forEach(({ cidade, dados }) => {
      if (dados.length > 0) {
        const meta = dados[0];
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

        if (atingimentoMedio > melhorCidade.percentual) {
          melhorCidade = { nome: cidade, percentual: atingimentoMedio };
        }
        if (atingimentoMedio < piorCidade.percentual) {
          piorCidade = { nome: cidade, percentual: atingimentoMedio };
        }
      }
    });

    // Construir HTML para impressão
    let html = `
      <!DOCTYPE html>
      <html lang="pt-BR">
      <head>
        <meta charset="UTF-8">
        <title>Relatório de Metas Estratégicas - ${periodoMeses} meses</title>
        <style>
          @page {
            size: A4 landscape;
            margin: 1cm;
          }
          
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            color: #1f2937;
            background: white;
            padding: 20px;
          }
          
          @media print {
            body {
              print-color-adjust: exact;
              -webkit-print-color-adjust: exact;
            }
          }
          
          .header {
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
          }
          
          .header h1 {
            color: #1e40af;
            font-size: 24pt;
            margin-bottom: 5px;
          }
          
          .header .subtitle {
            color: #6b7280;
            font-size: 11pt;
          }
          
          .header .data {
            color: #9ca3af;
            font-size: 9pt;
            margin-top: 5px;
          }
          
          .kpis {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
            page-break-inside: avoid;
          }
          
          .kpi-card {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            background: #f9fafb;
          }
          
          .kpi-card.destaque {
            border-color: #2563eb;
            background: #eff6ff;
          }
          
          .kpi-card h3 {
            font-size: 9pt;
            color: #6b7280;
            margin-bottom: 8px;
            text-transform: uppercase;
          }
          
          .kpi-card .valor {
            font-size: 20pt;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 5px;
          }
          
          .kpi-card .meta {
            font-size: 8pt;
            color: #6b7280;
          }
          
          .kpi-card .percentual {
            font-size: 12pt;
            font-weight: bold;
            margin-top: 5px;
          }
          
          .percentual.verde { color: #059669; }
          .percentual.amarelo { color: #d97706; }
          .percentual.laranja { color: #ea580c; }
          .percentual.vermelho { color: #dc2626; }
          
          .secao-titulo {
            font-size: 14pt;
            font-weight: bold;
            color: #1e40af;
            margin: 30px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
            page-break-after: avoid;
          }
          
          table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            font-size: 9pt;
            page-break-inside: auto;
          }
          
          table thead {
            background: #2563eb;
            color: white;
          }
          
          table th {
            padding: 10px;
            text-align: center;
            font-weight: bold;
            border: 1px solid #1e40af;
          }
          
          table td {
            padding: 8px;
            text-align: center;
            border: 1px solid #e5e7eb;
          }
          
          table tbody tr:nth-child(even) {
            background: #f9fafb;
          }
          
          table tbody tr:hover {
            background: #eff6ff;
          }
          
          .cidade-col {
            font-weight: bold;
            text-align: left !important;
            background: #e0f2fe !important;
          }
          
          .numero {
            text-align: right !important;
            font-family: 'Courier New', monospace;
          }
          
          .total-row {
            background: #fef3c7 !important;
            font-weight: bold;
          }
          
          .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 8pt;
            font-weight: bold;
          }
          
          .status-atingido { background: #d1fae5; color: #065f46; }
          .status-progresso { background: #fef3c7; color: #92400e; }
          .status-atencao { background: #fed7aa; color: #9a3412; }
          .status-critico { background: #fee2e2; color: #991b1b; }
          
          .legenda {
            margin-top: 30px;
            padding: 15px;
            background: #f9fafb;
            border-radius: 8px;
            font-size: 9pt;
            page-break-inside: avoid;
          }
          
          .legenda h4 {
            margin-bottom: 10px;
            color: #1e40af;
          }
          
          .legenda ul {
            list-style: none;
            padding-left: 0;
          }
          
          .legenda li {
            margin: 5px 0;
            padding-left: 20px;
            position: relative;
          }
          
          .legenda li::before {
            content: '●';
            position: absolute;
            left: 0;
            font-size: 14pt;
          }
          
          .legenda li.verde::before { color: #059669; }
          .legenda li.amarelo::before { color: #d97706; }
          .legenda li.laranja::before { color: #ea580c; }
          .legenda li.vermelho::before { color: #dc2626; }
          
          .footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            font-size: 8pt;
            color: #9ca3af;
            page-break-inside: avoid;
          }
          
          .destaque-cidade {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 30px;
          }
          
          .destaque-card {
            padding: 15px;
            border-radius: 8px;
            text-align: center;
          }
          
          .destaque-card.melhor {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border: 2px solid #059669;
          }
          
          .destaque-card.pior {
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            border: 2px solid #dc2626;
          }
          
          .destaque-card h4 {
            font-size: 10pt;
            margin-bottom: 8px;
          }
          
          .destaque-card .cidade-nome {
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 5px;
          }
          
          .destaque-card .percentual-destaque {
            font-size: 14pt;
            font-weight: bold;
          }
          
          @media print {
            .no-print { display: none !important; }
          }
        </style>
      </head>
      <body>
        <!-- HEADER -->
        <div class="header">
          <h1>📊 Relatório de Metas Estratégicas</h1>
          <div class="subtitle">Sistema de Mobilidade Urbana - Dashboard Executivo</div>
          <div class="data">
            Período: ${periodoMeses} meses | 
            Gerado em: ${new Date().toLocaleString('pt-BR')} | 
            Total de Cidades: ${dadosCidades.length}
          </div>
        </div>
    `;

    // Adicionar KPIs
    if (incluirKPIs) {
      html += `
        <div class="secao-titulo">📈 Indicadores Principais</div>
        <div class="kpis">
          <!-- Total Corridas -->
          <div class="kpi-card">
            <h3>🚗 Total de Corridas</h3>
            <div class="valor">${totalRealizadoCorridas.toLocaleString('pt-BR')}</div>
            <div class="meta">Meta: ${totalMetaCorridas.toLocaleString('pt-BR')}</div>
            <div class="percentual ${totalAtingimentoCorridas >= 100 ? 'verde' : totalAtingimentoCorridas >= 80 ? 'amarelo' : totalAtingimentoCorridas >= 50 ? 'laranja' : 'vermelho'}">
              ${totalAtingimentoCorridas.toFixed(1)}%
            </div>
          </div>
          
          <!-- Total Receita -->
          <div class="kpi-card">
            <h3>💰 Receita Total</h3>
            <div class="valor">R$ ${totalRealizadoReceita.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</div>
            <div class="meta">Meta: R$ ${totalMetaReceita.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</div>
            <div class="percentual ${totalAtingimentoReceita >= 100 ? 'verde' : totalAtingimentoReceita >= 80 ? 'amarelo' : totalAtingimentoReceita >= 50 ? 'laranja' : 'vermelho'}">
              ${totalAtingimentoReceita.toFixed(1)}%
            </div>
          </div>
          
          <!-- Total Motoristas -->
          <div class="kpi-card">
            <h3>👤 Motoristas Ativos</h3>
            <div class="valor">${totalRealizadoMotoristas.toLocaleString('pt-BR')}</div>
            <div class="meta">Meta: ${totalMetaMotoristas.toLocaleString('pt-BR')}</div>
            <div class="percentual ${totalAtingimentoMotoristas >= 100 ? 'verde' : totalAtingimentoMotoristas >= 80 ? 'amarelo' : totalAtingimentoMotoristas >= 50 ? 'laranja' : 'vermelho'}">
              ${totalAtingimentoMotoristas.toFixed(1)}%
            </div>
          </div>
          
          <!-- Atingimento Médio -->
          <div class="kpi-card destaque">
            <h3>🎯 Atingimento Médio</h3>
            <div class="valor">${totalAtingimentoMedio.toFixed(1)}%</div>
            <div class="meta">Média das 3 métricas</div>
            <div class="percentual ${totalAtingimentoMedio >= 100 ? 'verde' : totalAtingimentoMedio >= 80 ? 'amarelo' : totalAtingimentoMedio >= 50 ? 'laranja' : 'vermelho'}">
              ${totalAtingimentoMedio >= 100 ? '✅ Atingido' : totalAtingimentoMedio >= 80 ? '🟡 Progresso' : totalAtingimentoMedio >= 50 ? '🟠 Atenção' : '🔴 Crítico'}
            </div>
          </div>
        </div>
        
        <!-- Destaques -->
        <div class="secao-titulo">🏆 Destaques</div>
        <div class="destaque-cidade">
          <div class="destaque-card melhor">
            <h4>🏆 Melhor Desempenho</h4>
            <div class="cidade-nome">${melhorCidade.nome}</div>
            <div class="percentual-destaque">${melhorCidade.percentual.toFixed(1)}%</div>
          </div>
          <div class="destaque-card pior">
            <h4>⚠️ Necessita Atenção</h4>
            <div class="cidade-nome">${piorCidade.nome}</div>
            <div class="percentual-destaque">${piorCidade.percentual.toFixed(1)}%</div>
          </div>
        </div>
      `;
    }

    // Adicionar Tabela
    if (incluirTabela) {
      html += `
        <div class="secao-titulo">📋 Detalhamento por Cidade</div>
        <table>
          <thead>
            <tr>
              <th rowspan="2">Cidade</th>
              <th rowspan="2">Período</th>
              <th colspan="3">Corridas</th>
              <th colspan="3">Receita (R$)</th>
              <th colspan="3">Motoristas</th>
              <th rowspan="2">Atingimento<br/>Médio</th>
              <th rowspan="2">Status</th>
            </tr>
            <tr>
              <th>Meta</th>
              <th>Real.</th>
              <th>%</th>
              <th>Meta</th>
              <th>Real.</th>
              <th>%</th>
              <th>Meta</th>
              <th>Real.</th>
              <th>%</th>
            </tr>
          </thead>
          <tbody>
      `;

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
                               atingimentoMedio >= 80 ? '🟡 Progresso' :
                               atingimentoMedio >= 50 ? '🟠 Atenção' :
                               '🔴 Crítico';

            html += `
              <tr>
                <td class="cidade-col">${cidade}</td>
                <td>${meta.periodo_meses} meses</td>
                <td class="numero">${meta.meta_corridas}</td>
                <td class="numero">${meta.resultados_corridas}</td>
                <td class="numero">${atingimentoCorridas.toFixed(1)}%</td>
                <td class="numero">${meta.meta_receita.toFixed(2)}</td>
                <td class="numero">${meta.resultados_receita.toFixed(2)}</td>
                <td class="numero">${atingimentoReceita.toFixed(1)}%</td>
                <td class="numero">${meta.meta_motoristas}</td>
                <td class="numero">${meta.resultados_motoristas}</td>
                <td class="numero">${atingimentoMotoristas.toFixed(1)}%</td>
                <td class="numero">${atingimentoMedio.toFixed(1)}%</td>
                <td><span class="status-badge ${statusClass}">${statusTexto}</span></td>
              </tr>
            `;
          });
        }
      });

      // Linha de totais
      html += `
            <tr class="total-row">
              <td colspan="2"><strong>TOTAL GERAL</strong></td>
              <td class="numero">${totalMetaCorridas}</td>
              <td class="numero">${totalRealizadoCorridas}</td>
              <td class="numero">${totalAtingimentoCorridas.toFixed(1)}%</td>
              <td class="numero">${totalMetaReceita.toFixed(2)}</td>
              <td class="numero">${totalRealizadoReceita.toFixed(2)}</td>
              <td class="numero">${totalAtingimentoReceita.toFixed(1)}%</td>
              <td class="numero">${totalMetaMotoristas}</td>
              <td class="numero">${totalRealizadoMotoristas}</td>
              <td class="numero">${totalAtingimentoMotoristas.toFixed(1)}%</td>
              <td class="numero">${totalAtingimentoMedio.toFixed(1)}%</td>
              <td>-</td>
            </tr>
          </tbody>
        </table>
      `;
    }

    // Adicionar Legenda
    if (incluirLegenda) {
      html += `
        <div class="legenda">
          <h4>📖 Legenda de Status</h4>
          <ul>
            <li class="verde"><strong>✅ Atingido:</strong> Atingimento ≥ 100% da meta</li>
            <li class="amarelo"><strong>🟡 Em Progresso:</strong> Atingimento entre 80% e 99% da meta</li>
            <li class="laranja"><strong>🟠 Requer Atenção:</strong> Atingimento entre 50% e 79% da meta</li>
            <li class="vermelho"><strong>🔴 Crítico:</strong> Atingimento < 50% da meta</li>
          </ul>
        </div>
      `;
    }

    // Footer
    html += `
        <div class="footer">
          <p>
            <strong>Dashboard de Mobilidade Urbana</strong> | 
            Sistema de Metas Estratégicas | 
            Relatório gerado automaticamente em ${new Date().toLocaleString('pt-BR')}
          </p>
          <p style="margin-top: 5px;">
            Fonte de Dados: PostgreSQL (rides_data, driver_personal_details, metas_estrategicas) | 
            Backend: FastAPI | Frontend: React
          </p>
        </div>
      </body>
      </html>
    `;

    // Abrir em nova janela e imprimir
    const printWindow = window.open('', '_blank', 'width=1200,height=800');
    if (!printWindow) {
      throw new Error('Popup bloqueado! Por favor, permita popups para este site.');
    }

    printWindow.document.write(html);
    printWindow.document.close();

    // Aguardar carregamento e abrir diálogo de impressão
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print();
        // Fechar janela após impressão (opcional)
        // printWindow.onafterprint = () => printWindow.close();
      }, 500);
    };

    return { 
      sucesso: true, 
      mensagem: 'Janela de impressão aberta. Use "Salvar como PDF" para gerar o arquivo.',
      cidades: dadosCidades.length
    };

  } catch (error) {
    console.error('Erro ao exportar PDF:', error);
    return { sucesso: false, erro: error.message };
  }
};

/**
 * Exporta apenas os KPIs em formato compacto para PDF
 */
export const exportarKPIsParaPDF = async (periodoMeses = 3) => {
  return exportarParaPDF(periodoMeses, {
    incluirGraficos: false,
    incluirKPIs: true,
    incluirTabela: false,
    incluirLegenda: false
  });
};

/**
 * Exporta relatório completo (KPIs + Tabela + Legenda)
 */
export const exportarRelatorioCompleto = async (periodoMeses = 3) => {
  return exportarParaPDF(periodoMeses, {
    incluirGraficos: false,
    incluirKPIs: true,
    incluirTabela: true,
    incluirLegenda: true
  });
};

export default {
  exportarParaPDF,
  exportarKPIsParaPDF,
  exportarRelatorioCompleto
};
