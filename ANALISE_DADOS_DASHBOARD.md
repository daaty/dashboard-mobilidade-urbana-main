# 🔍 ANÁLISE COMPLETA DOS DADOS EXIBIDOS NO DASHBOARD

Data da Análise: 11 de outubro de 2025

---

## 📊 DADOS EXIBIDOS vs REALIDADE

### ✅ **DADOS QUE ESTÃO CORRETOS:**

1. **Header Dinâmico:**
   - ✅ "Monitoramento em tempo real da execução da **1 fase**" (plural correto)
   - ✅ Período: "31 de out. a 30 de dez." (calculado dinamicamente)
   - ✅ "13 cidades no plano" (mas mostra 33 em outro lugar)

2. **Cards de Cidades:**
   - ✅ Status: "ativa"
   - ✅ Fases diferentes: "lançamento", "Fase 1", "Fase 2"
   - ✅ Meta Quantidade: 100, 80, 150
   - ✅ Orçamentos: R$ 5.000, R$ 3.200, R$ 7.500
   - ✅ Tipos: marketing_digital, aquisicao_motoristas, aquisicao_corridas

3. **Fases Estratégicas (cards grandes no final):**
   - ✅ Fase 1: Peixoto de Azevedo, Matupá, Guarantã do Norte
   - ✅ Fase 2: Peixoto de Azevedo, Nova Monte Verde, Matupá
   - ✅ Fase 3: Nova Bandeirantes, Nova Monte Verde, Guarantã do Norte
   - ✅ Dados de motoristas e corridas aparentam ser reais
   - ✅ Controle orçamentário estruturado

---

## ⚠️ **INCONSISTÊNCIAS IDENTIFICADAS:**

### 1. **CONTRADIÇÃO NO NÚMERO DE CIDADES:**
```
Header: "13 cidades no plano"
Card KPI: "33 Cidades no Plano | Ativas: 33 • Planejadas: 0"
```
**Problema:** Qual é o número correto? 13 ou 33?

**Causa Provável:**
- Endpoint `/api/dashboard-executivo/campanhas` retorna **33 campanhas**
- Função `calcularCidadesStatus()` conta campanhas, não cidades únicas
- Pode ter múltiplas campanhas para a mesma cidade

---

### 2. **"CIDADE NÃO ENCONTRADA" NOS CARDS:**
```
Comparativo de Performance por Cidade:
- Card 1: "Cidade não encontrada"
- Card 2: "Cidade não encontrada"  
- Card 3: "Cidade não encontrada"
```

**Causa Raiz Confirmada:**
```json
// Dados do endpoint /api/dashboard-executivo/campanhas
{
  "cidade": {
    "id": null,        // ← cidade_id NULL no banco
    "nome": "Cidade não encontrada",
    "populacao": 0
  }
}
```

**Problema no Backend:**
```python
# backend/routes/dashboard_executivo.py linha ~254
cidade = db.query(CidadesDemografia).filter(
    CidadesDemografia.id == campanha.cidade_id
).first()

campanha_data = {
    "cidade": {
        "id": cidade.id if cidade else None,
        "nome": cidade.cidade if cidade else "Cidade não encontrada",  # ← AQUI!
        "populacao": ...
    }
}
```

**Solução:** A tabela `Campanha` tem DOIS campos de cidade:
- `cidade_id` (ForeignKey - está NULL nas primeiras campanhas)
- `cidade` (String - campo antigo que provavelmente tem o nome)

---

### 3. **FASES MOSTRANDO DADOS REAIS MAS CARDS "AGUARDANDO INÍCIO":**

**Cards Performance (topo):**
- Status: "Aguardando início" ❌
- Meta Quantidade: exibida ✅
- Nenhum dado de performance

**Cards Fases Estratégicas (final):**
- Fase 1: 27 motoristas, 31 corridas ✅
- Fase 2: 27 motoristas, 394 corridas ✅
- Fase 3: 24 motoristas, 447 corridas ✅

**Problema:** Os cards de performance deveriam mostrar dados reais se as fases já têm dados!

---

### 4. **TODAS AS FASES MOSTRAM "🔴 Atrasado":**
```
Fase 1: Motoristas 27/750 (3.6%) - Atrasado
        Corridas 31/12500 (0.2%) - Atrasado
        
Fase 2: Motoristas 27/780 (3.5%) - Atrasado  
        Corridas 394/13000 (3.0%) - Atrasado
        
Fase 3: Motoristas 24/520 (4.6%) - Atrasado
        Corridas 447/8800 (5.1%) - Atrasado
```

**Análise:**
- Todas estão entre 2-5% de progresso
- Todas marcadas como "Atrasado"
- Fase 1 está "Em Execução" (01/ago a 14/set) mas estamos em **11 de outubro**!
- Fase 1 deveria estar **CONCLUÍDA** ou ter 100% de progresso

