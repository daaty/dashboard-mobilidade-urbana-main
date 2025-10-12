# 🔧 PLANO DE REFATORAÇÃO: Sistema de Metas por Cidades

**Data:** 10 de outubro de 2025  
**Objetivo:** Melhorar código EXISTENTE sem adicionar novas funcionalidades  
**Foco:** Refatorar código bagunçado, manter funcionalidade intacta

---

## 📊 ANÁLISE DO CÓDIGO ATUAL

### **Arquivo 1: MetasCidades.jsx**
**Status:** 🔴 **CRÍTICO - 3,529 LINHAS!**

#### **Problemas Identificados:**

1. **📏 Tamanho Excessivo**
   - 3,529 linhas em um único arquivo
   - Múltiplos componentes misturados
   - Impossível de manter

2. **🧩 Componentes Internos (dentro do mesmo arquivo):**
   ```
   - EditFaseForm (38 linhas)
   - buildPlanoDinamico (função, ~95 linhas)
   - getFasePeriodo (função helper)
   - getFaseStatus (função helper)
   - getPartPeriodo (função helper)
   - getPartStatus (função helper)
   - StatusFase (componente, ~166 linhas)
   - FormularioCadastroMetas (componente, ~496 linhas!)
   - TabelaExecucao (componente, ~186 linhas)
   - TabelaExecucaoComCruzamento (componente, ~131 linhas)
   - FaseDetailsContent (componente)
   - MetasCidades (componente principal)
   ```

3. **🔀 Responsabilidades Misturadas:**
   - Gerenciamento de fases
   - CRUD de metas
   - Visualização de execução
   - Cruzamento de dados
   - Formulários de edição

4. **📦 Imports Duplicados:**
   - 33 ícones do Lucide React
   - Muitos não são usados

5. **🎨 Lógica de Negócio Espalhada:**
   - Funções helper no meio do arquivo
   - Estados globais misturados
   - Callbacks complexos

---

### **Arquivo 2: TabelaMetasCidades.jsx**
**Status:** 🟡 **MODERADO - 354 LINHAS**

#### **Problemas Identificados:**

1. **🔗 Dependências Hardcoded:**
   ```javascript
   const cidadeIds = {
     'Peixoto de Azevedo': 1,
     'Nova Monte Verde': 2,
     'Matupá': 3,
     'Guarantã do Norte': 4,
     'Nova Bandeirantes': 5
   };
   ```
   ❌ IDs hardcoded - deve vir da API ou constantes

2. **🔄 Lógica Duplicada:**
   - Cálculo de percentuais repetido
   - Processamento de dados similar ao MetasCidades.jsx
   - Funções de ordenação/filtro básicas

3. **⚠️ Fallback para Estimativas:**
   ```javascript
   if (!dadosReal) {
     // Gera dados fake como fallback
     dadosReal = {
       meta_corridas: meta_mes,
       resultado_corridas: 0,
       // ...
     };
   }
   ```
   ❌ Ainda usa estimativas quando deveria retornar vazio

4. **📊 Múltiplas Responsabilidades:**
   - Carrega dados da API
   - Processa dados
   - Renderiza tabela
   - Gerencia filtros

---

## 🎯 ESTRATÉGIA DE REFATORAÇÃO

### **Princípios:**
1. ✅ **Não quebrar funcionalidades existentes**
2. ✅ **Dividir em componentes menores (max 200 linhas cada)**
3. ✅ **Separar lógica de apresentação**
4. ✅ **Criar hooks customizados para lógica reutilizável**
5. ✅ **Mover constantes para arquivos separados**
6. ✅ **Eliminar código duplicado**

---

## 📋 PLANO DE EXECUÇÃO (3 Fases)

### **FASE 1: Extração de Constantes e Utilitários (1 dia)**

#### **1.1 Criar arquivo de constantes**
**Arquivo:** `frontend/src/constants/cidadesConstants.js`

