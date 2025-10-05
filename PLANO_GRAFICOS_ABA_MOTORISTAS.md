# 📊 PLANO DE GRÁFICOS - ABA MOTORISTAS

## 🔍 Dados Disponíveis (Análise Real do Banco)

### Tabela `drivers_data` - **3.234 registros**

#### Campos Principais:
- `driver_id` - ID único do motorista
- `name` - Nome do motorista
- `email` - Email
- `mobile` - Telefone
- `data_type` - Tipo de dado: `performance`, `enrollment`, `active`, `leaderboard`, `deactive`
- `page_source` - Origem: `Driver Performance`, `Drivers Enrollment`, `Active Drivers`, `Leaderboard`, `Deactive Drivers`
- `additional_data` (JSONB) - **22 campos únicos**
- `scraped_at` - Data de coleta

#### Campos em `additional_data` (mais relevantes):
- ✅ **City** - Cidade do motorista (8/10 registros)
- ✅ **Driver Name** - Nome (10/10)
- ✅ **Driver Ratings** - Avaliação (6/10)
- ✅ **Rides in Last 30 Days** - Corridas últimos 30 dias (6/10)
- ✅ **Rides in Last 7 Days** - Corridas últimos 7 dias (6/10)
- ✅ **Status** - Status do motorista (6/10)
- ✅ **Last Ride** - Última corrida (6/10)
- ✅ **Last Login** - Último login (6/10)
- ✅ **Registered On** - Data de cadastro (8/10)
- ✅ **Vehicle Number** - Placa do veículo (6/10)
- ✅ **Franchise Name** - Franquia (6/10)
- ✅ **OTP** - Código (6/10)

#### Métricas de Performance encontradas:
- `success_rides` - 48 valores
- `cancelled_rides` - 288 valores
- `cancellation_rate` - 5 valores
- `online_hours` - 48 valores

---

## 🎨 GRÁFICOS PROPOSTOS (Ordem de Prioridade)

### 1. 📍 **Distribuição de Motoristas por Cidade** ⭐⭐⭐
- **Tipo:** Gráfico de Pizza ou Barras
- **Dados:** `additional_data->>'City'`
- **Query:**
```sql
SELECT 
    additional_data->>'City' as cidade,
    COUNT(DISTINCT driver_id) as total_motoristas
FROM drivers_data
WHERE additional_data->>'City' IS NOT NULL
    AND data_type = 'active'
GROUP BY additional_data->>'City'
ORDER BY total_motoristas DESC;
```
- **Endpoint:** `GET /api/drivers/analytics/by-city`
- **Componente:** `<PieChart>` ou `<BarChart>`

---

### 2. 🏆 **Top 10 Motoristas Mais Ativos** ⭐⭐⭐
- **Tipo:** Ranking com Barras Horizontais
- **Dados:** `additional_data->>'Rides in Last 30 Days'`
- **Query:**
```sql
SELECT 
    name,
    additional_data->>'City' as cidade,
    COALESCE((additional_data->>'Rides in Last 30 Days')::int, 0) as corridas_30d,
    additional_data->>'Driver Ratings' as avaliacao
FROM drivers_data
WHERE additional_data->>'Rides in Last 30 Days' IS NOT NULL
    AND data_type IN ('active', 'performance')
ORDER BY (additional_data->>'Rides in Last 30 Days')::int DESC
LIMIT 10;
```
- **Endpoint:** `GET /api/drivers/analytics/top-performers`
- **Componente:** `<BarChart layout="horizontal">`

---

