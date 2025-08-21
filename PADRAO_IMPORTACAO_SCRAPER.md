# 📋 PADRÃO DE IMPORTAÇÃO E SCRAPER - DRIVERS_DATA

## 🎯 **OBJETIVO**
Garantir que **importação de dados retroativos** e **scraper em tempo real** sigam o mesmo padrão, evitando conflitos no dashboard.

## ✅ **PADRÃO ATUAL DEFINIDO**

### **1. ESTRUTURA DA TABELA `drivers_data`**
```sql
drivers_data (
  id,
  driver_id,
  name,
  email,
  mobile,
  data_type,           -- 🔑 CAMPO CRÍTICO
  page_source,
  additional_data,     -- JSON com dados específicos
  data_hash,
  scraped_at,
  session_info,
  source,
  unique_id
)
```

### **2. TIPOS DE DATA_TYPE**
- ✅ **`active`** - Motoristas ativos (PADRÃO PRINCIPAL)
- ✅ **`enrollment`** - Dados de cadastro
- ✅ **`leaderboard`** - Rankings
- ✅ **`performance`** - Métricas de performance

### **3. API ENDPOINT**
- **URL**: `/api/drivers/analytics`
- **Filtro**: `WHERE data_type = 'active'`
- **Retorna**: 38 motoristas únicos

## 🔧 **ARQUIVOS PADRONIZADOS**

### **Backend API**
- `backend/app/api/import_ridesdata.py` - ✅ Corrigido
- Linha 268: `WHERE data_type = 'active'`
- Linha 249: `'data_type': 'active'`

### **Importação Excel**
- `import_drivers_direct.py` - ✅ Corrigido  
- Linha 99: `'data_type': 'active'`

### **Serviço de Importação**
- `backend/services/import_service.py` - ✅ Corrigido
- Linha 260: `'data_type': 'active'`

## 📊 **ESTRUTURA ADDITIONAL_DATA**

### **Formato Padrão do Scraper**
```json
{
  "otp": "1",
  "city": "16263441", 
  "status": "4.5",
  "headers": ["City", "Driver ID", "Driver Name", ...],
  "raw_row": ["16263441", "Bruno Silva", ...],
  "driver_id": "Bruno Silva",
  "last_ride": "2025040101-04-2025",
  "last_login": "Online",
  "driver_ratings": "Matupá",
  "franchise_name": "brunoribeiro280397@gmail.com",
  "vehicle_number": "View OTP",
  "scraped_timestamp": "2025-08-21T03:59:23.961Z",
  "rides_in_last_7_days": "202508202025-08-20 05:01 PM",
  "rides_in_last_30_days": "202508192025-08-19 08:19 PM"
}
```

### **Formato da Importação Excel**
```json
{
  "raw_data": { /* todos os campos da planilha */ },
  "metrics": {
    "requests_received": 45,
    "success_rides": 32,
    "user_cancelled": 5,
    "driver_cancelled": 3,
    "missed_rides": 5,
    "active_days": 15,
    "online_hours": 120.5
  },
  "profile": {
    "city": "Matupá",
    "vehicle": "HB20",
    "data_date": "2025-08-21"
  }
}
```

## 🚀 **PROCESSO DE IMPORTAÇÃO**

### **Para Dados Retroativos (Excel)**
1. Usar endpoint: `POST /api/import/driversdata`
2. Upload arquivo `.xlsx`
3. Função: `map_excel_to_driver_api()`
4. **Data_type**: `'active'`
5. Estrutura compatível com dashboard

### **Para Scraper (Tempo Real)**
1. Mantém padrão atual
2. **Data_type**: `'active'` para motoristas principais
3. Outros tipos para dados auxiliares
4. Estrutura JSON no `additional_data`

## 🎯 **GARANTIAS DE COMPATIBILIDADE**

### ✅ **API Analytics**
- Busca sempre: `data_type = 'active'`
- Retorna dados unificados
- Frontend processa ambas as estruturas

### ✅ **Frontend (useDriversAnalytics.js)**
- Detecta automaticamente estrutura dos dados
- Processa `data?.metrics` (Excel) ou campos diretos (Scraper)
- Calcula ratings estimados quando necessário
- TOP 5 limitado via `slice(0,5)`

### ✅ **Cálculos Financeiros**
- R$ 2,50 por corrida completada
- 15% de comissão
- Estimativas baseadas em performance

## ⚠️ **REGRAS IMPORTANTES**

1. **NUNCA** mudar `data_type = 'active'` na API
2. **SEMPRE** usar `'active'` nas novas importações
3. **TESTAR** dashboard após qualquer mudança
4. **MANTER** estrutura do `additional_data` compatível
5. **DOCUMENTAR** mudanças neste arquivo

## 🔍 **VERIFICAÇÃO DE FUNCIONAMENTO**

### Teste da API:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/drivers/analytics" | ConvertFrom-Json
```

### Dashboard:
- URL: `http://localhost:3000`
- Deve mostrar 38+ motoristas
- TOP 5 limitado corretamente
- Receitas calculadas em R$ 2,50

## 📈 **STATUS ATUAL**
- ✅ API funcionando (38 registros)
- ✅ Dashboard carregando dados
- ✅ Importação padronizada
- ✅ Scraper compatível
- ✅ Frontend processando corretamente

---

**Última atualização**: 21/08/2025  
**Responsável**: Sistema de Dashboard de Mobilidade Urbana