```javascript
export const CIDADES_IDS = {
  'Peixoto de Azevedo': 1,
  'Nova Monte Verde': 2,
  'Matupá': 3,
  'Guarantã do Norte': 4,
  'Nova Bandeirantes': 5
};

export const CIDADES_SIGLAS = {
  1: 'PXT',
  2: 'NMV',
  3: 'MTP',
  4: 'GTN',
  5: 'NBD'
};

export const CIDADES_NOMES = {
  1: 'Peixoto de Azevedo',
  2: 'Nova Monte Verde',
  3: 'Matupá',
  4: 'Guarantã do Norte',
  5: 'Nova Bandeirantes'
};

export const FASES_CONFIG = {
  'Fase 1': {
    periodo: '01/ago a 14/set',
    status: 'em_execucao',
    part1: { duracao: 15, tipo: 'motoristas' },
    part2: { duracao: 30, tipo: 'corridas' }
  },
  'Fase 2': {
    periodo: '15/set a 30/out',
    status: 'planejada',
    part1: { duracao: 15, tipo: 'motoristas' },
    part2: { duracao: 30, tipo: 'corridas' }
  },
  'Fase 3': {
    periodo: '01/nov a 14/dez',
    status: 'planejada',
    part1: { duracao: 15, tipo: 'motoristas' },
    part2: { duracao: 30, tipo: 'corridas' }
  }
};

export const STATUS_CORES = {
  'acima': 'text-green-600 bg-green-50',
  'meta': 'text-blue-600 bg-blue-50',
  'atencao': 'text-yellow-600 bg-yellow-50',
  'abaixo': 'text-red-600 bg-red-50'
};
```

#### **1.2 Criar arquivo de utilitários**
**Arquivo:** `frontend/src/utils/metasUtils.js`

```javascript
import { FASES_CONFIG } from '../constants/cidadesConstants';

export const calcularPercentual = (realizado, meta) => {
  if (!meta || meta === 0) return 0;
  return (realizado / meta) * 100;
};

export const formatarMoeda = (valor) => {
  return valor.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2
  });
};

export const formatarNumero = (valor) => {
  return valor.toLocaleString('pt-BR');
};

export const obterStatusPerformance = (percentual) => {
  if (percentual >= 100) return 'acima';
  if (percentual >= 90) return 'meta';
  if (percentual >= 70) return 'atencao';
  return 'abaixo';
};

export const getFasePeriodo = (fase) => {
  return FASES_CONFIG[fase]?.periodo || 'Não definido';
};

export const getFaseStatus = (fase) => {
  return FASES_CONFIG[fase]?.status || 'planejada';
};

export const getPartPeriodo = (fase, part) => {
  const config = FASES_CONFIG[fase];
  if (!config) return 'Não definido';
  
  const partConfig = part === 1 ? config.part1 : config.part2;
  return `${partConfig.duracao} dias`;
};

export const getPartStatus = (fase, part) => {
  const faseStatus = getFaseStatus(fase);
  if (faseStatus === 'concluida') return 'concluida';
  if (faseStatus === 'em_execucao' && part === 1) return 'em_execucao';
  if (faseStatus === 'em_execucao' && part === 2) return 'planejada';
  return 'planejada';
};
```

---

### **FASE 2: Extração de Componentes (2 dias)**

#### **2.1 Quebrar MetasCidades.jsx em componentes menores**

**Estrutura Nova:**
```
frontend/src/components/MetasCidades/
├── index.jsx (componente principal, max 150 linhas)
├── EditFaseForm.jsx (formulário de edição, ~80 linhas)
├── StatusFase.jsx (card de status de fase, ~150 linhas)
├── FormularioCadastroMetas.jsx (formulário cadastro, ~400 linhas)
├── TabelaExecucao.jsx (tabela execução, ~180 linhas)
├── TabelaExecucaoComCruzamento.jsx (tabela cruzamento, ~130 linhas)
├── FaseDetailsContent.jsx (detalhes da fase, ~150 linhas)
└── hooks/
    ├── usePlanoDinamico.js (lógica de plano dinâmico)
    ├── useMetasCidades.js (fetch de metas)
    └── useCampanhas.js (fetch de campanhas)
```

**Exemplo - Componente Principal Refatorado:**

