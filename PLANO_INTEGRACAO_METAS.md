# 🎯 PLANO DE AÇÃO: INTEGRAÇÃO SISTEMA DE METAS

**Projeto:** Dashboard Mobilidade Urbana - Integração Aba Metas  
**Data:** 10 de Outubro de 2025  
**Estimativa Total:** 18-27 horas (2-3 semanas de desenvolvimento)  
**Status Atual:** ✅ Refatoração concluída com sucesso (44% redução de código)

---

## 📋 SUMÁRIO EXECUTIVO

### Objetivo
Transformar a aba de Metas (atualmente isolada) em um sistema integrado que:
1. ✅ Consome dados reais de motoristas e corridas via APIs
2. ✅ Integra sistema financeiro com documentação de gastos
3. ✅ Exibe progresso real vs metas planejadas
4. ✅ Rastreia orçamento (Empenhado → Pago → Liquidado)
5. ✅ Simplifica lógica complexa existente

### Contexto do Sistema
- **3 Fases de Expansão:** Ago-Dez 2025 (45 dias cada)
- **7 Cidades:** Peixoto de Azevedo, Matupá, Guarantã do Norte, Alta Floresta, Paranaíta, Colíder, Nova Canaã do Norte
- **Orçamento Total:** R$ 19.790 (Fase 1: R$4.060 | Fase 2: R$6.700 | Fase 3: R$9.030)
- **Cada Fase:** Part 1 (Motoristas) + Part 2 (Corridas/Passageiros)

---

## 🗂️ FASE 1: ANÁLISE E PLANEJAMENTO (1-2 horas)

### 1.1 Mapeamento de Endpoints Disponíveis ✅

**APIs Backend Identificadas:**

#### **Drivers API** (`/api/drivers/`)
```javascript
// Endpoints utilizáveis
GET /api/drivers/kpis?period=3_months&city={cidade}
// Retorna: total_drivers, active_drivers, total_rides, avg_rating, etc.

GET /api/drivers/by-city?period=3_months
// Retorna: motoristas agrupados por cidade com métricas

GET /api/drivers/cities
// Retorna: ['Peixoto de Azevedo', 'Matupá', ...]

GET /api/drivers/analytics?period=3_months&city={cidade}
// Retorna: distribuições de status, performance, cidade
```

#### **Campanhas API** (`/api/campanhas`)
```javascript
GET /api/campanhas
// Retorna: lista de todas as campanhas

POST /api/campanhas
{
  "nome": "Campanha Fase 1 - Peixoto",
  "fase": "Fase 1",
  "cidade": "Peixoto de Azevedo",
  "parte_campanha": "Part 1",
  "tipo_campanha": "motoristas",
  "meta_quantidade": 1,
  "orcamento_previsto": 460,
  "status_financeiro": "empenhado"
}

PUT /api/campanhas/{id}
// Atualiza campanha (custo_real, status_financeiro, etc.)
```

#### **Financeiro API** (`/api/financeiro/`)
```javascript
GET /api/financeiro/overview?periodo=30
// Retorna: total_gastos, gastos_por_categoria, top_gastos[], etc.

GET /api/financeiro/categorias?periodo=30
// Retorna: gastos detalhados por categoria

PUT /api/financeiro/gastos/{id}
// Atualiza gasto (vincular a campanha, etc.)
```

### 1.2 Definição de Contratos de Dados

