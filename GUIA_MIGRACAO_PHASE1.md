# 📋 GUIA DE MIGRAÇÃO - Phase 1 Refactoring

**Data:** $(Get-Date)  
**Fase:** 1 de 3 - Extração de Constants e Utils  
**Status:** ✅ Arquivos criados, 🔄 Integração pendente

---

## 📦 Arquivos Criados (Phase 1)

### 1️⃣ `frontend/src/constants/cidadesConstants.js` (300 linhas)
**Propósito:** Centralizar todos os valores hardcoded

**Exports principais:**
- `CIDADES_IDS` - Mapa nome → ID
- `CIDADES_NOMES` - Mapa ID → nome
- `CIDADES_SIGLAS` - Mapa ID → sigla
- `FASES_CONFIG` - Configuração de cada fase
- `STATUS_CORES` - Cores Tailwind para cada status
- `STATUS_FASE_CORES` - Cores para status de fases
- `PERFORMANCE_THRESHOLDS` - Limites de performance (100%, 90%, 70%)
- `API_ENDPOINTS` - URLs da API centralizadas

**Funções helper:**
- `normalizarNomeCidade(nome)` - Normaliza nome para padrão
- `obterCidadeId(nome)` - Retorna ID da cidade
- `obterCidadeNome(id)` - Retorna nome da cidade
- `isCidadeValida(nome)` - Valida se cidade existe
- `listarTodasCidades()` - Lista todas as cidades

### 2️⃣ `frontend/src/utils/metasUtils.js` (500 linhas)
**Propósito:** Funções utilitárias reutilizáveis

**Categorias de funções:**

**Formatação:**
- `formatarMoeda(valor, showPrefix)` - R$ 1.234,56
- `formatarNumero(valor, decimais)` - 1.234,56
- `formatarPercentual(valor, decimais)` - 85,5%
- `formatarData(data)` - 01/08/2025
- `formatarPeriodo(inicio, fim)` - 01/ago a 14/set

**Cálculos:**
- `calcularPercentual(realizado, meta)` - % de realização
- `calcularDiferenca(realizado, meta)` - Diferença absoluta
- `calcularProjecao(realizado, diasDecorridos, diasTotais)` - Projeção
- `calcularMedia(valores)` - Média de array
- `calcularTaxaCrescimento(atual, anterior)` - % de crescimento

**Status:**
- `obterStatusPerformance(percentual)` - 'acima', 'meta', 'atencao', 'abaixo'
- `obterIconeStatus(status)` - Emoji correspondente
- `obterLabelStatus(status)` - Label amigável

**Fases:**
- `getFasePeriodo(fase)` - Período da fase
- `getFaseStatus(fase)` - Status atual da fase
- `getPartPeriodo(fase, part)` - Período de uma parte
- `getPartStatus(fase, part)` - Status de uma parte

**Validações:**
- `isNumeroValido(valor)` - Valida número
- `isPercentualValido(percentual)` - Valida percentual
- `isDataValida(data)` - Valida data

**Manipulação:**
- `removerAcentos(str)` - Remove acentos
- `normalizarNomeCidade(nome)` - Normaliza nome
- `agruparPor(array, key)` - Agrupa array por chave
- `ordenarPor(array, campo, ordem)` - Ordena array
- `removerNulos(obj)` - Remove valores null/undefined

**Comparação:**
- `compararValores(a, b, tolerancia)` - Compara com tolerância
- `calcularTendencia(valores)` - 'crescente', 'decrescente', 'estavel'

### 3️⃣ `frontend/src/utils/processCidadesData.js` (600 linhas)
**Propósito:** Lógica de processamento de dados de cidades

**Função principal:**
```javascript
processarDadosCidades(cidadesData, campanhasData, metasReais)
// Retorna array de objetos processados para exibição
```

**Funções auxiliares:**
- `filtrarPorFase(cidades, fase)` - Filtra por fase
- `filtrarPorStatus(cidades, status)` - Filtra por performance
- `ordenarCidades(cidades, ordenacao)` - Ordena cidades
- `buscarCidades(cidades, termo)` - Busca por nome
- `calcularTotais(cidades)` - Agregações totais