```jsx
// frontend/src/components/MetasCidades/index.jsx
import React, { useState } from 'react';
import { usePlanoDinamico } from './hooks/usePlanoDinamico';
import { useMetasCidades } from './hooks/useMetasCidades';
import { useCampanhas } from './hooks/useCampanhas';
import StatusFase from './StatusFase';
import TabelaExecucao from './TabelaExecucao';
import FormularioCadastroMetas from './FormularioCadastroMetas';
import CidadesManager from '../CidadesManager';
import GerenciadorMetasEstrategicas from '../GerenciadorMetasEstrategicas';

const MetasCidades = () => {
  // Custom hooks para lógica de negócio
  const { campanhas, loading: loadingCampanhas } = useCampanhas();
  const { metas, loading: loadingMetas } = useMetasCidades();
  const { planoExecucao } = usePlanoDinamico(campanhas);

  // Estados locais apenas para UI
  const [activeTab, setActiveTab] = useState('visao-geral');
  const [showFormulario, setShowFormulario] = useState(false);
  const [faseDetalhes, setFaseDetalhes] = useState(null);

  if (loadingCampanhas || loadingMetas) {
    return <LoadingSpinner />;
  }

  return (
    <div className="p-6">
      {/* Navegação de abas */}
      <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Conteúdo dinâmico por aba */}
      {activeTab === 'visao-geral' && (
        <VisaoGeralTab 
          planoExecucao={planoExecucao}
          metas={metas}
          onVerDetalhes={setFaseDetalhes}
        />
      )}

      {activeTab === 'execucao' && (
        <TabelaExecucao campanhas={campanhas} />
      )}

      {activeTab === 'cidades' && (
        <CidadesManager />
      )}

      {activeTab === 'gerenciador' && (
        <GerenciadorMetasEstrategicas />
      )}

      {/* Modais */}
      {showFormulario && (
        <FormularioCadastroMetas 
          isOpen={showFormulario}
          onClose={() => setShowFormulario(false)}
        />
      )}
    </div>
  );
};

export default MetasCidades;
```

#### **2.2 Criar hooks customizados**

**Arquivo:** `frontend/src/components/MetasCidades/hooks/usePlanoDinamico.js`

```javascript
import { useState, useEffect } from 'react';
import { FASES_CONFIG } from '../../../constants/cidadesConstants';

export const usePlanoDinamico = (campanhas) => {
  const [planoExecucao, setPlanoExecucao] = useState({});

  useEffect(() => {
    if (!campanhas || campanhas.length === 0) {
      setPlanoExecucao({});
      return;
    }

    const fasesPlanejamento = {};
    const cidadesComDadosReais = ['PEIXOTO', 'MATUPA', 'GUARANTA DO NORTE'];

    // Agrupar campanhas por fase
    campanhas.forEach(campanha => {
      const fase = campanha.fase || 'Fase 1';
      
      if (!fasesPlanejamento[fase]) {
        fasesPlanejamento[fase] = {
          periodo: FASES_CONFIG[fase]?.periodo || '',
          status: FASES_CONFIG[fase]?.status || 'planejada',
          cidades: new Set(),
          part1: { 
            periodo: FASES_CONFIG[fase]?.part1.duracao + ' dias',
            metas: {}, 
            tipo: "motoristas", 
            status: 'planejada'
          },
          part2: { 
            periodo: FASES_CONFIG[fase]?.part2.duracao + ' dias',
            metas: {}, 
            tipo: "corridas", 
            status: 'planejada'
          }
        };
      }

      // Adicionar cidade à fase
      const nomeCidade = campanha.cidade?.nome || 'Desconhecida';
      fasesPlanejamento[fase].cidades.add(nomeCidade);

      // Adicionar metas por parte
      if (campanha.parte_campanha === 'Part 1') {
        fasesPlanejamento[fase].part1.metas[nomeCidade] = {
          motoristas: campanha.meta_motoristas || 0,
          orcamento: campanha.orcamento_previsto || 0
        };
      } else if (campanha.parte_campanha === 'Part 2') {
        fasesPlanejamento[fase].part2.metas[nomeCidade] = {
          corridas: campanha.meta_corridas || 0,
          receita: campanha.meta_receita || 0
        };
      }
    });

    // Converter Set para Array
    Object.keys(fasesPlanejamento).forEach(fase => {
      fasesPlanejamento[fase].cidades = Array.from(fasesPlanejamento[fase].cidades);
    });

    setPlanoExecucao(fasesPlanejamento);
  }, [campanhas]);

  return { planoExecucao };
};
```

