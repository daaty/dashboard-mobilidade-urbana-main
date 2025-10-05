# 🐛 CORREÇÃO: Query de Performance Metrics (Duplicatas)

## Problema Identificado

A query original estava **somando TODOS os registros históricos** da tabela `drivers_data`, incluindo múltiplas capturas do mesmo motorista (scraping a cada 15 minutos).

### Dados Incorretos (ANTES)
```
✗ Corridas Concluídas: 6,507 (400x inflado!)
✗ Rejeitadas: 256
✗ Perdidas: 1,778
```

### Análise do Problema
- **18 motoristas** únicos
- **3,114 registros** total (scraping contínuo)
- **Média de 173 registros** por motorista
- Um único motorista tinha **716 registros** (capturado a cada 15 min por dias)

**Exemplo de Duplicatas**:
```
Driver ID: 16263441
Registros: 205
Scrapes:
  2025-09-30 02:59:28 → Success Rides: 2, Hours: 23
  2025-09-29 23:44:30 → Success Rides: 2, Hours: 22.75
  2025-09-29 23:29:27 → Success Rides: 2, Hours: 22.5
  ... (202 registros a mais do MESMO motorista)
```

A query estava fazendo `SUM()` de **TODOS** esses registros, multiplicando os valores por ~400x!

---

## Solução Implementada

Usar **CTE (Common Table Expression)** com `DISTINCT ON` para pegar apenas o **último registro** de cada motorista:

### Query ANTES (Errada) ❌
```sql
SELECT 
    SUM(CAST(additional_data->>'Success Rides' AS INTEGER)) as total_success_rides,
    SUM(CAST(additional_data->>'Rejected Rides' AS INTEGER)) as total_rejected_rides,
    ...
FROM drivers_data
WHERE data_type = 'performance'
    AND additional_data->>'Success Rides' IS NOT NULL;
```

### Query DEPOIS (Correta) ✅
```sql
WITH latest_records AS (
    SELECT DISTINCT ON (driver_id)
        driver_id,
        additional_data->>'Success Rides' as success_rides,
        additional_data->>'Rejected Rides' as rejected_rides,
        additional_data->>'Missed Rides' as missed_rides,
        additional_data->>'User Cancelled Rides' as user_cancelled,
        additional_data->>'Driver Cancelled Rides' as driver_cancelled,
        additional_data->>'Online Hours' as online_hours
    FROM drivers_data
    WHERE data_type = 'performance'
        AND additional_data->>'Success Rides' IS NOT NULL
    ORDER BY driver_id, scraped_at DESC  -- Último registro
)
SELECT 
    SUM(CAST(success_rides AS INTEGER)) as total_success_rides,
    SUM(CAST(rejected_rides AS INTEGER)) as total_rejected_rides,
    SUM(CAST(missed_rides AS INTEGER)) as total_missed_rides,
    SUM(CAST(user_cancelled AS INTEGER)) as total_user_cancelled,
    SUM(CAST(driver_cancelled AS INTEGER)) as total_driver_cancelled,
    SUM(CAST(online_hours AS FLOAT)) as total_online_hours,
    AVG(CAST(online_hours AS FLOAT)) as avg_online_hours,
    COUNT(DISTINCT driver_id) as total_drivers
FROM latest_records;
```

**Explicação**:
1. **CTE `latest_records`**: Seleciona apenas 1 registro por motorista (o mais recente)
2. **`DISTINCT ON (driver_id)`**: Garante unicidade por motorista
3. **`ORDER BY driver_id, scraped_at DESC`**: Pega o último scrape de cada um
4. **Query principal**: Soma apenas esses 18 registros únicos (não 3,114)

---

## Resultados Corretos (DEPOIS)

```json
{
  "total_success_rides": 16,
  "total_rejected_rides": 0,
  "total_missed_rides": 10,
  "total_user_cancelled": 1,
  "total_driver_cancelled": 2,
  "total_online_hours": 246.0,
  "avg_online_hours": 13.67,
  "total_drivers": 18
}
```

