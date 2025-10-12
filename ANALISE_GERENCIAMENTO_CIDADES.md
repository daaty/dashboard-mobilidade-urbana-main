# 🔍 ANÁLISE: GERENCIAMENTO DE CIDADES

Data: 11 de outubro de 2025

---

## 📊 DADOS EXIBIDOS vs REALIDADE

### ⚠️ **INCONSISTÊNCIAS CRÍTICAS:**

#### 1. **DUPLICAÇÃO DE CIDADES**
```
🟢 Cidades Operacionais (3 cidades):
  - MATUPA (lançamento)
  - PEIXOTO (Fase 1)
  - MATUPA (Fase 1)  ← DUPLICADO!

🟡 Em Planejamento (2 cidades):
  - Monte Verde (Fase 1)
  - Nova Bandeirantes (Fase 1)
```

**Problema:** MATUPA aparece 2 vezes na mesma categoria!
- Uma vez em "lançamento"
- Outra em "Fase 1"

**Causa Provável:** Estão sendo exibidas CAMPANHAS ao invés de CIDADES únicas.

---

#### 2. **CLASSIFICAÇÃO INCORRETA POR FASE**

**Dados mostrados:**
```
🟢 Cidades Operacionais: MATUPA, PEIXOTO, MATUPA
🔵 Expansão Fase 2: Paranaíta, Alta Floresta
🟣 Expansão Fase 3: Colíder, Nova Canaã do Norte, Carlinda
🟡 Em Planejamento: Monte Verde, Nova Bandeirantes
```

**Problema:** Monte Verde e Nova Bandeirantes estão marcadas como "Fase 1" mas aparecem em "Em Planejamento"!

**Lógica Esperada:**
- **Fase 1** → deveria estar em "Cidades Operacionais"
- **Fase 2** → "Expansão Fase 2"
- **Fase 3** → "Expansão Fase 3"
- **Planejada** → "Em Planejamento"

---

#### 3. **CONTAGEM DE CIDADES ERRADA**

**Header mostra:**
```
12 cidades monitoradas
5 Cidades Ativas
```

**Realidade na tela:**
```
🟢 Cidades Operacionais: 3 cidades (mas MATUPA duplicado = 2 únicas)
🔵 Expansão Fase 2: 2 cidades
🟣 Expansão Fase 3: 3 cidades
🟡 Em Planejamento: 2 cidades
-----------------------------------
TOTAL: 10 cidades (se contar MATUPA só 1 vez = 9 cidades)
```

**Problema:** 
- Diz "12 cidades" mas mostra apenas 9-10 (dependendo da duplicação)
- "5 Cidades Ativas" não bate com "3 cidades" em Operacionais

---

#### 4. **TODOS MOTORISTAS = 0**

**Cada card mostra:**
```
0 Motoristas
```

**Problema:** Mesmo cidades com muitas corridas (Monte Verde: 276, Nova Bandeirantes: 49) têm 0 motoristas!

**Causa Provável:** 
- Endpoint `/api/drivers/kpis` não está retornando dados
- OU campo `total_drivers` está sempre 0
- OU lógica de busca está errada

---

#### 5. **RECEITA ESTIMADA INCONSISTENTE**

```
MATUPA (lançamento): 4 corridas → R$ 50 (R$ 12,50/corrida)
PEIXOTO: 6 corridas → R$ 75 (R$ 12,50/corrida)
MATUPA (Fase 1): 4 corridas → R$ 50 (R$ 12,50/corrida)
Monte Verde: 276 corridas → R$ 3.450 (R$ 12,50/corrida)
Nova Bandeirantes: 49 corridas → R$ 613 (R$ 12,50/corrida)
```

**Observação:** Taxa fixa de R$ 12,50 por corrida. Parece correto.

---

#### 6. **NÚMERO DE CAMPANHAS SUSPEITO**

```
MATUPA (lançamento): 3 campanhas ativas
PEIXOTO: 3 campanhas ativas
MATUPA (Fase 1): 3 campanhas ativas ← MESMA CIDADE = MESMAS CAMPANHAS?
Paranaíta: 4 campanhas ativas
Alta Floresta: 2 campanhas ativas
Colíder: 4 campanhas ativas
Nova Canaã do Norte: 4 campanhas ativas
Carlinda: 4 campanhas ativas
Monte Verde: 2 campanhas ativas
Nova Bandeirantes: 4 campanhas ativas
```