**Arquivo:** `frontend/src/components/MetasCidades/hooks/useMetasCidades.js`

```javascript
import { useState, useEffect } from 'react';
import { CIDADES_IDS } from '../../../constants/cidadesConstants';

export const useMetasCidades = () => {
  const [metas, setMetas] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const carregarMetas = async () => {
      setLoading(true);
      const metasMap = {};

      try {
        // Buscar metas para cada cidade
        const promessas = Object.entries(CIDADES_IDS).map(async ([nomeCidade, cidadeId]) => {
          const response = await fetch(
            `http://localhost:8000/api/metas-estrategicas/consolidado/${cidadeId}`
          );
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              metasMap[nomeCidade] = data.metas;
            }
          }
        });

        await Promise.all(promessas);
        setMetas(metasMap);
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar metas:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    carregarMetas();
  }, []);

  const recarregarMetas = () => {
    setLoading(true);
    // Re-executa o useEffect
  };

  return { metas, loading, error, recarregarMetas };
};
```

---

### **FASE 3: Refatoração de TabelaMetasCidades.jsx (1 dia)**

#### **3.1 Eliminar código duplicado**

**Antes (TabelaMetasCidades.jsx):**
```javascript
// ❌ IDs hardcoded
const cidadeIds = {
  'Peixoto de Azevedo': 1,
  'Nova Monte Verde': 2,
  'Matupá': 3,
  'Guarantã do Norte': 4,
  'Nova Bandeirantes': 5
};

// ❌ Lógica de cálculo duplicada
const percentual = dadosReal.progresso_corridas;
const projecao_ano = Math.round(dadosReal.meta_corridas * (12 / dadosReal.periodo_meses));
```

**Depois:**
```javascript
// ✅ Importar constantes
import { CIDADES_IDS } from '../../constants/cidadesConstants';
import { calcularPercentual, formatarMoeda } from '../../utils/metasUtils';

// ✅ Usar funções utilitárias
const percentual = calcularPercentual(resultados.corridas, metas.corridas);
const projecao_ano = Math.round(metas.corridas * (12 / periodo_meses));
```

#### **3.2 Usar hook customizado**

```javascript
// ✅ Usar hook em vez de useEffect complexo
import { useMetasCidades } from '../MetasCidades/hooks/useMetasCidades';

const TabelaMetasCidades = ({ cidadesData, campanhasData }) => {
  const { metas, loading } = useMetasCidades();
  
  // Resto da lógica de apresentação apenas
  // ...
};
```

#### **3.3 Separar lógica de processamento**

**Criar:** `frontend/src/utils/processCidadesData.js`

```javascript
import { calcularPercentual, obterStatusPerformance } from './metasUtils';

