# 🎯 PLANO DE AÇÃO ATUALIZADO - Metas por Cidade

**Data Atualização:** 2025-01-XX (Pós-Sprint 1)  
**Status:** ✅ Sprint 1 Completa | 🔄 Sprint 2 Revisada com Dados Reais  
**Referência:** ESTRUTURA_REAL_DADOS_METAS.md

---

## 📊 CONTEXTO ATUALIZADO

### ✅ Sprint 1 - Resultados
- Auditoria completa realizada (AUDIT_METAS_CIDADES.md)
- Código obsoleto removido (4 arquivos)
- 23 testes criados (15 backend + 8 frontend)
- Banco de dados analisado: metas_progressivas com 0% dados reais
- **DESCOBERTA CRÍTICA:** Estrutura real dos dados mapeada

### 🎯 Dados Reais Identificados

**Tabelas Operacionais:**
1. **rides_data** (1.044 registros)
   - JSON com cidade no índice [15] (Completed), [17] (Cancelled), [8] (Missed)
   - Tipos: Completed Rides (430), Ongoing (486), Cancelled (52), Missed (47), Scheduled (26)
   
2. **driver_personal_details** (42 registros)
   - Campo `city` direto
   - `rides_history` com engagement_id, fare, distance
   
3. **drivers_data** (3.792 registros)
   - Métricas de performance em `additional_data`
   - Success Rides, Active Days, Online Hours
   
4. **passenger_personal_details** (271 registros)
   - Campo `city` direto
   - `rides_history` com engagement_id, fare

**Cidades Encontradas:**
- MATUPA (Matupá)
- PEIXOTO (Peixoto de Azevedo)
- Nova Monte Verde
- Guarantã do Norte
- Nova Bandeirantes

---

## 🚀 SPRINT 2 - INTEGRAÇÃO COM DADOS REAIS (ATUALIZADA)

**Objetivo:** Extrair dados reais de corridas, motoristas e passageiros por cidade e popular `metas_progressivas`

**Prazo:** 5 dias úteis  
**Complexidade:** ⚠️ ALTA (extração JSON + normalização de cidades)

---

### 📋 Task 2.1: Script de Extração de Dados Reais

**Arquivo:** `populate_metas_from_real_data.py`

**Funcionalidades:**

#### 1. Extração de Corridas por Cidade
```python
def extrair_corridas_por_cidade(periodo_meses: int, data_referencia: str):
    """
    Extrai corridas completadas agrupadas por cidade
    
    SQL:
        SELECT 
            CASE 
                WHEN ride_data::json->'newRecords'->0->>15 = 'MATUPA' THEN 'Matupá'
                WHEN ride_data::json->'newRecords'->0->>15 = 'PEIXOTO' THEN 'Peixoto de Azevedo'
                -- ... normalização
            END as cidade,
            COUNT(*) as total_corridas,
            SUM(CAST(ride_data::json->'newRecords'->0->>12 AS NUMERIC)) as receita_total,
            COUNT(DISTINCT ride_data::json->'newRecords'->0->>1) as motoristas_unicos
        FROM rides_data
        WHERE table_name = 'Completed Rides'
            AND CAST(ride_data::json->'newRecords'->0->>6 AS TIMESTAMP) >= (data_referencia - periodo_meses MONTH)
            AND CAST(ride_data::json->'newRecords'->0->>6 AS TIMESTAMP) < data_referencia
        GROUP BY cidade;
    
    Retorna:
        {
            'Matupá': {'corridas': 150, 'receita': 2500.00, 'motoristas': 12},
            'Peixoto de Azevedo': {...}
        }
    """
```

#### 2. Contagem de Motoristas Ativos
```python
def contar_motoristas_ativos_por_cidade(periodo_meses: int):
    """
    Motoristas que fizeram pelo menos 1 corrida no período
    
    SQL:
        SELECT 
            dpd.city,
            COUNT(DISTINCT dpd.driver_id) as motoristas_ativos
        FROM driver_personal_details dpd
        WHERE dpd.city IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM jsonb_array_elements(dpd.rides_history) ride
                WHERE CAST(ride->>'drop_time' AS TIMESTAMP) >= (now() - periodo_meses MONTH)
            )
        GROUP BY dpd.city;
    """
```

#### 3. Normalização de Cidades
```python
CITY_NORMALIZATION = {
    'MATUPA': 'Matupá',
    'PEIXOTO': 'Peixoto de Azevedo',
    'GUARANTA': 'Guarantã do Norte',
    'NOVA MONTE VERDE': 'Nova Monte Verde',
    'NOVA BANDEIRANTES': 'Nova Bandeirantes'
}

def normalizar_cidade(cidade_raw: str) -> str:
    """Normaliza nome da cidade para padrão consistente"""
    return CITY_NORMALIZATION.get(cidade_raw.upper(), cidade_raw)
```