**Total:** 3+3+3+4+2+4+4+4+2+4 = **33 campanhas**

**Confirmação:** Bate com os 33 campanhas do endpoint `/api/dashboard-executivo/campanhas`

---

## 🎯 **PROBLEMAS TÉCNICOS IDENTIFICADOS:**

### **A. DUPLICAÇÃO DE CIDADES**

**Causa Raiz:** Está mapeando CAMPANHAS ao invés de agrupar por CIDADE

**Código Problemático (provável):**
```javascript
// ERRADO:
cidades = campanhas.map(camp => ({ 
  nome: camp.cidade.nome,
  fase: camp.fase
}))
// Resultado: 33 "cidades" (uma por campanha)

// CORRETO:
const cidadesUnicas = [...new Map(
  campanhas.map(camp => [camp.cidade.id, camp])
).values()]
// Resultado: Apenas cidades únicas
```

---

### **B. CLASSIFICAÇÃO INCORRETA**

**Monte Verde e Nova Bandeirantes:**
- Mostra "Fase 1" no card
- Mas estão na categoria "Em Planejamento" 🟡
- Deveriam estar em "Cidades Operacionais" 🟢

**Lógica de Agrupamento Esperada:**
```javascript
const grupos = {
  operacionais: campanhas.filter(c => c.status === 'ativa' && c.fase === 'Fase 1'),
  fase2: campanhas.filter(c => c.fase === 'Fase 2'),
  fase3: campanhas.filter(c => c.fase === 'Fase 3'),
  planejamento: campanhas.filter(c => c.status === 'planejada')
}
```

---

### **C. MOTORISTAS SEMPRE 0**

**Possíveis Causas:**
1. Endpoint `/api/drivers/kpis` retorna `total_drivers: 0` para todas as cidades
2. Campo sendo buscado está errado (ex: `active_drivers` ao invés de `total_drivers`)
3. Dados de motoristas não estão cadastrados no banco

**Teste Necessário:**
```bash
curl "http://localhost:8000/api/drivers/kpis?period=3_months&city=Monte%20Verde"
```

---

### **D. BADGES DE STATUS ESTRANHOS**

```
🌱 Iniciando    → MATUPA, PEIXOTO (Fase 1 com poucas corridas)
🔮 Fase 2/3     → Paranaíta, Alta Floresta, Colíder (0 corridas)
⏳ Aguardando   → Nova Canaã, Carlinda (0 corridas)
🚀 Muito Ativa  → Monte Verde (276 corridas!)
⚡ Ativa        → Nova Bandeirantes (49 corridas)
```

**Lógica dos Badges:**
- Baseado em número de corridas? ✅ Parece correto
- Mas Monte Verde (🚀 Muito Ativa) está em "Em Planejamento"? ❌ Incoerente

---

## 📋 **AÇÕES CORRETIVAS NECESSÁRIAS:**

### **🔴 CRÍTICO (Fazer AGORA):**

1. **Eliminar Duplicação de MATUPA:**
   - Agrupar por `cidade.id` ou `cidade.nome` único
   - Consolidar múltiplas campanhas da mesma cidade

2. **Corrigir Classificação de Monte Verde e Nova Bandeirantes:**
   - Se estão em Fase 1 → mover para "Cidades Operacionais"
   - OU corrigir a fase delas no banco de dados

3. **Investigar Motoristas = 0:**
   - Testar endpoint de KPIs
   - Verificar se há motoristas cadastrados no banco

### **🟡 IMPORTANTE (Fazer DEPOIS):**

4. **Corrigir Contagem "12 cidades":**
   - Recalcular total real de cidades únicas
   - Atualizar "5 Cidades Ativas"

5. **Revisar Lógica de Agrupamento:**
   - Definir critério claro: status? fase? ambos?
   - Documentar regras de negócio

---

## 🔍 **PRÓXIMAS AÇÕES:**

**Vou criar script para:**
1. Listar cidades ÚNICAS (sem duplicação)
2. Mostrar quantas campanhas cada cidade tem
3. Verificar dados de motoristas via API
4. Sugerir correção de lógica de agrupamento

**Aguardando autorização para prosseguir!** 🚀