export const processarDadosCidades = (cidadesData, campanhasData, metasReais) => {
  if (!cidadesData || !campanhasData) return [];

  return cidadesData.map(cidade => {
    // Filtrar campanhas desta cidade
    const campanhasCidade = campanhasData.filter(c => c.cidade.id === cidade.id);
    
    // Calcular métricas básicas
    const populacao = cidade.populacao_estimada_2024 || cidade.populacao_censo_2022 || 0;
    const publico_alvo = Math.round(populacao * 0.45);
    
    // Determinar fase atual
    const fases = campanhasCidade.map(c => c.fase);
    const fase_atual = fases.includes('Fase 3') ? 'Fase 3' : 
                      fases.includes('Fase 2') ? 'Fase 2' : 
                      fases.includes('Fase 1') ? 'Fase 1' : 'Planejamento';

    // Buscar dados reais da API
    const metasCidade = metasReais[cidade.cidade];
    let dadosReal = null;
    
    if (metasCidade && metasCidade.length > 0) {
      const metaPrincipal = metasCidade[0];
      
      dadosReal = {
        periodo_meses: metaPrincipal.periodo_meses,
        meta_corridas: metaPrincipal.metas.corridas,
        resultado_corridas: metaPrincipal.resultados.corridas,
        meta_motoristas: metaPrincipal.metas.motoristas,
        resultado_motoristas: metaPrincipal.resultados.motoristas,
        meta_receita: metaPrincipal.metas.receita,
        resultado_receita: metaPrincipal.resultados.receita,
        usuarios_ativos: metaPrincipal.resultados.usuarios_ativos,
        satisfacao: metaPrincipal.resultados.satisfacao,
        taxa_cancelamento: metaPrincipal.resultados.taxa_cancelamento,
        progresso_corridas: metaPrincipal.progresso.corridas,
        progresso_receita: metaPrincipal.progresso.receita,
        progresso_motoristas: metaPrincipal.progresso.motoristas
      };
    }

    // ❌ REMOVER FALLBACK - Se não tem dados, retornar vazio
    if (!dadosReal) {
      return null; // Será filtrado depois
    }

    const percentual = dadosReal.progresso_corridas;
    const projecao_ano = Math.round(dadosReal.meta_corridas * (12 / dadosReal.periodo_meses));

    return {
      cidade: cidade.cidade,
      populacao: populacao.toLocaleString(),
      publico_alvo: publico_alvo.toLocaleString(),
      fase_atual,
      mes_campanha: `${dadosReal.periodo_meses}º Mês`,
      meta_mes: `${dadosReal.meta_corridas.toLocaleString()} corridas`,
      realizado: `${dadosReal.resultado_corridas.toLocaleString()} corridas`,
      percentual: `${percentual.toFixed(1)}%`,
      projecao_ano: `${projecao_ano.toLocaleString()} corridas`,
      receita_estimada: formatarMoeda(dadosReal.resultado_receita),
      satisfacao: dadosReal.satisfacao,
      taxa_cancelamento: dadosReal.taxa_cancelamento,
      usuarios_ativos: dadosReal.usuarios_ativos,
      campanhas_ativas: campanhasCidade.filter(c => c.status === 'ativa').length,
      orcamento_total: campanhasCidade.reduce((sum, c) => sum + c.orcamento_previsto, 0),
      status_performance: obterStatusPerformance(percentual),
      populacao_num: populacao,
      percentual_num: percentual
    };
  }).filter(Boolean); // Remove nulls (cidades sem dados)
};
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### **Fase 1: Constantes e Utilitários**
- [ ] Arquivo `cidadesConstants.js` criado
- [ ] Arquivo `metasUtils.js` criado
- [ ] Testes unitários para funções utilitárias
- [ ] Todos os imports atualizados

### **Fase 2: Componentes**
- [ ] Pasta `MetasCidades/` criada
- [ ] `EditFaseForm.jsx` extraído (< 100 linhas)
- [ ] `StatusFase.jsx` extraído (< 200 linhas)
- [ ] `FormularioCadastroMetas.jsx` extraído (< 450 linhas)
- [ ] `TabelaExecucao.jsx` extraído (< 200 linhas)
- [ ] `TabelaExecucaoComCruzamento.jsx` extraído (< 150 linhas)
- [ ] `FaseDetailsContent.jsx` extraído (< 200 linhas)
- [ ] `usePlanoDinamico.js` hook criado
- [ ] `useMetasCidades.js` hook criado
- [ ] `useCampanhas.js` hook criado
- [ ] Componente principal `index.jsx` (< 200 linhas)

### **Fase 3: TabelaMetasCidades**
- [ ] IDs hardcoded removidos
- [ ] Usa `CIDADES_IDS` de constantes
- [ ] Usa `useMetasCidades` hook
- [ ] Lógica de processamento em `processCidadesData.js`
- [ ] Fallback de estimativas REMOVIDO
- [ ] Código duplicado eliminado

### **Validação Funcional**
- [ ] Todos os componentes renderizam corretamente
- [ ] APIs continuam sendo chamadas
- [ ] Dados reais são exibidos
- [ ] Filtros funcionam
- [ ] Ordenação funciona
- [ ] Formulários funcionam
- [ ] Navegação entre abas funciona
- [ ] Modais abrem/fecham

---

## 📊 MÉTRICAS DE SUCESSO

| Métrica | Antes | Meta Depois | Benefício |
|---------|-------|-------------|-----------|
| **Linhas MetasCidades.jsx** | 3,529 | < 200 | ✅ 94% redução |
| **Número de arquivos** | 2 | ~15 | ✅ Organização |
| **Componentes > 200 linhas** | 1 | 0 | ✅ Manutenibilidade |
| **Código duplicado** | Alto | Baixo | ✅ DRY |
| **Imports não usados** | ~15 | 0 | ✅ Clean |
| **Constantes hardcoded** | ~30 | 0 | ✅ Centralizado |