#### 4. Atualização de metas_progressivas
```python
def popular_metas_progressivas(cidade_id: int, periodo_meses: int, data_ref: str):
    """
    Popula campos resultado_* com dados reais
    
    UPDATE metas_progressivas
    SET 
        resultado_corridas = (dados_extraidos['corridas']),
        resultado_receita = (dados_extraidos['receita']),
        resultado_motoristas = (dados_extraidos['motoristas']),
        resultado_passageiros = (contagem de passageiros únicos),
        resultado_aceitacao = (
            SELECT (Success Rides / Requests Received) * 100
            FROM drivers_data 
            WHERE driver_id IN (motoristas da cidade)
        ),
        resultado_cancelamento = (
            SELECT COUNT(*) FROM rides_data 
            WHERE table_name = 'Cancelled Rides' AND cidade = ...
        ) / total_corridas * 100,
        resultado_avaliacao = (
            SELECT AVG(rating) FROM driver_personal_details.rides_history
            WHERE city = ...
        )
    WHERE cidade_id = cidade_id
        AND periodo_meses = periodo_meses;
    """
```

**Critérios de Aceitação:**
- [x] Script conecta no banco PostgreSQL
- [ ] Extrai corridas dos últimos 2, 3, 6, 12 meses por cidade
- [ ] Normaliza nomes de cidades (MATUPA → Matupá)
- [ ] Calcula métricas: corridas, receita, motoristas ativos, passageiros, taxa aceitação/cancelamento, avaliação média
- [ ] Atualiza `metas_progressivas.resultado_*` para cada cidade e período
- [ ] Log de execução: quantos registros atualizados
- [ ] Tratamento de erros: JSON malformado, valores NULL

**Estimativa:** 2 dias

---

### 📋 Task 2.2: Endpoint Consolidado com Dados Reais

**Arquivo:** `backend/services/metas_estrategicas_service.py`

**Nova Função:**
```python
async def get_metas_consolidado_real_time(cidade_id: int, periodo_meses: int = None):
    """
    Retorna metas + dados reais em tempo real
    
    Query:
        WITH corridas_cidade AS (
            SELECT 
                normalizar_cidade(ride_data::json->'newRecords'->0->>15) as cidade,
                CAST(ride_data::json->'newRecords'->0->>12 AS NUMERIC) as valor,
                CAST(ride_data::json->'newRecords'->0->>6 AS TIMESTAMP) as data_hora
            FROM rides_data
            WHERE table_name = 'Completed Rides'
        ),
        metas AS (
            SELECT * FROM metas_progressivas
            WHERE cidade_id = :cidade_id
                AND (periodo_meses = :periodo OR :periodo IS NULL)
        )
        SELECT 
            m.*,
            COUNT(cc.*) as corridas_real_time,
            SUM(cc.valor) as receita_real_time,
            (m.resultado_corridas / m.meta_mes * 100) as percentual_atingido
        FROM metas m
        LEFT JOIN corridas_cidade cc ON cc.cidade = (
            SELECT nome FROM cidades WHERE id = m.cidade_id
        )
        GROUP BY m.id;
    
    Retorna:
        {
            "cidade_id": 3,
            "cidade_nome": "Matupá",
            "periodo_meses": 2,
            "metas": {
                "corridas": 150,
                "receita": 2500.00,
                "motoristas": 12
            },
            "resultados": {
                "corridas": 145,
                "receita": 2380.50,
                "motoristas": 11
            },
            "percentual_atingido": {
                "corridas": 96.67,
                "receita": 95.22,
                "motoristas": 91.67
            },
            "real_time": {
                "corridas_hoje": 8,
                "receita_hoje": 150.00
            }
        }
    """
```

**Rotas:**
```python
@router.get("/metas-estrategicas/consolidado/{cidade_id}")
async def get_consolidado(
    cidade_id: int,
    periodo_meses: int = Query(None, description="2, 3, 6 ou 12 meses")
):
    """Retorna metas + resultados reais + progresso"""
    return await metas_service.get_metas_consolidado_real_time(cidade_id, periodo_meses)

@router.get("/metas-estrategicas/cidades/resumo")
async def get_resumo_todas_cidades():
    """
    Resumo de todas as cidades com metas ativas
    
    Retorna:
        [
            {
                "cidade_id": 3,
                "cidade_nome": "Matupá",
                "metas_ativas": 4,  # 2, 3, 6, 12 meses
                "progresso_geral": 94.5,  # média de todos os períodos
                "ultima_atualizacao": "2025-10-08T22:00:00"
            },
            ...
        ]
    """
```