**Estrutura de Dados Integrada:**
```typescript
interface MetaIntegrada {
  fase: 'Fase 1' | 'Fase 2' | 'Fase 3';
  periodo: string; // "01/ago - 14/set"
  status: 'planejada' | 'em_execucao' | 'concluida';
  
  cidades: CidadeMeta[];
  
  orcamento: {
    previsto: number;      // Total planejado
    empenhado: number;     // Reservado
    pago: number;          // Efetivamente pago
    liquidado: number;     // Finalizado
    disponivel: number;    // previsto - empenhado
  };
}

interface CidadeMeta {
  nome: string;
  populacao: number;
  publico_alvo: number;
  
  part1: ParteMeta; // Motoristas
  part2: ParteMeta; // Corridas
  
  // Dados reais da API
  motoristas_reais: {
    total: number;        // ← /api/drivers/by-city
    ativos: number;
    inativos: number;
    ultima_atualizacao: string;
  };
  
  corridas_reais: {
    total: number;        // ← /api/drivers/kpis (city filtered)
    canceladas: number;
    concluidas: number;
    receita: number;
    ultima_atualizacao: string;
  };
  
  financeiro_real: {
    gastos: GastoDetalhado[];  // ← /api/financeiro/overview
    total_gasto: number;
    documentos_pendentes: number;
    ultima_atualizacao: string;
  };
}

interface ParteMeta {
  tipo: 'motoristas' | 'corridas';
  meta: number;              // Meta planejada
  realizado: number;         // Dados reais da API
  progresso: number;         // (realizado / meta) * 100
  status: 'atrasado' | 'no_prazo' | 'adiantado';
  
  orcamento: number;         // Previsto
  gasto_real: number;        // Soma dos gastos vinculados
  saldo: number;             // orcamento - gasto_real
  
  campanhas: Campanha[];     // Campanhas vinculadas
  documentos: Documento[];   // Comprovantes anexados
}

interface GastoDetalhado {
  id: number;
  data: string;
  valor: number;
  descricao: string;
  categoria: 'facebook_ads' | 'hotel' | 'restaurante' | 'combustivel' | 'outros';
  fornecedor: string;
  tipo_documento: 'Nota Fiscal' | 'Comprovante de Pagamento' | 'Recibo';
  arquivo_url: string;
  possui_nota_fiscal: boolean;
  numero_nf?: string;
  status_aprovacao: 'pendente' | 'aprovado' | 'rejeitado';
  campanha_vinculada?: number; // ID da campanha
}
```

### 1.3 Arquitetura de Componentes

```
src/
├── components/
│   └── MetasCidades/
│       ├── MetasCidades.jsx (orquestrador principal)
│       │
│       ├── StatusFase.jsx ← ATUALIZAR (adicionar dados reais)
│       ├── TabelaExecucao.jsx ← ATUALIZAR (integrar APIs)
│       ├── FaseDetailsContent.jsx ← ATUALIZAR (mostrar documentos)
│       │
│       ├── ExpenseDocumentation.jsx ← NOVO
│       ├── ProgressIndicator.jsx ← NOVO
│       ├── BudgetTracker.jsx ← NOVO
│       ├── AlertsPanel.jsx ← NOVO
│       └── IntegratedDashboard.jsx ← NOVO
│       │
│       └── hooks/
│           ├── usePlanoDinamico.js (existente)
│           ├── useCruzamentoDados.js (existente)
│           │
│           ├── useDriversByCidade.js ← NOVO
│           ├── useRidesByCidade.js ← NOVO
│           ├── useCampaignExpenses.js ← NOVO
│           ├── useMetasProgress.js ← NOVO (master hook)
│           └── useFinancialDocuments.js ← NOVO
```

---

## 🔌 FASE 2: HOOKS DE INTEGRAÇÃO COM APIs (3-4 horas)

### 2.1 Hook: useDriversByCidade.js

**Arquivo:** `frontend/src/components/MetasCidades/hooks/useDriversByCidade.js`

```javascript
import { useState, useEffect } from 'react';

/**
 * Hook para buscar dados de motoristas por cidade
 * @param {string} cidade - Nome da cidade
 * @param {string} period - Período de análise (7_days, 30_days, 3_months)
 * @returns {Object} { data, loading, error, refresh }
 */
export const useDriversByCidade = (cidade = 'all', period = '3_months') => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchDrivers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Buscar KPIs gerais filtrados por cidade
      const kpisResponse = await fetch(
        `${API_URL}/api/drivers/kpis?period=${period}&city=${cidade}`
      );
      
      if (!kpisResponse.ok) throw new Error('Erro ao buscar KPIs de motoristas');
      
      const kpisData = await kpisResponse.json();
      
      // Processar dados
      const processedData = {
        cidade: cidade,
        total_motoristas: kpisData.data?.total_drivers || 0,
        motoristas_ativos: kpisData.data?.active_drivers || 0,
        motoristas_inativos: kpisData.data?.inactive_drivers || 0,
        rating_medio: kpisData.data?.avg_rating || 0,
        horas_online: kpisData.data?.avg_hours_online || 0,
        ultima_atualizacao: new Date().toISOString(),
      };
      
      setData(processedData);
    } catch (err) {
      console.error('Erro useDriversByCidade:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchDrivers();
  }, [cidade, period]);
  
  return {
    data,
    loading,
    error,
    refresh: fetchDrivers
  };
};
```

### 2.2 Hook: useRidesByCidade.js

**Arquivo:** `frontend/src/components/MetasCidades/hooks/useRidesByCidade.js`

