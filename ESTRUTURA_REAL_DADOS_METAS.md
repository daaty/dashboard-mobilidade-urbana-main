# 📊 ESTRUTURA REAL DOS DADOS - Metas por Cidade

**Data:** 2025-01-XX  
**Status:** ✅ Análise Completa  
**Objetivo:** Documentar estrutura real das tabelas para integração com Aba de Metas

---

## 🎯 RESUMO EXECUTIVO

**Descobertas Críticas:**
1. ✅ **rides_data** contém TODOS os tipos de corridas (Completed, Cancelled, Missed, Ongoing, Scheduled)
2. ✅ **Cidade está no índice [15]** do array JSON (últim campo) - valores: MATUPA, PEIXOTO, etc
3. ✅ **4 tabelas operacionais** confirmadas: rides_data, driver_personal_details, drivers_data, passenger_personal_details
4. ⚠️ **Estrutura de dados é JSON** dentro de campo TEXT, não colunas diretas

---

## 📋 TABELA 1: rides_data

### Estrutura Geral
```
Colunas:
  - id (integer)
  - table_name (varchar) - Tipo: "Completed Rides", "Cancelled Rides", "Missed Rides", etc
  - data_hash (varchar)
  - ride_data (TEXT) - ⚠️ JSON com estrutura: {"tableName": "...", "newRecords": [[...]]}
  - scraped_at (timestamp)
  - session_info (varchar)
  - source (varchar) - Valores: "import_excel", "monitoring-service-adapted"
```

### Tipos de Corridas (table_name)
| Tipo | Total Registros | Período |
|------|----------------|---------|
| **Ongoing Rides** | 486 | 22/08/2025 - 08/10/2025 |
| **Completed Rides** | 430 | 13/08/2025 - 09/10/2025 |
| **Cancelled Rides** | 52 | 13/08/2025 - 09/10/2025 |
| **Missed Rides** | 47 | 13/08/2025 - 09/10/2025 |
| **Scheduled Rides** | 26 | 04/09/2025 - 09/10/2025 |
| rides_data (genérico) | 3 | 19/08/2025 |

**TOTAL: 1.044 registros**

---

## 🗺️ MAPEAMENTO: Completed Rides (JSON Array)

**Estrutura do JSON:**
```json
{
  "tableName": "Completed Rides",
  "newRecords": [
    [campo0, campo1, campo2, ...campo15]
  ]
}
```

### Índices dos Campos (Array)
| Índice | Campo | Exemplo | Tipo |
|--------|-------|---------|------|
| **[0]** | engagement_id | 572095015 | int |
| [1] | driver_name | "Rogério Oliveira Lima" | string |
| [2] | passenger_name | "Ana Carolina Diefenthaler" | string |
| [3] | passenger_phone | "5566996588792" | string |
| [4] | pickup_location | "Machadão Atacadista Matupá..." | string |
| [5] | drop_location | "1612, Rua 9, União, Matupá" | string |
| [6] | ride_start_time | "2025-04-09 10:29:54" | datetime |
| [7] | ride_end_time | "2025-04-09 10:34:54" | datetime |
| [8] | vehicle_type | "OFEREÇA SEU PREÇO" / "POPULAR" | string |
| [9] | status | "Concluído" | string |
| [10] | campo_10 | "--" | ? |
| [11] | campo_11 | "--" | ? |
| [12] | fare_value | "5" | numeric |
| [13] | campo_13 | "-" | ? |
| [14] | campo_14 | "-" | ? |
| **[15]** | **CITY** | **"MATUPA"** | **string** ⭐ |

**🎯 CAMPO CRÍTICO: Índice [15] = CIDADE**

---

## 🗺️ MAPEAMENTO: Cancelled Rides (JSON Array)

