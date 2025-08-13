# 📊 PLANO DE AÇÃO - Dashboard de Mobilidade Corporativa

## 📋 ANÁLISE DO ESTADO ATUAL

### Estrutura Atual do Projeto
O dashboard atual está estruturado com:

**Frontend (React/Vite):**
- ✅ Componentes modulares bem organizados
- ✅ Sistema de navegação via Sidebar
- ✅ Abas funcionais: Overview, Análises, Drivers, Financeiro, Performance, Metas, etc.
- ✅ Interface moderna com Framer Motion e Tailwind CSS
- ✅ Sistema de importação de dados avançado

**Backend (FastAPI):**
- ✅ API RESTful bem estruturada
- ✅ Modelos de dados (Corridas, Motoristas, Gastos)
- ✅ Sistema de sincronização com Google Sheets
- ✅ Serviços de cache e importação
- ✅ Sistema financeiro com agrupamento de documentos

**Banco de Dados:**
- ✅ Schema PostgreSQL bem definido
- ✅ Tabelas: corridas, motoristas, gastos_empresa, metas
- ✅ Enums para status e tipos de dados

### Problemas Identificados
1. **Falta de estrutura para as 3 abas principais** definidas no planejamento
2. **Ausência de dados de campanhas e metas por cidade**
3. **Falta de KPIs específicos de mobilidade corporativa**
4. **Necessidade de estrutura para análise de créditos**

---

## 🎯 OBJETIVO: IMPLEMENTAR AS 3 ABAS PRINCIPAIS

### **ABA 1: ANÁLISE OPERACIONAL DE CORRIDAS**
### **ABA 2: ANÁLISE FINANCEIRA (MODELO DE CRÉDITOS)**  
### **ABA 3: METAS E PERFORMANCE**

---

## 🚀 PLANO DE AÇÃO DETALHADO

### **FASE 1: REESTRUTURAÇÃO DO BANCO DE DADOS** (2-3 dias)

#### 1.1 Novas Tabelas Necessárias