```javascript
import { useState, useEffect } from 'react';

/**
 * Hook para buscar dados de corridas por cidade
 */
export const useRidesByCidade = (cidade = 'all', period = '3_months') => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchRides = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Buscar KPIs que incluem dados de corridas
      const response = await fetch(
        `${API_URL}/api/drivers/kpis?period=${period}&city=${cidade}`
      );
      
      if (!response.ok) throw new Error('Erro ao buscar dados de corridas');
      
      const kpisData = await response.json();
      
      const processedData = {
        cidade: cidade,
        total_corridas: kpisData.data?.total_rides || 0,
        corridas_concluidas: kpisData.data?.total_rides_completed || 0,
        corridas_canceladas: kpisData.data?.cancelled_rides || 0,
        receita_estimada: kpisData.data?.total_revenue || 0,
        distancia_total: kpisData.data?.total_distance || 0,
        taxa_conclusao: kpisData.data?.completion_rate || 0,
        ultima_atualizacao: new Date().toISOString(),
      };
      
      setData(processedData);
    } catch (err) {
      console.error('Erro useRidesByCidade:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchRides();
  }, [cidade, period]);
  
  return { data, loading, error, refresh: fetchRides };
};
```

### 2.3 Hook: useCampaignExpenses.js

**Arquivo:** `frontend/src/components/MetasCidades/hooks/useCampaignExpenses.js`

```javascript
import { useState, useEffect } from 'react';

/**
 * Hook para buscar gastos de campanhas
 */
export const useCampaignExpenses = (fase = null, cidade = null) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchExpenses = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Buscar overview financeiro
      const financeiroResponse = await fetch(
        `${API_URL}/api/financeiro/overview?periodo=90`
      );
      
      if (!financeiroResponse.ok) throw new Error('Erro ao buscar dados financeiros');
      
      const financeiroData = await financeiroResponse.json();
      
      // Buscar campanhas
      const campanhasResponse = await fetch(`${API_URL}/api/campanhas`);
      
      if (!campanhasResponse.ok) throw new Error('Erro ao buscar campanhas');
      
      const campanhasData = await campanhasResponse.json();
      
      // Filtrar campanhas por fase e cidade
      let campanhasFiltradas = campanhasData;
      
      if (fase) {
        campanhasFiltradas = campanhasFiltradas.filter(c => c.fase === fase);
      }
      
      if (cidade) {
        campanhasFiltradas = campanhasFiltradas.filter(c => c.cidade === cidade);
      }
      
      // Calcular totais
      const orcamento_previsto = campanhasFiltradas.reduce(
        (sum, c) => sum + parseFloat(c.orcamento_previsto || 0), 
        0
      );
      
      const custo_real = campanhasFiltradas.reduce(
        (sum, c) => sum + parseFloat(c.custo_real || 0), 
        0
      );
      
      // Processar gastos (top_gastos do financeiro)
      const gastosRelevantes = financeiroData.top_gastos || [];
      
      const processedData = {
        fase,
        cidade,
        campanhas: campanhasFiltradas,
        orcamento_previsto,
        custo_real,
        saldo: orcamento_previsto - custo_real,
        gastos: gastosRelevantes,
        total_gastos: financeiroData.total_gastos || 0,
        gastos_por_categoria: financeiroData.gastos_por_categoria || {},
        documentos_pendentes: gastosRelevantes.filter(
          g => !g.possui_nota_fiscal
        ).length,
        ultima_atualizacao: new Date().toISOString(),
      };
      
      setData(processedData);
    } catch (err) {
      console.error('Erro useCampaignExpenses:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchExpenses();
  }, [fase, cidade]);
  
  return { data, loading, error, refresh: fetchExpenses };
};
```

### 2.4 Hook Master: useMetasProgress.js

**Arquivo:** `frontend/src/components/MetasCidades/hooks/useMetasProgress.js`

