# Endpoints da API Driver Personal Details

Este documento descreve os novos endpoints criados para acessar os dados da tabela `driver_personal_details` no PostgreSQL.

## Base URL
```
http://localhost:8000/api/drivers
```

## Endpoints Disponíveis

### 1. Listar Motoristas com Dados Pessoais
```http
GET /api/drivers/personal-details
```

**Parâmetros de Query:**
- `page` (int, opcional): Número da página (padrão: 1)
- `limit` (int, opcional): Itens por página (padrão: 20, máx: 100)
- `city` (string, opcional): Filtrar por cidade
- `driver_id` (string, opcional): Filtrar por ID específico do motorista

**Resposta:**
```json
{
  "drivers": [
    {
      "driver_id": "17207660",
      "name": "João Silva",
      "phone": "+5511999999999",
      "city": "Matupá",
      "total_rides": 15,
      "total_earnings": 450.50,
      "average_rating": 4.8,
      "status": "active",
      "last_activity": "2023-12-15T14:30:00"
    }
  ],
  "total_count": 24,
  "page": 1,
  "limit": 20
}
```

### 2. Detalhes Completos de um Motorista
```http
GET /api/drivers/personal-details/{driver_id}
```

**Resposta:**
```json
{
  "id": 1,
  "driver_id": "17207660",
  "city": "Matupá",
  "personal_data": {
    "name": "João Silva",
    "phone": "+5511999999999",
    "email": "joao@email.com",
    "cpf": "12345678901"
  },
  "rides_history": [...],
  "wallet_transactions": [...],
  "subscription_history": [...],
  "additional_info": {...},
  "extracted_at": "2023-12-15T10:00:00",
  "updated_at": "2023-12-15T10:00:00",
  "extraction_source": "api_scraper",
  "data_hash": "abc123..."
}
```

### 3. Analytics Detalhadas de um Motorista
```http
GET /api/drivers/analytics/{driver_id}
```

**Resposta:**
```json
{
  "driver_id": "17207660",
  "city": "Matupá",
  "personal_data": {...},
  "total_rides": 15,
  "completed_rides": 13,
  "cancelled_rides": 2,
  "completion_rate": 86.67,
  "total_earnings": 450.50,
  "average_ride_value": 34.65,
  "wallet_balance": 120.30,
  "average_rating": 4.8,
  "total_distance": 450.5,
  "total_duration": 720,
  "first_ride_date": "2023-10-01T08:00:00",
  "last_ride_date": "2023-12-15T14:30:00",
  "active_days": 75,
  "current_subscription": {...}
}
```

### 4. Cidades Disponíveis
```http
GET /api/drivers/cities
```

**Resposta:**
```json
[
  "Matupá",
  "Cuiabá", 
  "Várzea Grande"
]
```

### 5. Resumo Geral dos Motoristas
```http
GET /api/drivers/summary
```

**Parâmetros de Query:**
- `city` (string, opcional): Filtrar por cidade

**Resposta:**
```json
{
  "total_drivers": 24,
  "cities_count": 1,
  "total_rides": 342,
  "total_earnings": 12450.30,
  "average_rating": 4.6,
  "active_drivers": 18,
  "cities": ["Matupá"]
}
```

## Estrutura dos Dados

### Personal Data
```json
{
  "name": "Nome do motorista",
  "phone": "Telefone",
  "email": "Email",
  "cpf": "CPF",
  "birth_date": "Data de nascimento",
  "address": {
    "street": "Rua",
    "city": "Cidade",
    "state": "Estado",
    "zip": "CEP"
  }
}
```

### Rides History
```json
[
  {
    "ride_id": "ride_123",
    "date": "2023-12-15T14:30:00",
    "origin": "Endereço de origem",
    "destination": "Endereço de destino",
    "distance": 15.5,
    "duration": 45,
    "fare": 35.50,
    "status": "completed",
    "rating": 4.8
  }
]
```

### Wallet Transactions
```json
[
  {
    "transaction_id": "tx_123",
    "date": "2023-12-15T10:00:00",
    "type": "ride_payment",
    "amount": 35.50,
    "description": "Pagamento corrida #123",
    "balance_after": 120.30
  }
]
```

### Subscription History
```json
[
  {
    "subscription_id": "sub_123",
    "plan_type": "premium",
    "start_date": "2023-10-01",
    "end_date": "2023-12-31",
    "status": "active",
    "price": 29.90
  }
]
```

## Códigos de Erro

- `200`: Sucesso
- `404`: Motorista não encontrado
- `422`: Parâmetros inválidos
- `500`: Erro interno do servidor

## Uso no Frontend

### Exemplo com fetch:
```javascript
// Listar motoristas
const response = await fetch('/api/drivers/personal-details?page=1&limit=10');
const data = await response.json();

// Obter detalhes de um motorista
const driverResponse = await fetch(`/api/drivers/personal-details/${driverId}`);
const driverData = await driverResponse.json();

// Obter analytics
const analyticsResponse = await fetch(`/api/drivers/analytics/${driverId}`);
const analytics = await analyticsResponse.json();
```

### Exemplo com axios:
```javascript
import axios from 'axios';

// Hook personalizado para React
const useDriverPersonalDetails = () => {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const fetchDrivers = async (page = 1, city = null) => {
    setLoading(true);
    try {
      const params = { page, limit: 20 };
      if (city) params.city = city;
      
      const response = await axios.get('/api/drivers/personal-details', { params });
      setDrivers(response.data.drivers);
    } catch (error) {
      console.error('Erro ao buscar motoristas:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return { drivers, loading, fetchDrivers };
};
```

## Notas Técnicas

1. **Paginação**: Todos os endpoints de listagem suportam paginação para melhor performance
2. **Filtros**: Suporte a filtros por cidade e driver_id
3. **JSON Parsing**: Os dados JSON armazenados como string são automaticamente convertidos
4. **Error Handling**: Tratamento robusto de erros com mensagens descritivas
5. **Performance**: Queries otimizadas com índices no database
6. **Segurança**: Validação de parâmetros com Pydantic

## Testing

Para testar os endpoints, execute:
```bash
python test_endpoints.py
```

Este script testará todos os endpoints e verificará se estão funcionando corretamente.