| Índice | Campo | Exemplo |
|--------|-------|---------|
| [0] | engagement_id | 571116030 |
| [1] | driver_id | 17174024 |
| [2] | driver_name | "Rogério Gelcivan" |
| [3] | user_id | 17177005 |
| [4] | user_phone | "5566996356157" |
| [5] | user_name | "valdiceia santos silva" |
| [6] | vehicle_type | "POPULAR" |
| [7] | pickup_location | "R. Corumbá, 390 - Peixoto de Azevedo" |
| [8] | drop_location | "nan" |
| [9] | campo_9 | "--" |
| [10] | campo_10 | "--" |
| [11] | cancellation_time | "2025-04-04 16:10:46" |
| [12] | cancellation_reason | "teste de aplicativo" |
| [13] | cancelled_by | "Cancelado pelo motorista" |
| [14] | campo_14 | "--" |
| [15] | campo_15 | (mais 3 campos) |
| [16] | campo_16 | ? |
| **[17]** | **CITY** | **"PEIXOTO"** ⭐ |

**⚠️ Cancelled Rides tem 18 campos (2 a mais que Completed)**

---

## 🗺️ MAPEAMENTO: Missed Rides (JSON Array)

| Índice | Campo | Exemplo |
|--------|-------|---------|
| [0] | ride_id | 179415327 |
| [1] | passenger_name | "Maycon Batista" |
| [2] | passenger_phone | "5566999595359" |
| [3] | pickup_location | "Avenida Rotary Internacional, 90, Peixoto" |
| [4] | vehicle_type | "POPULAR" |
| [5] | miss_reason | "Timeout Ride" |
| [6] | missed_time | "2025-04-19 02:56:39" |
| [7] | campo_7 | "nan" |
| **[8]** | **CITY** | **"PEIXOTO"** ⭐ |

**⚠️ Missed Rides tem apenas 9 campos**

---

## 👤 TABELA 2: driver_personal_details

### Estrutura
```
Colunas:
  - id (integer)
  - driver_id (varchar) ⭐ - Relacionamento com rides_data[1] ou [2]
  - city (varchar) ⭐ - "Nova Monte Verde", "Guarantã do Norte", "Nova Bandeirantes"
  - personal_data (jsonb) - Dados pessoais do motorista
  - rides_history (jsonb) - Histórico de corridas (engagement_id, fare, distance, etc)
  - wallet_transactions (jsonb) - Transações de carteira
  - subscription_history (jsonb)
  - additional_info (jsonb)
  - rides_cancelled (jsonb) - Corridas canceladas
  - extracted_at (timestamp)
  - updated_at (timestamp)
  - extraction_source (varchar) - "hybrid_scraper"
  - data_hash (varchar)
```

### Estatísticas
- **Total:** 42 registros
- **Cidades:** Nova Monte Verde, Guarantã do Norte, Nova Bandeirantes
- **rides_history:** Array de dicionários com fare, engagement_id, distance_travelled, drop_time, customer_id

**🔗 Relacionamento:** `driver_personal_details.driver_id` = `rides_data[1]` (driver_id em Cancelled) ou driver identificado em Completed

---

## 👤 TABELA 3: drivers_data

### Estrutura
```
Colunas:
  - id (integer)
  - driver_id (varchar) ⭐
  - name (varchar)
  - email (varchar)
  - mobile (varchar)
  - data_type (varchar) - "performance"
  - page_source (varchar) - "Driver Performance"
  - additional_data (jsonb) - Métricas: Active Days, Online Hours, Success Rides, etc
  - data_hash (varchar)
  - scraped_at (timestamp)
  - session_info (jsonb)
  - source (varchar) - "drivers-unified-transaction"
  - unique_id (varchar)
```

### Estatísticas
- **Total:** 3.792 registros
- **Métricas em additional_data:**
  - Vehicle: "POPULAR"
  - Active Days, Online Hours
  - Success Rides, Missed Rides, Rejected Rides
  - User Cancelled Rides, Driver Cancelled Rides
  - Request Sent, Requests Received

**🔗 Relacionamento:** `drivers_data.driver_id` = `driver_personal_details.driver_id`