```javascript
import { useState, useEffect } from 'react';
import { useDriversByCidade } from './useDriversByCidade.js';
import { useRidesByCidade } from './useRidesByCidade.js';
import { useCampaignExpenses } from './useCampaignExpenses.js';
import { PLANO_EXECUCAO } from '../../../constants/cidadesConstants.js';

/**
 * Hook Master que combina todos os dados
 * Integra: Plano + Motoristas + Corridas + Financeiro
 */
export const useMetasProgress = (fase) => {
  const [consolidatedData, setConsolidatedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Dados do plano estático
  const planoFase = PLANO_EXECUCAO[fase];
  
  // Buscar dados financeiros da fase
  const { 
    data: expensesData, 
    loading: expensesLoading 
  } = useCampaignExpenses(fase, null);
  
  useEffect(() => {
    if (!planoFase) {
      setError('Fase não encontrada no plano de execução');
      setLoading(false);
      return;
    }
    
    const fetchAllData = async () => {
      setLoading(true);
      
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        
        // Buscar dados reais para cada cidade da fase
        const cidadesComDados = await Promise.all(
          planoFase.cidades.map(async (nomeCidade) => {
            // Buscar dados de motoristas
            const driversResponse = await fetch(
              `${API_URL}/api/drivers/kpis?period=3_months&city=${nomeCidade}`
            );
            const driversData = await driversResponse.json();
            
            // Buscar dados de corridas (mesmo endpoint, filtrando)
            const ridesData = driversData; // KPIs já contém dados de corridas
            
            // Extrair metas do plano
            const metaPart1 = planoFase.part1?.metas?.[nomeCidade] || 0;
            const metaPart2 = planoFase.part2?.metas?.[nomeCidade] || 0;
            
            // Calcular progresso
            const motoristaRealizados = driversData.data?.total_drivers || 0;
            const corridasRealizadas = driversData.data?.total_rides || 0;
            
            const progressoPart1 = metaPart1 > 0 
              ? (motoristaRealizados / metaPart1) * 100 
              : 0;
              
            const progressoPart2 = metaPart2 > 0 
              ? (corridasRealizadas / metaPart2) * 100 
              : 0;
            
            return {
              nome: nomeCidade,
              part1: {
                tipo: 'motoristas',
                meta: metaPart1,
                realizado: motoristaRealizados,
                progresso: progressoPart1,
                status: progressoPart1 >= 100 ? 'concluido' : 
                        progressoPart1 >= 70 ? 'no_prazo' : 'atrasado',
              },
              part2: {
                tipo: 'corridas',
                meta: metaPart2,
                realizado: corridasRealizadas,
                progresso: progressoPart2,
                status: progressoPart2 >= 100 ? 'concluido' : 
                        progressoPart2 >= 70 ? 'no_prazo' : 'atrasado',
              },
              dados_reais: {
                motoristas: driversData.data,
                corridas: ridesData.data,
                ultima_atualizacao: new Date().toISOString(),
              }
            };
          })
        );
        
        // Consolidar dados
        const consolidated = {
          fase: fase,
          periodo: planoFase.periodo,
          status: planoFase.status,
          cidades: cidadesComDados,
          orcamento: {
            ...planoFase.orcamento,
            gasto_real: expensesData?.custo_real || 0,
            saldo: (planoFase.orcamento?.previsto || 0) - (expensesData?.custo_real || 0),
          },
          financeiro: expensesData,
          estatisticas: {
            total_motoristas_meta: cidadesComDados.reduce((sum, c) => sum + c.part1.meta, 0),
            total_motoristas_real: cidadesComDados.reduce((sum, c) => sum + c.part1.realizado, 0),
            total_corridas_meta: cidadesComDados.reduce((sum, c) => sum + c.part2.meta, 0),
            total_corridas_real: cidadesComDados.reduce((sum, c) => sum + c.part2.realizado, 0),
          },
          alertas: gerarAlertas(cidadesComDados, planoFase, expensesData),
        };
        
        setConsolidatedData(consolidated);
      } catch (err) {
        console.error('Erro useMetasProgress:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (!expensesLoading) {
      fetchAllData();
    }
  }, [fase, planoFase, expensesData, expensesLoading]);
  
  return { data: consolidatedData, loading, error };
};

// Função auxiliar para gerar alertas
function gerarAlertas(cidades, plano, financeiro) {
  const alertas = [];
  
  // Alertas de progresso
  cidades.forEach(cidade => {
    if (cidade.part1.status === 'atrasado') {
      alertas.push({
        tipo: 'atrasado',
        nivel: 'warning',
        mensagem: `${cidade.nome}: Meta de motoristas atrasada (${cidade.part1.progresso.toFixed(1)}%)`,
        cidade: cidade.nome,
        parte: 'Part 1'
      });
    }
    
    if (cidade.part2.status === 'atrasado') {
      alertas.push({
        tipo: 'atrasado',
        nivel: 'warning',
        mensagem: `${cidade.nome}: Meta de corridas atrasada (${cidade.part2.progresso.toFixed(1)}%)`,
        cidade: cidade.nome,
        parte: 'Part 2'
      });
    }
  });
  
  // Alertas orçamentários
  const orcamentoPrevisto = plano.orcamento?.previsto || 0;
  const gastoReal = financeiro?.custo_real || 0;
  const percentualGasto = (gastoReal / orcamentoPrevisto) * 100;
  
  if (percentualGasto > 90) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'danger',
      mensagem: `Orçamento quase esgotado (${percentualGasto.toFixed(1)}% utilizado)`,
    });
  } else if (percentualGasto > 75) {
    alertas.push({
      tipo: 'orcamento',
      nivel: 'warning',
      mensagem: `Atenção ao orçamento (${percentualGasto.toFixed(1)}% utilizado)`,
    });
  }
  
  // Alertas de documentação
  if (financeiro?.documentos_pendentes > 0) {
    alertas.push({
      tipo: 'documentacao',
      nivel: 'info',
      mensagem: `${financeiro.documentos_pendentes} documentos pendentes de validação`,
    });
  }
  
  return alertas;
}
```