---

## 🚀 ORDEM DE EXECUÇÃO RECOMENDADA

### **Dia 1: Constantes e Utilitários**
1. Criar `cidadesConstants.js`
2. Criar `metasUtils.js`
3. Criar `processCidadesData.js`
4. Executar testes

### **Dia 2: Hooks e Componentes Pequenos**
1. Criar pasta `MetasCidades/hooks/`
2. Extrair `usePlanoDinamico.js`
3. Extrair `useMetasCidades.js`
4. Extrair `useCampanhas.js`
5. Extrair `EditFaseForm.jsx`
6. Extrair `StatusFase.jsx`

### **Dia 3: Componentes Grandes**
1. Extrair `FormularioCadastroMetas.jsx`
2. Extrair `TabelaExecucao.jsx`
3. Extrair `TabelaExecucaoComCruzamento.jsx`
4. Extrair `FaseDetailsContent.jsx`

### **Dia 4: Refatorar Componente Principal**
1. Refatorar `MetasCidades/index.jsx`
2. Atualizar todos os imports
3. Testar navegação entre abas
4. Validar funcionalidades

### **Dia 5: Refatorar TabelaMetasCidades**
1. Usar constantes importadas
2. Usar hook `useMetasCidades`
3. Usar `processCidadesData`
4. Remover fallbacks
5. Testes finais

---

## ⚠️ RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Quebrar funcionalidade | Média | Alto | ✅ Testes em cada etapa |
| Imports quebrados | Alta | Médio | ✅ Atualizar imports incrementalmente |
| Perda de contexto | Baixa | Alto | ✅ Commits pequenos e frequentes |
| Performance degradada | Baixa | Médio | ✅ Profiler antes/depois |

---

## 🎯 RESULTADO ESPERADO

**Antes:**
```
frontend/src/components/
├── MetasCidades.jsx (3,529 linhas 🔴)
├── TabelaMetasCidades.jsx (354 linhas 🟡)
└── CidadesManager.jsx
```

**Depois:**
```
frontend/src/
├── constants/
│   └── cidadesConstants.js (150 linhas)
├── utils/
│   ├── metasUtils.js (100 linhas)
│   └── processCidadesData.js (80 linhas)
├── components/
│   ├── MetasCidades/
│   │   ├── index.jsx (180 linhas ✅)
│   │   ├── EditFaseForm.jsx (80 linhas ✅)
│   │   ├── StatusFase.jsx (150 linhas ✅)
│   │   ├── FormularioCadastroMetas.jsx (400 linhas ✅)
│   │   ├── TabelaExecucao.jsx (180 linhas ✅)
│   │   ├── TabelaExecucaoComCruzamento.jsx (130 linhas ✅)
│   │   ├── FaseDetailsContent.jsx (150 linhas ✅)
│   │   └── hooks/
│   │       ├── usePlanoDinamico.js (100 linhas ✅)
│   │       ├── useMetasCidades.js (60 linhas ✅)
│   │       └── useCampanhas.js (50 linhas ✅)
│   ├── TabelaMetasCidades.jsx (200 linhas ✅)
│   └── CidadesManager.jsx
```

**Total de Linhas:** ~2,010 linhas (vs 3,883 antes) = **48% de redução**  
**Arquivos:** 15 arquivos bem organizados  
**Manutenibilidade:** ✅ Excelente

---

## 📝 PRÓXIMOS PASSOS

1. **Aprovação:** Validar este plano com o time
2. **Backup:** Criar branch de backup (`backup/metas-cidades-pre-refactor`)
3. **Execução:** Seguir ordem de dias 1-5
4. **Validação:** Testes manuais + automatizados
5. **Deploy:** Staging → Produção

---

**Documento Criado:** 10/10/2025  
**Autor:** GitHub Copilot  
**Foco:** Refatoração sem adicionar features  
**Prazo:** 5 dias úteis  
**Prioridade:** 🔴 ALTA (código crítico com 3,5k linhas)