**Problema:** Datas das fases parecem estar desatualizadas ou lógica de status não considera a data atual.

---

### 5. **ORÇAMENTO: CONTRADIÇÃO ENTRE CARDS:**

**Card Orçamento Total (topo):**
```
R$ 97.100 Orçamento Total Empenhado
60.0% executado
R$ 58.260 Já Pago/Liquidado
```

**Cards de Fases (final):**
```
Fase 1: Previsto R$ 500.000 | Empenhado R$ 0 | Pago R$ 0
Fase 2: Previsto R$ 600.000 | Empenhado R$ 0 | Pago R$ 0
Fase 3: Previsto R$ 450.000 | Empenhado R$ 0 | Pago R$ 0
```

**Problema:** 
- Card geral mostra R$ 97.100 empenhado e R$ 58.260 pago
- Cards de fases mostram R$ 0 empenhado e R$ 0 pago
- **Onde está a origem dos R$ 97.100?**

---

### 6. **PROJEÇÃO ESTRATÉGICA SEM FONTE CLARA:**
```
61 corridas/motorista/ano
Total Motoristas: 55
Total Corridas: 280
```

**Questionamento:**
- De onde vêm esses 55 motoristas? (soma das fases = 27+27+24 = 78)
- De onde vêm 280 corridas? (soma das fases = 31+394+447 = 872)
- Como chegou em 61 corridas/motorista/ano?

---

## 🎯 **PROBLEMAS TÉCNICOS CRÍTICOS:**

### **A. Campo `cidade_id` NULL**
**Impacto:** Cards mostram "Cidade não encontrada"

**Verificação Necessária:**
```sql
SELECT id, nome, cidade, cidade_id FROM campanhas LIMIT 5;
```

**Soluções:**
1. Popular `cidade_id` fazendo lookup por nome do campo `cidade` (string)
2. Modificar endpoint para usar campo `cidade` (string) como fallback
3. Criar script de migração para popular cidade_id

---

### **B. Contagem de Cidades vs Campanhas**
**Problema:** Header diz "13" mas card KPI diz "33"

**Verificação:**
```javascript
// No código atual fazemos:
const cidadesUnicas = new Set(campanhas.map(c => c.cidade?.nome || c.cidade))
console.log('Total cidades únicas:', cidadesUnicas.size)
console.log('Total campanhas:', campanhas.length)
```

**Causa:** Estamos contando campanhas (33) ao invés de cidades únicas

---

### **C. Mismatch entre Tabelas**
**Dados estão espalhados em:**
- `campanhas` → campos: meta_quantidade, orcamento_previsto, cidade (string), cidade_id (FK)
- `fases_planejamento` → campos: data_inicio, data_fim, orcamento_previsto, cidades (relação)
- `metas_progressivas` → campos: meta_motoristas, meta_corridas, resultado_motoristas, resultado_corridas
- `cidades_demografia` → campos: id, cidade (nome), populacao

**Problema:** Cards de Performance tentam usar campos de `campanhas` que não têm dados de motoristas/corridas

---

## 📋 **AÇÕES RECOMENDADAS (PRIORIDADE):**

### **🔴 CRÍTICO - Fazer Agora:**

1. **Corrigir cidade_id NULL:**
   - Criar script para popular cidade_id fazendo match com CidadesDemografia
   - OU modificar endpoint para usar campo `cidade` (string) como fallback

2. **Corrigir contagem de cidades:**
   - Usar `new Set()` com campo correto para contar cidades únicas
   - Verificar se são 13 ou 33 cidades reais

3. **Unificar fonte de dados orçamentários:**
   - Investigar de onde vem R$ 97.100 (card geral)
   - Por que fases mostram R$ 0?

### **🟡 IMPORTANTE - Fazer Depois:**

4. **Atualizar lógica de status das fases:**
   - Considerar data atual vs data_fim
   - Fase 1 (terminou em 14/set) deveria estar "Concluída"

5. **Conectar Cards Performance com dados reais:**
   - Buscar de `metas_progressivas` ou calcular agregado por cidade
   - Remover "Aguardando início" se já tem dados

6. **Validar Projeção Estratégica:**
   - Conferir fonte dos 55 motoristas e 280 corridas
   - Recalcular 61 corridas/motorista/ano

---

## 🔍 **PRÓXIMA AÇÃO IMEDIATA:**

**Vou criar script para verificar a estrutura real do banco:**
1. Quantas cidades únicas existem?
2. Quais campanhas têm cidade_id NULL?
3. Qual campo usar: `cidade` (string) ou `cidade_id` (FK)?