---

## 💰 FASE 3: SISTEMA DE DOCUMENTAÇÃO FINANCEIRA (4-6 horas)

### 3.1 Componente: ExpenseDocumentation.jsx

**Arquivo:** `frontend/src/components/MetasCidades/ExpenseDocumentation.jsx`

```javascript
import React, { useState } from 'react';
import { Upload, File, Check, X, Eye, Download } from 'lucide-react';

/**
 * Componente para gerenciar documentação de gastos
 * - Upload de comprovantes
 * - Vinculação com campanhas
 * - Categorização
 * - Workflow de aprovação
 */
const ExpenseDocumentation = ({ fase, cidade, campanha }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [expenses, setExpenses] = useState([]);
  
  const handleFileUpload = async (files) => {
    setUploading(true);
    
    try {
      // TODO: Implementar upload para Google Drive ou servidor
      // Por enquanto, simulação
      
      const newExpenses = Array.from(files).map((file, index) => ({
        id: Date.now() + index,
        nome: file.name,
        tamanho: file.size,
        tipo: file.type,
        data_upload: new Date().toISOString(),
        status: 'pendente',
        categoria: 'outros',
        valor: 0,
        fornecedor: '',
        campanha_vinculada: campanha?.id || null,
      }));
      
      setExpenses([...expenses, ...newExpenses]);
      setSelectedFiles([]);
    } catch (error) {
      console.error('Erro ao fazer upload:', error);
      alert('Erro ao fazer upload dos arquivos');
    } finally {
      setUploading(false);
    }
  };
  
  const categorias = [
    { value: 'facebook_ads', label: 'Anúncios Facebook' },
    { value: 'google_ads', label: 'Anúncios Google' },
    { value: 'hotel', label: 'Hospedagem' },
    { value: 'restaurante', label: 'Alimentação' },
    { value: 'combustivel', label: 'Combustível' },
    { value: 'transporte', label: 'Transporte' },
    { value: 'material', label: 'Material Gráfico' },
    { value: 'outros', label: 'Outros' },
  ];
  
  const statusColors = {
    pendente: 'bg-yellow-100 text-yellow-800',
    aprovado: 'bg-green-100 text-green-800',
    rejeitado: 'bg-red-100 text-red-800',
  };
  
  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h3 className="text-xl font-bold mb-4">Documentação de Gastos</h3>
      
      {/* Upload Area */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-6">
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-600 mb-2">
          Arraste arquivos ou clique para selecionar
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Formatos aceitos: PDF, JPG, PNG (máx. 10MB)
        </p>
        <input
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700"
        >
          Selecionar Arquivos
        </label>
      </div>
      
      {/* Lista de Documentos */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-700">Documentos Anexados</h4>
        
        {expenses.length === 0 ? (
          <p className="text-gray-500 text-sm italic">
            Nenhum documento anexado ainda
          </p>
        ) : (
          expenses.map((expense) => (
            <div 
              key={expense.id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center space-x-3 flex-1">
                <File className="h-8 w-8 text-blue-600" />
                
                <div className="flex-1">
                  <p className="font-medium">{expense.nome}</p>
                  <p className="text-sm text-gray-500">
                    {(expense.tamanho / 1024).toFixed(2)} KB • 
                    {new Date(expense.data_upload).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <select
                  value={expense.categoria}
                  onChange={(e) => {
                    const updated = expenses.map(exp =>
                      exp.id === expense.id
                        ? { ...exp, categoria: e.target.value }
                        : exp
                    );
                    setExpenses(updated);
                  }}
                  className="px-2 py-1 border rounded text-sm"
                >
                  {categorias.map(cat => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
                
                <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[expense.status]}`}>
                  {expense.status}
                </span>
                
                <button className="p-1 hover:bg-gray-200 rounded">
                  <Eye className="h-4 w-4 text-gray-600" />
                </button>
                
                <button className="p-1 hover:bg-gray-200 rounded">
                  <Download className="h-4 w-4 text-gray-600" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* Resumo */}
      {expenses.length > 0 && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">{expenses.length}</p>
              <p className="text-sm text-gray-600">Total Documentos</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-yellow-600">
                {expenses.filter(e => e.status === 'pendente').length}
              </p>
              <p className="text-sm text-gray-600">Pendentes</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">
                {expenses.filter(e => e.status === 'aprovado').length}
              </p>
              <p className="text-sm text-gray-600">Aprovados</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpenseDocumentation;
```

### 3.2 Componente: BudgetTracker.jsx

**Arquivo:** `frontend/src/components/MetasCidades/BudgetTracker.jsx`

```javascript
import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, AlertCircle } from 'lucide-react';