---

## 🧑‍🤝‍🧑 TABELA 4: passenger_personal_details

### Estrutura
```
Colunas:
  - id (integer)
  - passenger_id (varchar) ⭐
  - full_name (varchar)
  - phone (varchar)
  - city (varchar) ⭐ - "Matupá", "N/A"
  - total_rides (integer)
  - total_spent (numeric)
  - personal_data (jsonb) - user_id, user_name, user_phone, city, etc
  - rides_history (jsonb) - engagement_id, driver_id, user_fare, ride_distance
  - additional_info (jsonb)
  - data_hash (varchar)
  - extraction_source (varchar) - "passenger_extractor"
  - extracted_at (timestamp with time zone)
  - created_at (timestamp with time zone)
  - updated_at (timestamp with time zone)
```

### Estatísticas
- **Total:** 271 registros
- **Cidades:** Matupá, N/A
- **rides_history:** engagement_id, driver_id, user_fare, ride_distance, preferred_mode (Wallet/Cash)

**🔗 Relacionamento:** `passenger_personal_details.passenger_id` = user_id em rides_data

---

## 🔗 MAPA DE RELACIONAMENTOS

```
┌─────────────────────────────────────────────────────────────┐
│                        rides_data                           │
│  (1.044 registros - JSON array com cidade no índice [15])  │
└─────────────────────────────────────────────────────────────┘
                    │                   │
         ┌──────────┴────────┐   ┌──────┴──────────┐
         │                   │   │                 │
         ▼                   ▼   ▼                 ▼
┌──────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│driver_personal_  │  │ drivers_data    │  │passenger_personal_  │
│details           │  │                 │  │details              │
│ (42 registros)   │  │ (3.792 reg)     │  │ (271 registros)     │
│ - driver_id      │  │ - driver_id     │  │ - passenger_id      │
│ - city ⭐       │  │ - performance   │  │ - city ⭐          │
│ - rides_history  │  │   metrics       │  │ - rides_history     │
└──────────────────┘  └─────────────────┘  └─────────────────────┘
```

**Joins Necessários:**
1. `rides_data::json->'newRecords'->>1 = driver_personal_details.driver_id`
2. `rides_data::json->'newRecords'->>3 = passenger_personal_details.passenger_id`
3. `driver_personal_details.driver_id = drivers_data.driver_id`

---

## 🎯 CAMPOS PARA METAS POR CIDADE

### Extração de Cidade
```sql
-- Completed Rides
CAST(ride_data::json->'newRecords'->0->>15 AS VARCHAR) AS city

-- Cancelled Rides  
CAST(ride_data::json->'newRecords'->0->>17 AS VARCHAR) AS city

-- Missed Rides
CAST(ride_data::json->'newRecords'->0->>8 AS VARCHAR) AS city
```

### Valores de Cidade Encontrados
- **MATUPA** (Matupá)
- **PEIXOTO** (Peixoto de Azevedo)
- **GUARANTA** (provavelmente Guarantã do Norte)
- **NOVA MONTE VERDE**
- **NOVA BANDEIRANTES**

---

## 📊 QUERIES PARA METAS

### 1. Total de Corridas Completadas por Cidade
```sql
SELECT 
    CAST(ride_data::json->'newRecords'->0->>15 AS VARCHAR) AS cidade,
    COUNT(*) as total_corridas,
    SUM(CAST(ride_data::json->'newRecords'->0->>12 AS NUMERIC)) as receita_total
FROM rides_data
WHERE table_name = 'Completed Rides'
    AND ride_data::json->'newRecords'->0->>15 IS NOT NULL
GROUP BY cidade
ORDER BY total_corridas DESC;
```

### 2. Motoristas Ativos por Cidade
```sql
SELECT 
    city,
    COUNT(DISTINCT driver_id) as motoristas_ativos,
    SUM(jsonb_array_length(rides_history)) as total_corridas_history
FROM driver_personal_details
WHERE city IS NOT NULL
GROUP BY city
ORDER BY motoristas_ativos DESC;
```