### 3. ⭐ **Distribuição de Avaliações (Ratings)** ⭐⭐
- **Tipo:** Histograma ou Gráfico de Barras
- **Dados:** `additional_data->>'Driver Ratings'`
- **Query:**
```sql
SELECT 
    CASE 
        WHEN (additional_data->>'Driver Ratings')::float >= 4.5 THEN '4.5 - 5.0'
        WHEN (additional_data->>'Driver Ratings')::float >= 4.0 THEN '4.0 - 4.5'
        WHEN (additional_data->>'Driver Ratings')::float >= 3.5 THEN '3.5 - 4.0'
        WHEN (additional_data->>'Driver Ratings')::float >= 3.0 THEN '3.0 - 3.5'
        ELSE '< 3.0'
    END as faixa_avaliacao,
    COUNT(*) as quantidade
FROM drivers_data
WHERE additional_data->>'Driver Ratings' IS NOT NULL
    AND additional_data->>'Driver Ratings' != ''
    AND data_type = 'active'
GROUP BY faixa_avaliacao
ORDER BY faixa_avaliacao DESC;
```
- **Endpoint:** `GET /api/drivers/analytics/ratings-distribution`
- **Componente:** `<BarChart>` com cores graduadas

---

### 4. 📅 **Evolução de Cadastros ao Longo do Tempo** ⭐⭐
- **Tipo:** Gráfico de Linha
- **Dados:** `additional_data->>'Registered On'` ou `scraped_at`
- **Query:**
```sql
SELECT 
    DATE(scraped_at) as data,
    COUNT(*) as novos_cadastros,
    COUNT(DISTINCT driver_id) as motoristas_unicos
FROM drivers_data
WHERE data_type = 'enrollment'
GROUP BY DATE(scraped_at)
ORDER BY data DESC
LIMIT 30;
```
- **Endpoint:** `GET /api/drivers/analytics/registrations-timeline`
- **Componente:** `<LineChart>`

---

### 5. 🚗 **Status dos Motoristas (Ativo/Inativo/Deativo)** ⭐⭐⭐
- **Tipo:** Gráfico de Pizza com Cards
- **Dados:** `data_type` + `/api/drivers/status-kpi` (JÁ EXISTE!)
- **Query:**
```sql
SELECT 
    data_type,
    COUNT(DISTINCT driver_id) as total
FROM drivers_data
WHERE data_type IN ('active', 'deactive', 'enrollment')
GROUP BY data_type;
```
- **Endpoint:** ✅ **JÁ IMPLEMENTADO** - `/api/drivers/status-kpi`
- **Componente:** `<PieChart>` + Cards KPI

---

### 6. 📊 **Atividade Recente (7 vs 30 dias)** ⭐⭐
- **Tipo:** Gráfico de Barras Agrupadas
- **Dados:** `Rides in Last 7 Days` vs `Rides in Last 30 Days`
- **Query:**
```sql
SELECT 
    name,
    additional_data->>'City' as cidade,
    COALESCE((additional_data->>'Rides in Last 7 Days')::int, 0) as corridas_7d,
    COALESCE((additional_data->>'Rides in Last 30 Days')::int, 0) as corridas_30d
FROM drivers_data
WHERE data_type IN ('active', 'performance')
    AND additional_data->>'Rides in Last 30 Days' IS NOT NULL
ORDER BY (additional_data->>'Rides in Last 30 Days')::int DESC
LIMIT 15;
```
- **Endpoint:** `GET /api/drivers/analytics/activity-comparison`
- **Componente:** `<BarChart>` com 2 séries

---

### 7. 🕒 **Últimas Atividades (Last Ride / Last Login)** ⭐
- **Tipo:** Timeline / Cards com indicadores
- **Dados:** `Last Ride`, `Last Login`
- **Query:**
```sql
SELECT 
    name,
    additional_data->>'City' as cidade,
    additional_data->>'Last Ride' as ultima_corrida,
    additional_data->>'Last Login' as ultimo_login,
    additional_data->>'Status' as status_atual
FROM drivers_data
WHERE data_type = 'active'
    AND additional_data->>'Last Ride' IS NOT NULL
ORDER BY scraped_at DESC
LIMIT 10;
```
- **Endpoint:** `GET /api/drivers/analytics/recent-activity`
- **Componente:** Cards com Timeline

---