/**
 * Componente para rastrear orçamento e gastos
 * Visualiza: Previsto → Empenhado → Pago → Liquidado
 */
const BudgetTracker = ({ orcamento }) => {
  const {
    previsto = 0,
    empenhado = 0,
    pago = 0,
    liquidado = 0,
  } = orcamento || {};
  
  const disponivel = previsto - empenhado;
  const percentualUtilizado = previsto > 0 ? (empenhado / previsto) * 100 : 0;
  
  const stages = [
    { 
      label: 'Previsto', 
      value: previsto, 
      color: 'bg-blue-500',
      icon: DollarSign 
    },
    { 
      label: 'Empenhado', 
      value: empenhado, 
      color: 'bg-yellow-500',
      icon: AlertCircle 
    },
    { 
      label: 'Pago', 
      value: pago, 
      color: 'bg-orange-500',
      icon: TrendingDown 
    },
    { 
      label: 'Liquidado', 
      value: liquidado, 
      color: 'bg-green-500',
      icon: TrendingUp 
    },
  ];
  
  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h3 className="text-xl font-bold mb-6">Rastreamento Orçamentário</h3>
      
      {/* Barra de Progresso Geral */}
      <div className="mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Utilização do Orçamento
          </span>
          <span className="text-sm font-medium text-gray-700">
            {percentualUtilizado.toFixed(1)}%
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className={`h-4 rounded-full transition-all ${
              percentualUtilizado > 90 ? 'bg-red-500' :
              percentualUtilizado > 75 ? 'bg-yellow-500' :
              'bg-green-500'
            }`}
            style={{ width: `${Math.min(percentualUtilizado, 100)}%` }}
          />
        </div>
        
        <div className="flex justify-between mt-2 text-sm text-gray-600">
          <span>R$ 0</span>
          <span>R$ {previsto.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
        </div>
      </div>
      
      {/* Cards dos Estágios */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stages.map((stage, index) => (
          <div 
            key={stage.label}
            className="p-4 border rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <stage.icon className={`h-5 w-5 text-gray-600`} />
              <span className={`w-3 h-3 rounded-full ${stage.color}`}></span>
            </div>
            
            <p className="text-2xl font-bold text-gray-800">
              R$ {stage.value.toLocaleString('pt-BR', { 
                minimumFractionDigits: 2,
                maximumFractionDigits: 2 
              })}
            </p>
            
            <p className="text-sm text-gray-600 mt-1">{stage.label}</p>
            
            {index < stages.length - 1 && (
              <div className="mt-3 flex items-center text-xs text-gray-500">
                <span className="mr-1">→</span>
                <span>
                  {((stage.value / previsto) * 100).toFixed(0)}% do total
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Resumo */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Disponível</p>
            <p className={`text-xl font-bold ${
              disponivel < 0 ? 'text-red-600' : 'text-green-600'
            }`}>
              R$ {disponivel.toLocaleString('pt-BR', { 
                minimumFractionDigits: 2 
              })}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Em Execução</p>
            <p className="text-xl font-bold text-blue-600">
              R$ {(empenhado - liquidado).toLocaleString('pt-BR', { 
                minimumFractionDigits: 2 
              })}
            </p>
          </div>
        </div>
      </div>
      
      {/* Alertas */}
      {percentualUtilizado > 90 && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2 mt-0.5" />
            <div>
              <p className="font-semibold text-red-800">Atenção: Orçamento Crítico</p>
              <p className="text-sm text-red-700">
                Mais de 90% do orçamento já foi empenhado. Considere revisar gastos.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BudgetTracker;
```

---

## 📊 FASE 4: ATUALIZAÇÃO COMPONENTES EXISTENTES (2-3 horas)

### 4.1 Atualizar TabelaExecucao.jsx

**Modificações principais:**
- Integrar hook `useMetasProgress`
- Exibir dados reais vs meta
- Adicionar indicadores de progresso visuais
- Mostrar alertas de desvios

```javascript
// Adicionar no início do componente
import { useMetasProgress } from './hooks/useMetasProgress.js';

// Dentro do componente
const { data: progressData, loading, error } = useMetasProgress('Fase 1');

// Renderizar dados reais
{progressData?.cidades.map(cidade => (
  <tr key={cidade.nome}>
    <td>{cidade.nome}</td>
    <td>
      <div className="flex items-center">
        <span className="mr-2">{cidade.part1.realizado} / {cidade.part1.meta}</span>
        <div className="w-20 bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${
              cidade.part1.status === 'concluido' ? 'bg-green-500' :
              cidade.part1.status === 'no_prazo' ? 'bg-blue-500' :
              'bg-red-500'
            }`}
            style={{ width: `${Math.min(cidade.part1.progresso, 100)}%` }}
          />
        </div>
      </div>
    </td>
    {/* ... mais colunas */}
  </tr>
))}
```

### 4.2 Atualizar StatusFase.jsx

**Adicionar:**
- Badge de status (Planejada / Em Execução / Concluída)
- Progresso geral da fase
- Resumo financeiro

### 4.3 Atualizar FaseDetailsContent.jsx

**Adicionar:**
- Aba "Documentos" mostrando ExpenseDocumentation
- Aba "Financeiro" com BudgetTracker
- Aba "Alertas" com problemas identificados

---

## 🎨 FASE 5: DASHBOARD CONSOLIDADO (3-4 horas)

### 5.1 Componente: IntegratedDashboard.jsx

**Arquivo:** `frontend/src/components/MetasCidades/IntegratedDashboard.jsx`

Painel único integrando:
- Visão geral de todas as 3 fases
- Gráficos comparativos meta vs realizado
- Timeline de execução
- Status financeiro consolidado
- Alertas críticos

---

## 🔄 FASE 6: SINCRONIZAÇÃO E VALIDAÇÃO (2-3 horas)

### 6.1 Implementar Auto-Refresh

```javascript
// Hook com polling automático
useEffect(() => {
  const interval = setInterval(() => {
    refresh(); // Atualizar dados a cada 5 minutos
  }, 5 * 60 * 1000);
  
  return () => clearInterval(interval);
}, []);
```

### 6.2 Validação de Dados Cruzados

- Verificar consistência entre metas e dados reais
- Validar somas de orçamento
- Detectar anomalias (ex: gasto > orçamento)

### 6.3 Cache Inteligente

```javascript
// Usar React Query ou SWR para cache
import { useQuery } from '@tanstack/react-query';

const { data } = useQuery(
  ['drivers', cidade, period],
  () => fetchDrivers(cidade, period),
  {
    staleTime: 5 * 60 * 1000, // Cache por 5 minutos
    cacheTime: 30 * 60 * 1000, // Manter em cache por 30 minutos
  }
);
```

---

## ✅ FASE 7: TESTES E REFINAMENTO (2-3 horas)

### 7.1 Checklist de Validação

- [ ] Dados de motoristas são carregados corretamente
- [ ] Dados de corridas são filtrados por cidade
- [ ] Cálculos de progresso estão corretos
- [ ] Orçamento é rastreado corretamente (empenhado → pago → liquidado)
- [ ] Upload de documentos funciona
- [ ] Categorização de gastos funciona
- [ ] Alertas são gerados apropriadamente
- [ ] Performance é aceitável (< 3s para carregar)
- [ ] Responsividade funciona em mobile

### 7.2 Testes com Dados Reais

- Usar dados de Peixoto de Azevedo (primeira cidade)
- Validar com dados reais do backend
- Comparar cálculos manuais vs sistema

---

## 🚀 FASE 8: DEPLOY E MONITORAMENTO (1-2 horas)

### 8.1 Preparação para Deploy

```bash
# Build de produção
cd frontend
npm run build

# Testar build localmente
npm run preview
```

### 8.2 Configuração de Logs

```javascript
// Adicionar logging estruturado
console.log('[MetasProgress]', {
  fase,
  cidades: data?.cidades.length,
  orcamento: data?.orcamento,
  timestamp: new Date().toISOString()
});
```

### 8.3 Monitoramento

- Configurar alertas para erros de API
- Monitorar tempo de carregamento
- Rastrear uso de features

---

## 📈 MÉTRICAS DE SUCESSO

### KPIs do Projeto

1. **Integração de Dados**
   - ✅ 100% dos endpoints identificados consumidos
   - ✅ Dados sincronizados em tempo real (< 5 min)
   - ✅ Zero erros de consistência

2. **Documentação Financeira**
   - ✅ Sistema de upload funcional
   - ✅ 100% dos gastos categorizados
   - ✅ Workflow de aprovação implementado

3. **UX/Performance**
   - ✅ Tempo de carregamento < 3s
   - ✅ Interface responsiva (mobile/desktop)
   - ✅ Feedback visual em todas ações

4. **Confiabilidade**
   - ✅ Taxa de erro < 1%
   - ✅ Tratamento de edge cases
   - ✅ Fallbacks para dados indisponíveis

---

## 📚 DOCUMENTAÇÃO TÉCNICA

### Arquivos a Criar/Modificar

**NOVOS (10 arquivos):**
1. `useDriversByCidade.js` - Hook motoristas
2. `useRidesByCidade.js` - Hook corridas
3. `useCampaignExpenses.js` - Hook gastos
4. `useMetasProgress.js` - Hook master
5. `useFinancialDocuments.js` - Hook documentos
6. `ExpenseDocumentation.jsx` - Componente upload
7. `BudgetTracker.jsx` - Componente orçamento
8. `ProgressIndicator.jsx` - Indicador progresso
9. `AlertsPanel.jsx` - Painel alertas
10. `IntegratedDashboard.jsx` - Dashboard consolidado

**MODIFICADOS (3 arquivos):**
1. `TabelaExecucao.jsx` - Integrar dados reais
2. `StatusFase.jsx` - Adicionar progresso
3. `FaseDetailsContent.jsx` - Adicionar abas

---

## ⏱️ CRONOGRAMA SUGERIDO

**Semana 1 (12 horas):**
- Dia 1-2: Fases 1 e 2 (Análise + Hooks)
- Dia 3-4: Fase 3 (Sistema Financeiro)

**Semana 2 (10 horas):**
- Dia 1-2: Fase 4 (Atualização Componentes)
- Dia 3: Fase 5 (Dashboard)

**Semana 3 (5 horas):**
- Dia 1: Fase 6 (Sincronização)
- Dia 2: Fases 7 e 8 (Testes + Deploy)

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

### Para Começar AGORA:

1. **Validar Proposta** ✋
   - Revisar este plano
   - Aprovar abordagem
   - Priorizar features (se necessário)

2. **Configurar Ambiente** 
   - Garantir backend rodando
   - Validar endpoints disponíveis
   - Testar conexão APIs

3. **Iniciar Desenvolvimento**
   - Começar pela Fase 2 (Hooks)
   - Criar primeiro hook (useDriversByCidade)
   - Testar integração

---

## ❓ PERGUNTAS PARA DECISÃO

Antes de começar, preciso que você decida:

1. **Prioridade de Implementação:**
   - [ ] Opção A: Fazer TUDO (plano completo 18-27h)
   - [ ] Opção B: MVP Mínimo (só Fase 2 + 4: ~5-7h)
   - [ ] Opção C: Personalizado (você escolhe fases)

2. **Upload de Documentos:**
   - [ ] Google Drive API (mais complexo, melhor UX)
   - [ ] Upload servidor local (mais simples, rápido)
   - [ ] Apenas URLs manuais (sem upload)

3. **Frequência de Atualização:**
   - [ ] Tempo real (websockets)
   - [ ] Polling 5 minutos (recomendado)
   - [ ] Manual (botão refresh)

4. **Prioridade Visual:**
   - [ ] Funcionalidade primeiro, design depois
   - [ ] Design + funcionalidade balanceado
   - [ ] Design impecável desde o início

---

**Aguardo suas decisões para iniciar o desenvolvimento! 🚀**