**Tabela: campanhas**
```sql
CREATE TABLE campanhas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    fase VARCHAR(20) NOT NULL, -- 'Fase 1', 'Fase 2', 'Fase 3'
    cidade VARCHAR(50) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    tipo_campanha VARCHAR(50) NOT NULL, -- 'aquisicao_motoristas', 'aquisicao_corridas'
    meta_quantidade INTEGER NOT NULL,
    orcamento_previsto DECIMAL(10,2) NOT NULL,
    custo_real DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ativa', -- 'ativa', 'finalizada', 'pausada'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tabela: cidades_expansao**
```sql
CREATE TABLE cidades_expansao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL,
    populacao_estimada INTEGER NOT NULL,
    publico_alvo INTEGER NOT NULL, -- 15 a 44 anos
    densidade_demografica DECIMAL(8,2),
    meta_corridas_mes_1 INTEGER NOT NULL,
    meta_corridas_mes_2 INTEGER NOT NULL,
    meta_corridas_mes_3 INTEGER NOT NULL,
    meta_corridas_mes_6 INTEGER NOT NULL,
    meta_receita_media_mensal DECIMAL(10,2),
    data_lancamento DATE,
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tabela: transacoes_creditos**
```sql
CREATE TABLE transacoes_creditos (
    id SERIAL PRIMARY KEY,
    motorista_id INTEGER REFERENCES motoristas(id),
    tipo_transacao VARCHAR(20) NOT NULL, -- 'compra', 'consumo'
    quantidade_creditos INTEGER NOT NULL,
    valor_transacao DECIMAL(10,2) NOT NULL, -- R$ 2,50 por crédito
    data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    corrida_id INTEGER REFERENCES corridas(id), -- apenas para consumo
    descricao VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tabela: metas_mensais**
```sql
CREATE TABLE metas_mensais (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(50) NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    meta_corridas INTEGER NOT NULL,
    meta_receita DECIMAL(10,2),
    meta_penetracao_mercado DECIMAL(5,2), -- percentual
    corridas_realizadas INTEGER DEFAULT 0,
    receita_realizada DECIMAL(10,2) DEFAULT 0,
    penetracao_realizada DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cidade, ano, mes)
);
```

#### 1.2 Atualização de Tabelas Existentes

**Adicionar campos à tabela corridas:**
```sql
ALTER TABLE corridas ADD COLUMN categoria_veiculo VARCHAR(50) DEFAULT 'Básico';
ALTER TABLE corridas ADD COLUMN bairro_origem VARCHAR(100);
ALTER TABLE corridas ADD COLUMN bairro_destino VARCHAR(100);
ALTER TABLE corridas ADD COLUMN tempo_espera INTEGER; -- minutos até aceite
ALTER TABLE corridas ADD COLUMN tempo_chegada INTEGER; -- minutos até embarque
ALTER TABLE corridas ADD COLUMN creditos_consumidos INTEGER DEFAULT 1;
```

**Adicionar campos à tabela motoristas:**
```sql
ALTER TABLE motoristas ADD COLUMN saldo_creditos INTEGER DEFAULT 0;
ALTER TABLE motoristas ADD COLUMN total_creditos_comprados INTEGER DEFAULT 0;
ALTER TABLE motoristas ADD COLUMN total_creditos_consumidos INTEGER DEFAULT 0;
ALTER TABLE motoristas ADD COLUMN ultima_recarga TIMESTAMP;
```

#### 1.3 Scripts de Migração e População Inicial
```bash
# Arquivo: database/migrations/001_add_mobilidade_tables.sql
# Arquivo: database/seeds/001_populate_cidades_expansao.sql
# Arquivo: database/seeds/002_populate_campanhas_iniciais.sql
```

---

### **FASE 2: BACKEND - NOVAS APIs** (3-4 dias)

#### 2.1 Novos Endpoints para Aba 1 (Análise Operacional)

**Arquivo: `backend/app/api/analise_operacional.py`**
```python
@router.get("/overview-operacional")
async def get_overview_operacional(
    periodo: str = "30d",
    cidade: str = None,
    categoria_veiculo: str = None
):
    """
    Retorna KPIs operacionais principais:
    - Total de corridas solicitadas
    - Taxa de conclusão, cancelamento e perda
    - Tempo médio de espera e chegada
    """

@router.get("/analise-cancelamentos")
async def get_analise_cancelamentos(periodo: str = "30d"):
    """
    Retorna análise detalhada de cancelamentos:
    - Quem cancelou (motorista vs passageiro)
    - Principais motivos
    - Distribuição por cidade/horário
    """

@router.get("/mapa-calor-problemas")
async def get_mapa_calor_problemas(periodo: str = "30d"):
    """
    Retorna dados para heatmap de problemas:
    - Áreas com maior concentração de cancelamentos
    - Áreas com maior tempo de espera
    """
```

#### 2.2 Novos Endpoints para Aba 2 (Análise Financeira)

**Arquivo: `backend/app/api/analise_financeira_creditos.py`**
```python
@router.get("/overview-receita-creditos")
async def get_overview_receita_creditos(periodo: str = "30d"):
    """
    Retorna visão geral da receita com créditos:
    - Receita bruta com recargas
    - Total de créditos vendidos
    - Receita média por recarga/motorista
    """

@router.get("/fluxo-creditos")
async def get_fluxo_creditos(periodo: str = "30d"):
    """
    Retorna análise do fluxo de créditos:
    - Créditos vendidos vs consumidos
    - Burn rate
    - Saldo total de créditos na plataforma
    """

@router.get("/grafico-creditos-dual")
async def get_grafico_creditos_dual(periodo: str = "30d"):
    """
    Dados para gráfico de eixo duplo:
    - Barras: Créditos vendidos por dia
    - Linha: Créditos consumidos por dia
    """
