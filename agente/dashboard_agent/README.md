# 🤖 Agente Inteligente para Dashboard de Mobilidade Urbana

## 🎯 Visão Geral

Este é um agente inteligente especializado em análise de dados de mobilidade urbana, construído com o framework **agnai** e equipado com:

- 🧠 **Reasoning avançado** - Análise lógica de dados complexos
- 💾 **Memória persistente** - Aprende com análises anteriores  
- 🛠️ **Ferramentas especializadas** - APIs dedicadas ao dashboard
- 📊 **Business Intelligence** - KPIs e insights estratégicos

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install agno openai python-dotenv requests pandas numpy
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na pasta do agente:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
DASHBOARD_URL=http://localhost:8000
# Usa o mesmo PostgreSQL da API, mas com tabelas específicas do agente
MEMORY_DB_URL=postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db
AGENT_MEMORY_TABLE_PREFIX=agente_
```

### 3. Inicializar memória persistente

```bash
# Criar tabelas de memória no PostgreSQL
python init_memory.py criar

# Verificar se as tabelas foram criadas
python init_memory.py verificar
```

## 🎮 Como Usar

### Uso Básico

```python
from mobility_agent import MobilityDashboardAgent

# Criar agente
agent = MobilityDashboardAgent(
    dashboard_url="http://localhost:8000",
    openai_api_key="sua-chave-aqui"
)

# Análise completa
resultado = agent.analyze_overall_performance()
print(resultado)
```

### Análises Específicas

```python
# Análise financeira
saude_financeira = agent.financial_health_assessment()

# Performance de motoristas  
performance_drivers = agent.driver_performance_analysis()

# Expansão geográfica
expansao = agent.city_expansion_analysis(['São Paulo', 'Rio de Janeiro'])

# Tendências de mercado
tendencias = agent.market_trends_forecast()

# Relatório executivo
relatorio = agent.generate_executive_report()

# Pergunta específica
resposta = agent.interactive_analysis("Qual cidade tem melhor ROI?")
```

## 📊 Capacidades do Agente

### 🔍 Análise de Dados
- Métricas de corridas (concluídas, canceladas, perdidas)
- Performance de motoristas (produtividade, ratings)
- Indicadores financeiros (ROI, gastos, receita)
- Metas estratégicas (progresso, campanhas)

### 🧠 Business Intelligence
- Cálculo de KPIs críticos
- Benchmarks da indústria
- Análise competitiva
- Projeções e forecasting

### 🎯 Recomendações Estratégicas
- Planos de expansão geográfica
- Otimização operacional
- Estratégias de marketing
- Programas de incentivo

## 🛠️ Ferramentas Disponíveis

### Dashboard API Tools
- `get_rides_overview()` - Métricas gerais de corridas
- `get_drivers_overview()` - Dados de motoristas
- `get_financial_overview()` - Indicadores financeiros
- `get_strategic_goals()` - Metas e campanhas
- `compare_cities_performance()` - Análise por cidade

### Business Analysis Tools
- `calculate_business_kpis()` - KPIs automáticos
- `generate_growth_strategy()` - Estratégias de crescimento
- `analyze_market_trends()` - Tendências de mercado
- `competitive_analysis()` - Análise competitiva
- `financial_health_check()` - Saúde financeira

## 📈 Exemplos de Insights

O agente pode gerar insights como:

```
🎯 RESUMO EXECUTIVO
- Total de corridas: 1,247 (↑12% vs mês anterior)
- Taxa de cancelamento: 18% (⚠️ acima do ideal 15%)
- ROI médio campanhas: 165% (✅ acima da meta 150%)

📊 ALERTAS CRÍTICOS
⚠️ Produtividade motoristas em Campinas: 5.2 corridas/dia (abaixo de 6)
⚠️ Taxa cancelamento São Paulo: 22% (muito alta)

🚀 TOP 3 RECOMENDAÇÕES
1. Implementar incentivos para reduzir cancelamentos (-30 dias)
2. Campanha de recrutamento em Campinas (+15 motoristas)
3. Otimizar algoritmo de matching (reduzir tempo espera)
```

## 🔧 Configuração Avançada

### Memória Persistente

Para habilitar memória entre sessões:

```python
agent = MobilityDashboardAgent(
    dashboard_url="http://localhost:8000",
    memory_db_url="postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
)
```

#### Gerenciar Memória

```bash
# Criar tabelas de memória
python init_memory.py criar

# Verificar tabelas existentes
python init_memory.py verificar

# Limpar toda a memória (cuidado!)
python init_memory.py limpar
```

O agente criará automaticamente as tabelas:
- `agente_memory` - Memória geral do agente
- `agente_conversations` - Histórico de conversas
- `agente_insights` - Insights gerados automaticamente

### Customização de Instruções

Você pode modificar as instruções do agente em `_get_agent_instructions()` para comportamentos específicos.

### Adição de Ferramentas

Adicione novas ferramentas no `__init__()`:

```python
self.agent = Agent(
    tools=[
        ReasoningTools(),
        DashboardAPITools(),
        BusinessAnalysisTools(),
        SuaNovaFerramenta()  # Adicione aqui
    ]
)
```

## 🚨 Troubleshooting

### Erro: "Módulo agno não encontrado"
```bash
pip install agno
# ou
git clone https://github.com/phidatahq/agno.git && cd agno && pip install -e .
```

### Erro: "API Key inválida"
Verifique se a `OPENAI_API_KEY` está correta no `.env`

### Erro: "Dashboard não acessível"
Certifique-se que o backend está rodando em `http://localhost:8000`

## 🎯 Roadmap

- [ ] Integração com GPT-4 Turbo
- [ ] Dashboard web para o agente
- [ ] Alertas automáticos por email/Slack
- [ ] Previsões com ML
- [ ] Análise de sentimento (reviews)
- [ ] Integração com BI tools (Tableau, Power BI)

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs de debug
2. Teste as ferramentas individualmente
3. Valide conectividade com APIs
4. Consulte documentação do agno

---

💡 **Dica**: Use o modo interativo para fazer perguntas específicas ao agente e obter insights personalizados para seu negócio!