### Comparação
| Métrica | ANTES (Errado) | DEPOIS (Correto) | Diferença |
|---------|----------------|------------------|-----------|
| Corridas Concluídas | 6,507 | 16 | -99.75% ✅ |
| Rejeitadas | 256 | 0 | -100% ✅ |
| Perdidas | 1,778 | 10 | -99.44% ✅ |
| Horas Média | 10.88 | 13.67 | +25.6% |

---

## Distribuição de Horas Online

**Query ANTES (Duplicatas)** ❌:
```sql
SELECT 
    CASE 
        WHEN CAST(additional_data->>'Online Hours' AS FLOAT) >= 8 THEN '8+ horas'
        ...
    END as faixa_horas,
    COUNT(*) as quantidade
FROM drivers_data  -- 3,114 registros!
WHERE data_type = 'performance'
```

**Query DEPOIS (Única por Motorista)** ✅:
```sql
WITH latest_records AS (
    SELECT DISTINCT ON (driver_id)
        driver_id,
        additional_data->>'Online Hours' as online_hours
    FROM drivers_data
    WHERE data_type = 'performance'
    ORDER BY driver_id, scraped_at DESC
)
SELECT 
    CASE 
        WHEN CAST(online_hours AS FLOAT) >= 8 THEN '8+ horas'
        ...
    END as faixa_horas,
    COUNT(*) as quantidade
FROM latest_records  -- Apenas 18 registros únicos
GROUP BY faixa_horas;
```

**Resultado**:
```json
{
  "online_hours_distribution": [
    { "faixa": "8+ horas", "quantidade": 12 },
    { "faixa": "6-8 horas", "quantidade": 1 },
    { "faixa": "4-6 horas", "quantidade": 3 },
    { "faixa": "< 2 horas", "quantidade": 2 }
  ]
}
```

Agora reflete os **18 motoristas únicos**, não os 3,114 registros históricos.

---

## Arquivo Modificado

**Arquivo**: `backend/app/api/drivers_analytics.py`
**Endpoint**: `GET /api/drivers/analytics/performance-metrics`
**Linhas**: ~307-350

---

## Validação

### Teste Manual
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/drivers/analytics/performance-metrics" | Select-Object -ExpandProperty Content
```

**Resposta**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_success_rides": 16,
      "total_rejected_rides": 0,
      "total_missed_rides": 10,
      "total_user_cancelled": 1,
      "total_driver_cancelled": 2,
      "total_online_hours": 246.0,
      "avg_online_hours": 13.67,
      "total_drivers": 18
    },
    "online_hours_distribution": [...]
  }
}
```

✅ **Validado**: Números agora refletem realidade (18 motoristas, não 3,114 registros)

---

## Impacto

### Frontend
O componente `DriversAnalytics.jsx` vai **automaticamente** exibir os valores corretos:

**Cards de Métricas**:
- ✅ Corridas Concluídas: **16** (razoável para 18 motoristas)
- ✅ Rejeitadas: **0**
- ✅ Perdidas: **10**
- ✅ Média Horas: **13.67h**

**Gráfico de Distribuição**:
- ✅ 12 motoristas com 8+ horas
- ✅ 1 motorista com 6-8 horas
- ✅ 3 motoristas com 4-6 horas
- ✅ 2 motoristas com < 2 horas
- **Total: 18 motoristas** ✅

---

## Lições Aprendidas

1. **Sempre verificar duplicatas em tabelas com scraping contínuo**
2. **Usar `DISTINCT ON` ou `ROW_NUMBER()` para dados temporais**
3. **Testar queries com `COUNT(*)` vs `COUNT(DISTINCT driver_id)`**
4. **Validar números com senso comum** (6,507 corridas para 18 motoristas = suspeito!)

---

## Status

✅ **CORRIGIDO** - Endpoint retornando valores reais
✅ **TESTADO** - Query validada no PostgreSQL
✅ **DOCUMENTADO** - Explicação completa da correção

---

*Data da correção: 2025-10-05*
*Arquivo: backend/app/api/drivers_analytics.py*
*Endpoint: GET /api/drivers/analytics/performance-metrics*
