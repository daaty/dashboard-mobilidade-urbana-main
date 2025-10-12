# 📊 RESUMO EXECUTIVO - Análise de Dados Reais

**Data:** 2025-01-XX  
**Sprint:** Pós-Sprint 1  
**Objetivo:** Análise estrutural das tabelas operacionais para integração com Aba de Metas por Cidade

---

## ✅ O QUE FOI FEITO

### 1. Estrutura Real Mapeada ✅

Analisamos 4 tabelas operacionais do PostgreSQL:

| Tabela | Registros | Informação Chave |
|--------|-----------|------------------|
| **rides_data** | 1.044 | Corridas (Completed, Cancelled, Missed, Ongoing, Scheduled) |
| **driver_personal_details** | 42 | Motoristas com histórico de corridas |
| **drivers_data** | 3.792 | Métricas de performance dos motoristas |
| **passenger_personal_details** | 271 | Passageiros com histórico de corridas |

### 2. Descoberta Crítica: Estrutura JSON 🎯

A tabela `rides_data` armazena dados em formato JSON dentro de um campo TEXT:

```json
{
  "tableName": "Completed Rides",
  "newRecords": [
    [engagement_id, driver_name, passenger_name, ..., CIDADE]
  ]
}
```

**IMPORTANTE:** O campo **CIDADE** está em índices diferentes dependendo do tipo de corrida:
- **Completed Rides:** índice [15] → "MATUPA", "PEIXOTO"
- **Cancelled Rides:** índice [17] → "PEIXOTO"
- **Missed Rides:** índice [8] → "PEIXOTO"

### 3. Cidades Identificadas 🏙️

Encontramos 5 cidades com dados operacionais:

1. **MATUPA** (Matupá)
2. **PEIXOTO** (Peixoto de Azevedo)
3. **Nova Monte Verde**
4. **Guarantã do Norte**
5. **Nova Bandeirantes**

### 4. Dados Disponíveis por Tipo de Corrida 📈

| Tipo | Registros | Período |
|------|-----------|---------|
| Ongoing Rides | 486 | 22/08/2025 - 08/10/2025 |
| Completed Rides | 430 | 13/08/2025 - 09/10/2025 |
| Cancelled Rides | 52 | 13/08/2025 - 09/10/2025 |
| Missed Rides | 47 | 13/08/2025 - 09/10/2025 |
| Scheduled Rides | 26 | 04/09/2025 - 09/10/2025 |

**Total:** 1.041 corridas com dados estruturados

---

## 🎯 CAMPOS ÚTEIS PARA METAS

### De `rides_data` (JSON):
- **engagement_id** [0] - ID único da corrida
- **driver_name** [1] - Nome do motorista
- **passenger_name** [2] - Nome do passageiro
- **pickup_location** [4] - Local de embarque (contém nome da cidade)
- **drop_location** [5] - Local de desembarque
- **ride_start_time** [6] - Data/hora início (TIMESTAMP)
- **ride_end_time** [7] - Data/hora fim
- **fare_value** [12] - Valor da corrida (NUMERIC)
- **CITY** [15/17/8] - **Cidade** (dependendo do tipo)

### De `driver_personal_details`:
- **driver_id** - ID do motorista (relacionamento)
- **city** - Cidade do motorista (direto, não JSON)
- **rides_history** (JSONB) - Array de corridas com:
  - `engagement_id`, `fare`, `distance_travelled`, `drop_time`, `customer_id`
- **wallet_transactions** - Transações financeiras

### De `drivers_data`:
- **additional_data** (JSONB) - Métricas de performance:
  - `Success Rides` - Corridas completadas
  - `Missed Rides` - Corridas perdidas
  - `Active Days` - Dias ativos
  - `Online Hours` - Horas online
  - `User Cancelled Rides` - Cancelamentos por passageiro
  - `Driver Cancelled Rides` - Cancelamentos por motorista