**Critérios de Aceitação:**
- [ ] GET `/metas-estrategicas/consolidado/{cidade_id}` retorna dados reais
- [ ] Parâmetro `periodo_meses` filtra período específico
- [ ] Calcula percentual de atingimento automaticamente
- [ ] Dados em tempo real (query direto em rides_data)
- [ ] Endpoint `/cidades/resumo` lista todas as cidades
- [ ] Tratamento de cidade sem metas configuradas (retorna 404 ou estrutura vazia)
- [ ] Testes de integração para ambas as rotas

**Estimativa:** 1.5 dias

---

### 📋 Task 2.3: Integração Frontend

**Arquivo:** `frontend/src/components/MetasEstrategicas/TabelaMetasCidades.jsx`

**Alterações:**

#### 1. Remover Math.random()
```jsx
// ANTES (linha 48):
const realizado = Math.round(meta_mes * (1 + (Math.random() * 0.4 - 0.2)));

// DEPOIS:
const realizado = metasData[cidade.id]?.[periodo]?.resultado_corridas || 0;
const receita_realizada = metasData[cidade.id]?.[periodo]?.resultado_receita || 0;
```

#### 2. Fetch de Dados Reais
```jsx
const fetchMetasConsolidado = async () => {
    try {
        const response = await axios.get('/api/metas-estrategicas/cidades/resumo');
        const cidadesComMetas = response.data;
        
        // Para cada cidade, buscar detalhes por período
        const metasDetalhadas = {};
        for (const cidade of cidadesComMetas) {
            const detalhes = await axios.get(`/api/metas-estrategicas/consolidado/${cidade.cidade_id}`);
            metasDetalhadas[cidade.cidade_id] = {
                2: detalhes.data.find(m => m.periodo_meses === 2),
                3: detalhes.data.find(m => m.periodo_meses === 3),
                6: detalhes.data.find(m => m.periodo_meses === 6),
                12: detalhes.data.find(m => m.periodo_meses === 12)
            };
        }
        
        setMetasData(metasDetalhadas);
    } catch (error) {
        console.error('Erro ao buscar metas:', error);
        setError('Falha ao carregar dados de metas');
    }
};
```

#### 3. Exibição de Percentuais
```jsx
const percentualAtingido = (resultado, meta) => {
    if (!meta || meta === 0) return 0;
    return ((resultado / meta) * 100).toFixed(1);
};

// Na renderização:
<TableCell>
    {resultado_corridas} / {meta_corridas}
    <Typography variant="caption" display="block" color={
        percentual >= 100 ? 'success.main' : 
        percentual >= 80 ? 'warning.main' : 
        'error.main'
    }>
        ({percentual}%)
    </Typography>
</TableCell>
```

**Critérios de Aceitação:**
- [ ] Math.random() removido completamente
- [ ] Dados vêm de `/api/metas-estrategicas/consolidado/{cidade_id}`
- [ ] Exibe percentual de atingimento por métrica
- [ ] Cores indicativas: verde (≥100%), amarelo (80-99%), vermelho (<80%)
- [ ] Loading state durante fetch
- [ ] Mensagem de erro se API falhar
- [ ] Auto-refresh a cada 5 minutos (opcional)

**Estimativa:** 1 dia

---

### 📋 Task 2.4: Testes e Validação

#### Testes Backend
```python
# tests/test_populate_metas.py
def test_extrair_corridas_matupa():
    """Testa extração de corridas para Matupá"""
    corridas = extrair_corridas_por_cidade(2, '2025-10-01')
    assert 'Matupá' in corridas
    assert corridas['Matupá']['corridas'] > 0

def test_normalizacao_cidades():
    """Testa normalização MATUPA → Matupá"""
    assert normalizar_cidade('MATUPA') == 'Matupá'
    assert normalizar_cidade('PEIXOTO') == 'Peixoto de Azevedo'

# tests/test_metas_consolidado_api.py
async def test_endpoint_consolidado():
    """Testa endpoint de metas consolidado"""
    response = await client.get("/api/metas-estrategicas/consolidado/3")
    assert response.status_code == 200
    assert 'resultados' in response.json()
    assert response.json()['resultados']['corridas'] >= 0
```

#### Testes Frontend
```jsx
// tests/unit/TabelaMetasCidades.test.jsx
test('não deve usar Math.random()', () => {
    const { container } = render(<TabelaMetasCidades />);
    const code = container.innerHTML;
    expect(code).not.toContain('Math.random');
});

test('exibe dados reais do backend', async () => {
    mock.onGet('/api/metas-estrategicas/cidades/resumo').reply(200, mockCidades);
    const { getByText } = render(<TabelaMetasCidades />);
    await waitFor(() => {
        expect(getByText(/145 \/ 150/)).toBeInTheDocument(); // resultado / meta
    });
});
```