```

#### 2.3 Novos Endpoints para Aba 3 (Metas e Performance)

**Arquivo: `backend/app/api/metas_performance.py`**
```python
@router.get("/overview-metas-agregadas")
async def get_overview_metas_agregadas(fase: str = None):
    """
    Retorna visão geral das metas:
    - Motoristas adquiridos vs meta
    - Corridas de lançamento vs meta
    - CAC por motorista e por corrida
    """

@router.get("/penetracao-mercado/{cidade}")
async def get_penetracao_mercado(cidade: str):
    """
    Retorna dados da cidade específica:
    - População e público-alvo
    - Evolução mensal (meta vs realizado)
    - Percentual de penetração atual
    """

@router.get("/tabela-desempenho-campanhas")
async def get_tabela_desempenho_campanhas():
    """
    Retorna tabela detalhada de todas as campanhas:
    - Por fase, cidade, tipo de meta
    - Atingimento percentual
    - Variação de custo
    """
```

---

### **FASE 3: FRONTEND - NOVAS ABAS** (4-5 dias)

#### 3.1 Reestruturação da Navegação

**Arquivo: `frontend/src/components/Sidebar.jsx`**
```javascript
const menuItems = [
  { id: 'overview', label: 'Visão Geral', icon: Home },
  
  // GRUPO: ANÁLISES OPERACIONAIS
  { id: 'operacional', label: 'Análise Operacional', icon: TrendingUp },
  { id: 'financeiro-creditos', label: 'Análise Financeira', icon: DollarSign },
  { id: 'metas-performance', label: 'Metas & Performance', icon: Target },
  
  // GRUPO: FERRAMENTAS
  { id: 'drivers', label: 'Motoristas', icon: Users },
  { id: 'importacao', label: 'Importação', icon: Settings },
  { id: 'configuracao', label: 'Configurações', icon: Settings }
]
```

#### 3.2 Componente: Análise Operacional

**Arquivo: `frontend/src/components/AnaliseOperacional.jsx`**
```javascript
export function AnaliseOperacional() {
  return (
    <div className="space-y-6">
      {/* Seção 1: KPIs Principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard 
          title="Taxa de Conclusão" 
          value="87.3%" 
          trend="up" 
          change="+2.1%" 
        />
        <KPICard 
          title="Taxa de Cancelamento" 
          value="9.2%" 
          trend="down" 
          change="-1.5%" 
        />
        <KPICard 
          title="Taxa de Perda" 
          value="3.5%" 
          trend="down" 
          change="-0.6%" 
        />
        <KPICard 
          title="Tempo Médio Espera" 
          value="4.2 min" 
          trend="down" 
          change="-0.8 min" 
        />
      </div>

      {/* Seção 2: Gráficos de Tendência */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Evolução das Taxas Operacionais</CardTitle>
          </CardHeader>
          <CardContent>
            <GraficoLinhasTaxas />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Análise de Cancelamentos</CardTitle>
          </CardHeader>
          <CardContent>
            <GraficoPizzaCancelamentos />
          </CardContent>
        </Card>
      </div>

      {/* Seção 3: Mapa de Calor */}
      <Card>
        <CardHeader>
          <CardTitle>Mapa de Problemas por Região</CardTitle>
        </CardHeader>
        <CardContent>
          <MapaCalorProblemas />
        </CardContent>
      </Card>
    </div>
  )
}
```

#### 3.3 Componente: Análise Financeira (Créditos)

**Arquivo: `frontend/src/components/AnaliseFinanceiraCreditos.jsx`**
```javascript
export function AnaliseFinanceiraCreditos() {
  return (
    <div className="space-y-6">
      {/* Seção 1: Visão Geral de Receita */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard 
          title="Receita Bruta" 
          value="R$ 18.750" 
          subtitle="Com Recargas" 
        />
        <KPICard 
          title="Créditos Vendidos" 
          value="7.500" 
          subtitle="Total no Período" 
        />
        <KPICard 
          title="Receita Média/Recarga" 
          value="R$ 62,50" 
          subtitle="Por Transação" 
        />
        <KPICard 
          title="Receita Média/Motorista" 
          value="R$ 125" 
          subtitle="Por Motorista Ativo" 
        />
      </div>

      {/* Seção 2: Gráfico Principal - Fluxo de Créditos */}
      <Card>
        <CardHeader>
          <CardTitle>Fluxo de Créditos (Vendidos vs Consumidos)</CardTitle>
          <CardDescription>
            Acompanhe a dinâmica entre vendas e consumo de créditos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <GraficoEixoDuplo />
        </CardContent>
      </Card>

      {/* Seção 3: Métricas de Consumo */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Burn Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <GraficoMedidor value={89} label="89% dos créditos vendidos foram consumidos" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Saldo Total na Plataforma</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">2.350 créditos</div>
            <div className="text-sm text-gray-500">R$ 5.875 em valor</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Motoristas (Recargas)</CardTitle>
          </CardHeader>
          <CardContent>
            <TabelaTopMotoristas />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

#### 3.4 Componente: Metas e Performance

**Arquivo: `frontend/src/components/MetasPerformance.jsx`**
```javascript
export function MetasPerformance() {
  const [cidadeSelecionada, setCidadeSelecionada] = useState('todos')
  const [faseSelecionada, setFaseSelecionada] = useState('todas')

  return (
    <div className="space-y-6">
      {/* Filtros */}
      <div className="flex gap-4">
        <Select value={faseSelecionada} onValueChange={setFaseSelecionada}>
          <SelectTrigger>
            <SelectValue placeholder="Selecione a Fase" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="todas">Todas as Fases</SelectItem>
            <SelectItem value="fase1">Fase 1</SelectItem>
            <SelectItem value="fase2">Fase 2</SelectItem>
            <SelectItem value="fase3">Fase 3</SelectItem>
          </SelectContent>
        </Select>

        <Select value={cidadeSelecionada} onValueChange={setCidadeSelecionada}>
          <SelectTrigger>
            <SelectValue placeholder="Selecione a Cidade" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="todos">Todas as Cidades</SelectItem>
            <SelectItem value="monte-verde">Monte Verde</SelectItem>
            <SelectItem value="colider">Colíder</SelectItem>
            <SelectItem value="alta-floresta">Alta Floresta</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Seção 1: Metas Agregadas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetaCard 
          titulo="Motoristas Adquiridos"
          realizado={23}
          meta={30}
          formato="numero"
        />
        <MetaCard 
          titulo="Corridas de Lançamento"
          realizado={187}
          meta={250}
          formato="numero"
        />
        <MetaCard 
          titulo="CAC - Motorista"
          realizado="R$ 142"
          meta="R$ 150"
          formato="moeda"
        />
        <MetaCard 
          titulo="CAC - Corrida"
          realizado="R$ 18,50"
          meta="R$ 25,00"
          formato="moeda"
        />
      </div>

      {/* Seção 2: Análise por Cidade (quando selecionada) */}
      {cidadeSelecionada !== 'todos' && (
        <Card>
          <CardHeader>
            <CardTitle>Penetração de Mercado - {cidadeSelecionada}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-2">Dados da Cidade</h4>
                <div className="space-y-1 text-sm">
                  <div>População Estimada: 32.010</div>
                  <div>Público-Alvo (15-44 anos): 14.045</div>
                  <div>Penetração Atual: 1.8%</div>
                </div>
              </div>
              <div>
                <GraficoEvolucaoMensal cidade={cidadeSelecionada} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Seção 3: Tabela Detalhada */}
      <Card>
        <CardHeader>
          <CardTitle>Desempenho Detalhado de Campanhas</CardTitle>
        </CardHeader>
        <CardContent>
          <TabelaDesempenhoCampanhas 
            fase={faseSelecionada}
            cidade={cidadeSelecionada}
          />
        </CardContent>
      </Card>
    </div>
  )
}
```

---

### **FASE 4: POPULAÇÃO DE DADOS INICIAIS** (1-2 dias)

#### 4.1 Scripts de População

**Arquivo: `backend/scripts/populate_initial_data.py`**
```python
async def populate_cidades_expansao():
    """Popula dados iniciais das cidades conforme planejamento"""
    cidades_data = [
        {
            "nome": "Monte Verde",
            "populacao_estimada": 15420,
            "publico_alvo": 6980,
            "meta_corridas_mes_1": 35,
            "meta_corridas_mes_2": 70,
            "meta_corridas_mes_3": 140,
            "meta_corridas_mes_6": 770,
            "meta_receita_media_mensal": 1925.00
        },
        {
            "nome": "Colíder", 
            "populacao_estimada": 32010,
            "publico_alvo": 14045,
            "meta_corridas_mes_1": 70,
            "meta_corridas_mes_2": 140,
            "meta_corridas_mes_3": 280,
            "meta_corridas_mes_6": 1544,
            "meta_receita_media_mensal": 3860.00
        }
        # ... outras cidades
    ]

async def populate_campanhas_iniciais():
    """Popula campanhas das fases 1, 2 e 3"""
    campanhas_data = [
        {
            "nome": "Fase 1 - Aquisição Motoristas Monte Verde",
            "fase": "Fase 1",
            "cidade": "Monte Verde", 
            "tipo_campanha": "aquisicao_motoristas",
            "meta_quantidade": 4,
            "orcamento_previsto": 580.00
        }
        # ... outras campanhas
    ]
```

#### 4.2 Dados Mock para Demonstração

**Arquivo: `backend/scripts/generate_mock_data.py`**
```python
async def generate_creditos_transactions():
    """Gera transações de créditos mock para demonstração"""
    
async def generate_corridas_operacionais():
    """Gera dados de corridas com status e tempos para análise operacional"""
```

---

### **FASE 5: TESTES E REFINAMENTOS** (2-3 dias)

#### 5.1 Testes de Integração
- Verificar funcionamento das 3 novas abas
- Testar filtros e navegação
- Validar cálculos de KPIs e métricas

#### 5.2 Ajustes de UX/UI
- Responsividade em dispositivos móveis
- Otimização de performance dos gráficos
- Refinamento visual das abas

#### 5.3 Documentação
- Atualizar README com novas funcionalidades
- Documentar APIs criadas
- Guia de uso das novas abas

---

## 📅 CRONOGRAMA RESUMIDO

| Fase | Atividade | Duração | Responsável |
|------|-----------|---------|-------------|
| 1 | Reestruturação BD | 2-3 dias | Backend Dev |
| 2 | Novas APIs | 3-4 dias | Backend Dev |
| 3 | Novas Abas Frontend | 4-5 dias | Frontend Dev |
| 4 | População Dados | 1-2 dias | Backend Dev |
| 5 | Testes/Refinamentos | 2-3 dias | Full Team |
| **TOTAL** | **12-17 dias** | **~3 semanas** | |

---

## 🎯 RESULTADO ESPERADO

Ao final da implementação, teremos um dashboard completo de mobilidade corporativa com:

✅ **Aba 1 - Análise Operacional**: Taxa de conclusão, análise de cancelamentos, tempos de espera, mapa de problemas

✅ **Aba 2 - Análise Financeira**: Receita com créditos, fluxo de compra/consumo, burn rate, saldo na plataforma

✅ **Aba 3 - Metas & Performance**: Acompanhamento de campanhas, penetração de mercado, CAC, evolução por cidade

✅ **Sistema Escalável**: Estrutura preparada para adicionar novas cidades e campanhas facilmente

✅ **Base de Dados Robusta**: Schema completo para suportar análises avançadas de mobilidade urbana

---

## 🚀 PRÓXIMOS PASSOS

1. **Aprovação do Plano**: Review e ajustes necessários
2. **Setup do Ambiente**: Preparação do banco para novas tabelas  
3. **Início da Fase 1**: Criação das migrações de banco de dados
4. **Desenvolvimento Iterativo**: Implementação fase por fase com testes contínuos

---

**Este plano transform o dashboard atual em uma ferramenta completa de análise de mobilidade corporativa, seguindo exatamente as especificações do planejamento estratégico fornecido.**