### 8. 🏢 **Motoristas por Franquia** ⭐
- **Tipo:** Gráfico de Barras
- **Dados:** `additional_data->>'Franchise Name'`
- **Query:**
```sql
SELECT 
    additional_data->>'Franchise Name' as franquia,
    COUNT(DISTINCT driver_id) as total_motoristas
FROM drivers_data
WHERE additional_data->>'Franchise Name' IS NOT NULL
    AND additional_data->>'Franchise Name' != ''
    AND data_type = 'active'
GROUP BY additional_data->>'Franchise Name'
ORDER BY total_motoristas DESC;
```
- **Endpoint:** `GET /api/drivers/analytics/by-franchise`
- **Componente:** `<BarChart>`

---

### 9. 📈 **Leaderboard (Ranking Geral)** ⭐⭐
- **Tipo:** Tabela Interativa com Ranking
- **Dados:** `data_type = 'leaderboard'` + `additional_data->>'Rank'`
- **Query:**
```sql
SELECT 
    COALESCE((additional_data->>'Rank')::int, 999) as posicao,
    name,
    additional_data->>'City' as cidade,
    additional_data->>'Rides' as total_corridas,
    additional_data->>'Driver Ratings' as avaliacao
FROM drivers_data
WHERE data_type = 'leaderboard'
ORDER BY (additional_data->>'Rank')::int ASC
LIMIT 20;
```
- **Endpoint:** `GET /api/drivers/analytics/leaderboard`
- **Componente:** Tabela com badges de posição (🥇🥈🥉)

---

### 10. 🔥 **Heatmap de Atividade (por cidade e período)** ⭐
- **Tipo:** Heatmap ou Matriz
- **Dados:** Cruzamento de cidade x período x corridas
- **Query:**
```sql
SELECT 
    additional_data->>'City' as cidade,
    DATE_TRUNC('week', scraped_at) as semana,
    SUM(COALESCE((additional_data->>'Rides in Last 7 Days')::int, 0)) as total_corridas
FROM drivers_data
WHERE additional_data->>'City' IS NOT NULL
    AND data_type IN ('active', 'performance')
GROUP BY additional_data->>'City', DATE_TRUNC('week', scraped_at)
ORDER BY semana DESC, total_corridas DESC;
```
- **Endpoint:** `GET /api/drivers/analytics/heatmap-activity`
- **Componente:** `<ScatterChart>` ou heatmap personalizado

---

## 🎯 IMPLEMENTAÇÃO SUGERIDA

### Fase 1: Básicos (1-2 horas)
1. ✅ Status dos Motoristas (já existe, só usar)
2. 📍 Distribuição por Cidade
3. 🏆 Top 10 Performers

### Fase 2: Avançados (2-3 horas)
4. ⭐ Distribuição de Avaliações
5. 📊 Atividade 7d vs 30d
6. 📅 Evolução de Cadastros

### Fase 3: Premium (1-2 horas)
7. 🏢 Por Franquia
8. 🏆 Leaderboard
9. 🕒 Últimas Atividades

---

## 🛠️ TECNOLOGIAS A USAR

- **Recharts** (já instalado) para todos os gráficos
- **Framer Motion** para animações
- **Lucide React** para ícones
- **Tailwind CSS** para estilização
- Componentes: `<BarChart>`, `<PieChart>`, `<LineChart>`, `<ScatterChart>`, `<RadialBarChart>`

---

## 📝 PRÓXIMOS PASSOS

1. ✅ **Criar endpoints no backend** (`backend/app/api/drivers_analytics.py`)
2. ✅ **Criar componente de gráficos** (`frontend/src/components/DriversAnalytics.jsx`)
3. ✅ **Integrar na aba DriversOverview** (após os KPIs, antes da tabela)
4. ✅ **Testar com dados reais**
5. ✅ **Ajustar responsividade**

---

**Autor:** GitHub Copilot  
**Data:** 05/10/2025  
**Base:** Análise real de 3.234 registros do banco PostgreSQL