**Objeto retornado por cidade:**
```javascript
{
  // Identificação
  cidade: "Matupá",
  cidade_id: 3,
  
  // População
  populacao: "14.929",
  populacao_num: 14929,
  publico_alvo: "6.718",
  publico_alvo_num: 6718,
  
  // Fase
  fase_atual: "Fase 1",
  mes_campanha: "1º Mês",
  periodo_meses: 1,
  
  // Metas
  meta_mes: "34 corridas",
  meta_mes_num: 34,
  realizado: "0 corridas",
  realizado_num: 0,
  
  // Performance
  percentual: "0.0%",
  percentual_num: 0,
  status_performance: "abaixo",
  
  // Receita
  receita_estimada: "R$ 0,00",
  
  // Campanhas
  campanhas_ativas: 0,
  orcamento_total: 0,
  
  // Metadados
  tem_dados_reais: false,
  _raw: { ... } // Dados brutos
}
```

---

## 🔄 MIGRAÇÕES NECESSÁRIAS

### ✅ TabelaMetasCidades.jsx

**1. Adicionar imports:**
```javascript
import { CIDADES_IDS } from '../constants/cidadesConstants';
import { processarDadosCidades, ordenarCidades } from '../utils/processCidadesData';
```

**2. Remover código:**
- ❌ Linhas 8-14: Objeto `cidadeIds` hardcoded
- ❌ Linhas 66-155: Função `processarDadosCidades()` completa
- ❌ Linhas 130-151: Lógica de cálculo de percentual duplicada

**3. Substituir:**
```javascript
// ANTES
const cidadeIds = {
  'Peixoto de Azevedo': 1,
  'Nova Monte Verde': 2,
  ...
};

const processarDadosCidades = () => {
  // 90 linhas de lógica...
};

// DEPOIS
import { CIDADES_IDS } from '../constants/cidadesConstants';
import { processarDadosCidades } from '../utils/processCidadesData';

// Usar diretamente
const dados = processarDadosCidades(cidadesData, campanhasData, metasReais);
```

**4. Atualizar ordenação:**
```javascript
// ANTES
const dadosOrdenados = [...dadosFiltrados].sort((a, b) => {
  if (ordenacao === 'alfabetica') return a.cidade.localeCompare(b.cidade);
  if (ordenacao === 'populacao') return b.populacao_num - a.populacao_num;
  if (ordenacao === 'performance') return b.percentual_num - a.percentual_num;
  return 0;
});

// DEPOIS
const dadosOrdenados = ordenarCidades(dadosFiltrados, ordenacao);
```

**Economia:** ~100 linhas removidas, código mais limpo

---

### ✅ MetasCidades.jsx

**1. Adicionar imports:**
```javascript
import { 
  FASES_CONFIG, 
  STATUS_CORES, 
  STATUS_FASE_CORES 
} from '../constants/cidadesConstants';

import {
  getFasePeriodo,
  getFaseStatus,
  getPartPeriodo,
  getPartStatus,
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
  obterStatusPerformance
} from '../utils/metasUtils';
```

**2. Remover código:**
- ❌ Linhas 273-282: `getFasePeriodo()` - mover para utils ✅
- ❌ Linhas 282-298: `getFaseStatus()` - mover para utils ✅
- ❌ Linhas 299-311: `getPartPeriodo()` - mover para utils ✅
- ❌ Linhas 312-325: `getPartStatus()` - mover para utils ✅
- ❌ Todas referências a cores hardcoded (ex: `'bg-green-500'`)

**3. Substituir chamadas:**
```javascript
// ANTES
const periodo = getFasePeriodo(fase); // função local

// DEPOIS
import { getFasePeriodo } from '../utils/metasUtils';
const periodo = getFasePeriodo(fase); // função importada
```

**4. Substituir cores hardcoded:**
```javascript
// ANTES (linha ~335)
const getStatusColor = (status) => {
  switch(status) {
    case 'em_execucao': return 'bg-green-500';
    case 'concluida': return 'bg-gray-500';
    ...
  }
};

// DEPOIS
import { STATUS_FASE_CORES } from '../constants/cidadesConstants';
const getStatusColor = (status) => STATUS_FASE_CORES[status]?.bg || 'bg-gray-400';
```

**5. Substituir função buildPlanoDinamico:**
```javascript
// ANTES (linhas 163-268)
const buildPlanoDinamico = (campanhas) => {
  const fasesPlanejamento = {
    'Fase 1': {
      periodo: getFasePeriodo('Fase 1'), // chamada local
      status: getFaseStatus('Fase 1'),
      ...
    }
  };
  ...
};

// DEPOIS
import { FASES_CONFIG } from '../constants/cidadesConstants';
import { getFasePeriodo, getFaseStatus } from '../utils/metasUtils';

const buildPlanoDinamico = (campanhas) => {
  const fasesPlanejamento = {};
  
  Object.keys(FASES_CONFIG).forEach(fase => {
    fasesPlanejamento[fase] = {
      ...FASES_CONFIG[fase],
      periodo: getFasePeriodo(fase),
      status: getFaseStatus(fase),
      ...
    };
  });
  ...
};
```