### De `passenger_personal_details`:
- **passenger_id** - ID do passageiro
- **city** - Cidade do passageiro
- **total_rides** - Total de corridas
- **total_spent** - Total gasto
- **rides_history** (JSONB) - Histórico de corridas

---

## 📋 QUERIES DEMONSTRADAS

### 1. Corridas Completadas por Cidade (últimos 2 meses)

```sql
SELECT 
    CASE 
        WHEN ride_data::json->'newRecords'->0->>15 = 'MATUPA' THEN 'Matupá'
        WHEN ride_data::json->'newRecords'->0->>15 = 'PEIXOTO' THEN 'Peixoto de Azevedo'
        ELSE ride_data::json->'newRecords'->0->>15
    END as cidade,
    COUNT(*) as total_corridas,
    SUM(CAST(ride_data::json->'newRecords'->0->>12 AS NUMERIC)) as receita_total
FROM rides_data
WHERE table_name = 'Completed Rides'
    AND CAST(ride_data::json->'newRecords'->0->>6 AS TIMESTAMP) >= NOW() - INTERVAL '2 months'
GROUP BY cidade
ORDER BY total_corridas DESC;
```

### 2. Motoristas Ativos por Cidade

```sql
SELECT 
    city,
    COUNT(DISTINCT driver_id) as motoristas_ativos,
    SUM(jsonb_array_length(rides_history)) as total_corridas_motorista
FROM driver_personal_details
WHERE city IS NOT NULL
GROUP BY city
ORDER BY motoristas_ativos DESC;
```

### 3. Métricas Consolidadas

```sql
WITH corridas AS (
    SELECT 
        ride_data::json->'newRecords'->0->>15 as cidade,
        COUNT(*) as total
    FROM rides_data
    WHERE table_name = 'Completed Rides'
    GROUP BY cidade
),
motoristas AS (
    SELECT city, COUNT(*) as qtd
    FROM driver_personal_details
    WHERE city IS NOT NULL
    GROUP BY city
),
passageiros AS (
    SELECT city, COUNT(*) as qtd
    FROM passenger_personal_details
    WHERE city IS NOT NULL AND city != 'N/A'
    GROUP BY city
)
SELECT 
    COALESCE(c.cidade, m.city, p.city) as cidade,
    c.total as corridas,
    m.qtd as motoristas,
    p.qtd as passageiros
FROM corridas c
FULL OUTER JOIN motoristas m ON UPPER(c.cidade) = UPPER(m.city)
FULL OUTER JOIN passageiros p ON UPPER(c.cidade) = UPPER(p.city);
```

---

## 🚧 DESAFIOS IDENTIFICADOS

### 1. **Índices JSON Variáveis** ⚠️
- Completed Rides usa índice [15] para cidade
- Cancelled Rides usa índice [17]
- Missed Rides usa índice [8]
- **Solução:** CASE statement para cada tipo de corrida

### 2. **Normalização de Cidades** ⚠️
- "MATUPA" ≠ "Matupá" ≠ "matupa" (mas são a mesma cidade)
- **Solução:** Dicionário de normalização + UPPER() em queries

### 3. **Performance de Queries JSON** ⚠️
- Parsing JSON em cada query pode ser lento com milhares de registros
- **Solução:** 
  - Criar índices em `table_name`
  - Considerar cache de resultados
  - Futuro: desnormalizar dados em tabela `rides_normalized`

### 4. **Dados Incompletos** ⚠️
- Algumas corridas não têm campo cidade preenchido
- **Solução:** Tentar extrair de `pickup_location` ou marcar como "NÃO IDENTIFICADA"

---

## 📄 DOCUMENTOS CRIADOS

1. **ESTRUTURA_REAL_DADOS_METAS.md** (100 linhas)
   - Estrutura completa de todas as 4 tabelas
   - Mapeamento de campos JSON
   - Queries de exemplo
   - Relacionamentos entre tabelas