**Critérios de Aceitação:**
- [ ] Todos os testes de extração passam
- [ ] Testes de normalização cobrem todas as cidades
- [ ] Testes de API validam estrutura de resposta
- [ ] Testes de frontend verificam ausência de Math.random()
- [ ] Teste de integração end-to-end (popular banco → buscar API → exibir frontend)

**Estimativa:** 0.5 dias

---

## 📊 RESUMO SPRINT 2 ATUALIZADA

| Task | Arquivo | Estimativa | Status |
|------|---------|-----------|--------|
| 2.1 | `populate_metas_from_real_data.py` | 2 dias | 🔜 |
| 2.2 | `metas_estrategicas_service.py` + rotas | 1.5 dias | 🔜 |
| 2.3 | `TabelaMetasCidades.jsx` | 1 dia | 🔜 |
| 2.4 | Testes (backend + frontend) | 0.5 dias | 🔜 |

**Total:** 5 dias úteis  
**Início Previsto:** Após aprovação do plano  
**Complexidade:** ⚠️ ALTA (extração JSON + joins complexos)

---

## 🚧 DESAFIOS TÉCNICOS IDENTIFICADOS

### 1. Extração JSON com Índices Variáveis
**Problema:** Completed Rides usa índice [15], Cancelled usa [17], Missed usa [8]  
**Solução:**
```sql
CASE 
    WHEN table_name = 'Completed Rides' THEN ride_data::json->'newRecords'->0->>15
    WHEN table_name = 'Cancelled Rides' THEN ride_data::json->'newRecords'->0->>17
    WHEN table_name = 'Missed Rides' THEN ride_data::json->'newRecords'->0->>8
END AS cidade
```

### 2. Normalização de Cidades
**Problema:** "MATUPA", "Matupá", "matupa" são a mesma cidade  
**Solução:** Dicionário de normalização + UPPER() em queries

### 3. Performance de Queries JSON
**Problema:** Parsing JSON em cada query pode ser lento  
**Solução:** 
- Criar índices: `CREATE INDEX idx_rides_table_name ON rides_data(table_name);`
- Cache de resultados no backend (Redis ou in-memory)
- Considerar desnormalização futura (criar tabela `rides_normalized`)

### 4. Dados Incompletos
**Problema:** Nem todas as corridas têm cidade preenchida  
**Solução:** Tentar extrair de pickup_location/drop_location, senão marcar como "NÃO IDENTIFICADA"

---

## 📈 MÉTRICAS DE SUCESSO - SPRINT 2

| Métrica | Meta | Como Medir |
|---------|------|------------|
| **Cobertura de Dados** | 100% das cidades com corridas têm metas | Query: `SELECT COUNT(DISTINCT city) FROM rides_data` vs `metas_progressivas` |
| **Acurácia** | 0% de Math.random() no código | Grep "Math.random" retorna vazio |
| **Performance API** | < 1s para endpoint consolidado | Teste de carga com 10 requisições simultâneas |
| **Atualização** | `resultado_*` atualizado em tempo real | Verificar que dados mudam ao adicionar nova corrida |

---

## 🎯 PRÓXIMAS SPRINTS (Preview)

### Sprint 3: Dashboard Executivo - Gráficos
- Task 3.1: Gráfico de barras (Metas vs Realizado)
- Task 3.2: Gráfico de linha (Evolução temporal)
- Task 3.3: Cards de KPIs principais

### Sprint 4: Filtros e Exportação
- Task 4.1: Filtro por cidade
- Task 4.2: Filtro por período
- Task 4.3: Exportar para Excel/PDF

### Sprint 5: Notificações e Alertas
- Task 5.1: Alerta quando meta < 80%
- Task 5.2: Email semanal para gestores

### Sprint 6: Refinamentos Finais
- Task 6.1: Otimização de performance
- Task 6.2: Documentação de usuário
- Task 6.3: Deploy em produção

---

## ✅ CRITÉRIOS DE CONCLUSÃO - SPRINT 2

- [ ] Script `populate_metas_from_real_data.py` executado com sucesso para todas as cidades
- [ ] Endpoint `/metas-estrategicas/consolidado/{cidade_id}` retorna dados reais
- [ ] Frontend exibe dados do backend (0% Math.random())
- [ ] 100% dos testes passam (backend + frontend)
- [ ] Documentação atualizada (README com instruções de execução do script)
- [ ] Code review aprovado
- [ ] Deploy em ambiente de staging validado

---

**Documento Atualizado:** 2025-01-XX  
**Autor:** GitHub Copilot  
**Baseado em:** ESTRUTURA_REAL_DADOS_METAS.md  
**Aprovação Necessária:** ✅ Usuário deve validar antes de iniciar Sprint 2