**Economia:** ~80 linhas removidas, 33 imports de ícones podem ser reduzidos

---

## 📊 IMPACTO ESTIMADO

### TabelaMetasCidades.jsx
- **Linhas antes:** 354
- **Linhas após:** ~250 (-104 linhas, -29%)
- **Remoções principais:**
  - cidadeIds hardcoded: 7 linhas
  - processarDadosCidades: 90 linhas
  - Lógica de ordenação duplicada: 7 linhas

### MetasCidades.jsx
- **Linhas antes:** 3.529
- **Linhas após Phase 1:** ~3.400 (-129 linhas, -4%)
- **Remoções principais:**
  - getFasePeriodo: 9 linhas
  - getFaseStatus: 16 linhas
  - getPartPeriodo: 12 linhas
  - getPartStatus: 13 linhas
  - getStatusColor, getStatusIcon, getStatusText: ~60 linhas
  - Imports de ícones não usados: ~19 linhas

**Total Phase 1:** -233 linhas removidas

---

## ✅ CHECKLIST DE INTEGRAÇÃO

### TabelaMetasCidades.jsx
- [ ] Adicionar imports de cidadesConstants
- [ ] Adicionar imports de processCidadesData
- [ ] Remover objeto cidadeIds hardcoded
- [ ] Remover função processarDadosCidades local
- [ ] Substituir chamadas por imports
- [ ] Atualizar função de ordenação
- [ ] Testar carregamento de dados
- [ ] Verificar exibição na tabela

### MetasCidades.jsx
- [ ] Adicionar imports de cidadesConstants
- [ ] Adicionar imports de metasUtils
- [ ] Remover funções getFasePeriodo, getFaseStatus, getPartPeriodo, getPartStatus
- [ ] Substituir chamadas por imports
- [ ] Atualizar função buildPlanoDinamico para usar FASES_CONFIG
- [ ] Substituir cores hardcoded por STATUS_CORES
- [ ] Remover imports de ícones não utilizados
- [ ] Testar abertura da aba
- [ ] Verificar formulários e modais
- [ ] Confirmar que fases são exibidas corretamente

### Testes Gerais
- [ ] Executar `npm run dev` sem erros
- [ ] Abrir aba "Metas por Cidades"
- [ ] Verificar que tabela carrega dados
- [ ] Testar filtros (por fase, ordenação)
- [ ] Abrir modal de criação de meta
- [ ] Editar uma fase existente
- [ ] Verificar que cores e ícones aparecem corretamente
- [ ] Confirmar que percentuais calculam certo
- [ ] Validar que não há erros no console

---

## 🎯 PRÓXIMOS PASSOS (após Phase 1)

**Phase 2 (Dias 2-3):** Break MetasCidades.jsx into components
- Criar pasta `frontend/src/components/MetasCidades/`
- Extrair EditFaseForm.jsx (~80 lines)
- Extrair StatusFase.jsx (~200 lines)
- Extrair FormularioCadastroMetas.jsx (~450 lines)
- Extrair TabelaExecucao.jsx (~200 lines)
- Extrair TabelaExecucaoComCruzamento.jsx (~150 lines)
- Criar hooks: usePlanoDinamico, useMetasCidades, useCampanhas

**Phase 3 (Dias 4-5):** Final refactor and testing
- Refatorar TabelaMetasCidades para usar hooks compartilhados
- Remover duplicação completa
- Testes end-to-end
- Documentação final

---

## 🔧 COMANDOS ÚTEIS

```powershell
# Executar dev server
npm run dev

# Verificar erros de build
npm run build

# Contar linhas de um arquivo
Get-Content "frontend/src/components/MetasCidades.jsx" | Measure-Object -Line

# Buscar imports não usados
eslint frontend/src/components/MetasCidades.jsx --fix
```

---

## 📝 NOTAS IMPORTANTES

1. **Não quebrar funcionalidade:** Cada refactoring deve manter 100% da funcionalidade existente
2. **Testar incrementalmente:** Fazer uma alteração, testar, commit, próxima alteração
3. **Preservar dados reais:** Garantir que API calls continuam funcionando
4. **Manter performance:** Não introduzir re-renders desnecessários

**Criado em:** $(date)  
**Autor:** GitHub Copilot  
**Versão:** 1.0  
**Status:** 📋 Aguardando execução da Task 4