2. **PLANO_ACAO_METAS_CIDADES_V2.md** (600 linhas)
   - Sprint 2 ATUALIZADA com dados reais
   - Task 2.1: Script `populate_metas_from_real_data.py`
   - Task 2.2: Endpoint consolidado `/metas-estrategicas/consolidado/{cidade_id}`
   - Task 2.3: Integração frontend (remover Math.random())
   - Task 2.4: Testes e validação
   - Estimativa: 5 dias úteis

3. **Scripts de Análise:**
   - `analisar_tabelas_reais.py` - Análise geral das 4 tabelas
   - `analisar_rides_data_colunas.py` - Estrutura detalhada de rides_data
   - `analisar_rides_json.py` - Extração e mapeamento de JSON

---

## 🎯 PRÓXIMOS PASSOS

### Imediato (Aguardando Aprovação):
1. ✅ **Revisar PLANO_ACAO_METAS_CIDADES_V2.md**
   - Confirma que a abordagem de extração JSON está correta
   - Valida queries de exemplo
   - Aprova estimativa de 5 dias para Sprint 2

2. ✅ **Decisão sobre Normalização**
   - Criar tabela `rides_normalized` agora ou depois?
   - Manter extração JSON direto ou pré-processar?

### Sprint 2 (Após Aprovação):
1. **Criar `populate_metas_from_real_data.py`**
   - Extração de corridas por cidade e período
   - Normalização de cidades (MATUPA → Matupá)
   - Cálculo de métricas (corridas, receita, motoristas, passageiros)
   - Atualização de `metas_progressivas.resultado_*`

2. **Endpoint Consolidado**
   - `/metas-estrategicas/consolidado/{cidade_id}`
   - Retorna metas + resultados + percentual de atingimento
   - Dados em tempo real (query direto em rides_data)

3. **Frontend: Remover Math.random()**
   - Integrar com endpoint consolidado
   - Exibir dados reais com percentuais
   - Cores indicativas (verde/amarelo/vermelho)

4. **Testes**
   - Backend: extração, normalização, API
   - Frontend: ausência de Math.random(), exibição de dados reais

---

## 📊 MÉTRICAS ESPERADAS - SPRINT 2

| Métrica | Valor Atual | Meta Sprint 2 |
|---------|-------------|---------------|
| **Dados Reais** | 0% (usa Math.random()) | 100% (extração de rides_data) |
| **Cidades com Metas** | 3 (IDs: 3, 6, 7) | 5 (todas com dados operacionais) |
| **Acurácia** | 0% (dados mockados) | 95%+ (dados reais do banco) |
| **Cobertura de Testes** | 23 testes (Sprint 1) | +15 testes (Sprint 2) |

---

## ✅ VALIDAÇÃO NECESSÁRIA

Antes de iniciar Sprint 2, preciso de confirmação sobre:

1. **Abordagem de Extração JSON está correta?**
   - [ ] Sim, usar CASE statement para índices variáveis
   - [ ] Não, preferir outra solução (qual?)

2. **Normalização de Cidades OK?**
   - [ ] Sim, usar dicionário MATUPA → Matupá
   - [ ] Não, criar tabela de_para em banco

3. **Estimativa de 5 dias está razoável?**
   - [ ] Sim, pode iniciar
   - [ ] Não, precisa ajustar (por quê?)

4. **Prioridade de Tasks:**
   - [ ] Seguir ordem: 2.1 → 2.2 → 2.3 → 2.4
   - [ ] Ajustar prioridade (qual ordem?)

---

**Aguardando Aprovação para Iniciar Sprint 2** 🚀

---

**Documento Gerado:** 2025-01-XX  
**Baseado em:** Análise de 4 tabelas PostgreSQL (1.044 rides, 42 drivers, 3.792 performance records, 271 passengers)  
**Próxima Ação:** Aprovação do usuário para iniciar `populate_metas_from_real_data.py`