### 3. Passageiros por Cidade
```sql
SELECT 
    city,
    COUNT(*) as total_passageiros,
    SUM(total_rides) as corridas_realizadas,
    SUM(total_spent) as receita_total
FROM passenger_personal_details
WHERE city IS NOT NULL AND city != 'N/A'
GROUP BY city
ORDER BY total_passageiros DESC;
```

### 4. Consolidado de Metas (JOIN)
```sql
WITH corridas_cidade AS (
    SELECT 
        CAST(ride_data::json->'newRecords'->0->>15 AS VARCHAR) AS cidade,
        CAST(ride_data::json->'newRecords'->0->>6 AS TIMESTAMP) AS data_corrida,
        CAST(ride_data::json->'newRecords'->0->>12 AS NUMERIC) AS valor_corrida
    FROM rides_data
    WHERE table_name = 'Completed Rides'
        AND ride_data::json->'newRecords'->0->>15 IS NOT NULL
),
motoristas_cidade AS (
    SELECT city, COUNT(DISTINCT driver_id) as qtd_motoristas
    FROM driver_personal_details
    WHERE city IS NOT NULL
    GROUP BY city
),
passageiros_cidade AS (
    SELECT city, COUNT(*) as qtd_passageiros
    FROM passenger_personal_details
    WHERE city IS NOT NULL AND city != 'N/A'
    GROUP BY city
)
SELECT 
    COALESCE(cc.cidade, mc.city, pc.city) as cidade,
    COUNT(DISTINCT cc.cidade) as corridas_completadas,
    SUM(cc.valor_corrida) as receita_total,
    mc.qtd_motoristas,
    pc.qtd_passageiros
FROM corridas_cidade cc
FULL OUTER JOIN motoristas_cidade mc ON UPPER(cc.cidade) = UPPER(mc.city)
FULL OUTER JOIN passageiros_cidade pc ON UPPER(cc.cidade) = UPPER(pc.city)
GROUP BY cidade, mc.qtd_motoristas, pc.qtd_passageiros
ORDER BY corridas_completadas DESC;
```

---

## ✅ PRÓXIMOS PASSOS

1. **Atualizar PLANO_ACAO_METAS_CIDADES.md:**
   - Sprint 2: Popular metas_progressivas com dados reais
   - Criar queries de extração JSON
   - Normalizar nomes de cidades (MATUPA → Matupá)

2. **Criar Script de Integração:**
   - `populate_metas_from_real_data.py`
   - Extrair corridas por cidade e período
   - Calcular receita, motoristas ativos, passageiros

3. **Endpoint Consolidado:**
   - `/api/metas-estrategicas/consolidado/{city_id}`
   - JOIN real-time entre rides_data, driver_personal_details, passenger_personal_details
   - Calcular progresso vs metas

4. **Frontend Update:**
   - Remover Math.random()
   - Consumir endpoint consolidado
   - Exibir dados reais por cidade

---

## 🚨 OBSERVAÇÕES IMPORTANTES

⚠️ **Estrutura JSON Variável:**
- Completed Rides: 16 campos (cidade em [15])
- Cancelled Rides: 18 campos (cidade em [17])
- Missed Rides: 9 campos (cidade em [8])

⚠️ **Normalização Necessária:**
- "MATUPA" → "Matupá"
- "PEIXOTO" → "Peixoto de Azevedo"
- "GUARANTA" → "Guarantã do Norte"

✅ **Dados Disponíveis:**
- ✅ engagement_id para rastreamento único
- ✅ Timestamps de rides (start/end time)
- ✅ Valores de corrida (fare)
- ✅ Relacionamento driver-passenger
- ✅ Performance metrics de motoristas

---

**Documento Gerado:** 2025-01-XX  
**Análise por:** GitHub Copilot  
**Validado:** ✅ Estrutura confirmada via queries diretas no PostgreSQL
