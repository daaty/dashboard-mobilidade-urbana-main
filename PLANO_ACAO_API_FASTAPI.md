
# 📋 PLANO DE AÇÃO - INTEGRAÇÃO FASTAPI E ENDPOINTS PARA DASHBOARD

## 🛠️ Boas Práticas e Regras de Execução

- Sempre criar o schema Pydantic (entrada/saída) junto com cada novo endpoint.
- Modularizar: separar rotas, schemas e serviços desde o início.
- Atualizar este documento a cada progresso, marcando o que foi implementado.
- Manter o contrato de dados claro para o frontend.
- Priorizar código limpo, testável e pronto para produção.


## 1. Integração FastAPI ao Projeto

### Estrutura Recomendada
```
backend_fastapi/
  ├── main.py              # Entrypoint FastAPI
  ├── requirements.txt     # Dependências Python
  ├── Dockerfile           # Containerização
  ├── app/                 # Lógica da aplicação
  │     ├── __init__.py
  │     ├── api/           # Rotas/endpoints
  │     ├── models/        # Schemas Pydantic
  │     ├── services/      # Serviços e lógica de negócio
  │     └── ...
  └── ...
```


### Passos para Integração
- [x] Estrutura do backend FastAPI criada (pasta `backend`)
- [x] Adicionado `requirements.txt` com FastAPI, Uvicorn e libs necessárias
- [x] Criado `Dockerfile` para build automatizado
- [x] Implementado `main.py` com instância FastAPI
- [x] Configurado docker-compose para rodar frontend e backend juntos

## 2. Endpoints Necessários para a Dashboard


- [x] `GET /api/metrics/overview` — Dados principais do dashboard (implementado exemplo)
- [x] `GET /api/metrics/performance` — Dados de performance (implementado exemplo)
- [x] `GET /api/metrics/alertas` — Dados de alertas (implementado exemplo)
- [x] `GET /api/metrics/analise-corridas` — Dados de análise de corridas (implementado exemplo)

### 2.2 Inteligência Artificial
- [x] `POST /api/ia/predict` — Previsão de demanda (implementado exemplo)
- [x] `POST /api/ia/sentiment` — Análise de sentimento (implementado exemplo)
- [x] `POST /api/ia/recommendation` — Recomendações automáticas (implementado exemplo)
    - [x] `POST /api/ia/anomaly` — Detecção de anomalias (implementado exemplo)
    - [x] `POST /api/ia/llm` — Chat LLM (implementado exemplo)

### 2.3 Mapas e Geolocalização
    - [x] `GET /api/maps/heatmap` — Dados para mapa de calor (implementado exemplo)
    - [x] `GET /api/maps/routes` — Rotas otimizadas (implementado exemplo)
    - [x] `GET /api/maps/geo-analysis` — Análise geográfica (implementado exemplo)
    - [x] `GET /api/maps/traffic` — Previsão de tráfego (implementado exemplo)

### 2.4 Dashboards Especializados
    - [x] `GET /api/dashboard/financeiro` — Dados financeiros (implementado exemplo)
    - [x] `GET /api/dashboard/operacional` — Dados operacionais (implementado exemplo)
    - [x] `GET /api/dashboard/executivo` — Dados executivos (implementado exemplo)
    - [x] `GET /api/dashboard/preditivo` — Dados preditivos (implementado exemplo)

### 2.5 Segurança e Usuários
    - [x] `POST /api/auth/login` — Login/autenticação (implementado exemplo)
    - [x] `POST /api/auth/2fa` — Autenticação 2FA (implementado exemplo)
    - [x] `GET /api/auth/user` — Dados do usuário logado (implementado exemplo)

## 3. Tarefas Técnicas
- [x] Definir contratos de dados (schemas Pydantic) (concluído)
- [x] Implementar endpoints FastAPI (concluído)
- [ ] Testar integração frontend-backend (em andamento)
- [ ] Documentar API (Swagger/OpenAPI) (em andamento)
- [ ] Automatizar build/deploy com Docker Compose

---

> **Observação:** Este plano cobre a estruturação da API FastAPI e os principais endpoints para alimentar todos os módulos da dashboard, conforme o plano de melhorias 2025. Cada endpoint pode ser detalhado em subtarefas conforme a necessidade do frontend.
