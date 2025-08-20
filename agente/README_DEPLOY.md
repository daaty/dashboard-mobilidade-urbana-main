# 🚀 Deploy do Agente Inteligente

## 📋 Overview

Este diretório contém o **Agente Inteligente** como uma API independente, pronta para deploy no Heroku.

## 🏠 Uso Local (mesmo ambiente do backend)

```bash
# 1. Ativar ambiente Python do backend
cd ..
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Instalar dependências do agente
cd agente
pip install -r requirements.txt

# 3. Configurar .env (copiar do .env.example)
cp dashboard_agent\.env.example dashboard_agent\.env
# Editar dashboard_agent\.env com sua OPENAI_API_KEY

# 4. Inicializar memória (opcional)
cd dashboard_agent
python init_memory.py criar

# 5. Usar o agente
python exemplo_uso.py
```

## 🌐 Deploy no Heroku (processo independente)

### Opção 1: Script Automático

```bash
cd agente
chmod +x deploy_agente.sh
./deploy_agente.sh
```

### Opção 2: Manual

```bash
# 1. Criar app no Heroku
heroku create dashboard-mobility-agent

# 2. Configurar variáveis
heroku config:set OPENAI_API_KEY="sua_chave" -a dashboard-mobility-agent
heroku config:set DASHBOARD_URL="https://seu-dashboard.herokuapp.com" -a dashboard-mobility-agent
heroku config:set MEMORY_DB_URL="postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db" -a dashboard-mobility-agent

# 3. Deploy
git init
git add .
git commit -m "Deploy agente"
heroku git:remote -a dashboard-mobility-agent
git push heroku main
```

## 🔗 URLs de Produção

Após deploy:
- **API Principal**: `https://dashboard-mobility-agent.herokuapp.com`
- **Documentação**: `https://dashboard-mobility-agent.herokuapp.com/docs`
- **Health Check**: `https://dashboard-mobility-agent.herokuapp.com/health`

## 📊 Endpoints da API

### Análises Predefinidas
```bash
POST /analyze
{
  "analysis_type": "performance|financial|drivers|expansion|trends|executive",
  "parameters": {}
}
```

### Perguntas Interativas
```bash
POST /ask
{
  "question": "Qual cidade tem melhor ROI?",
  "context": {}
}
```

### Status e Info
```bash
GET /status              # Status detalhado
GET /health              # Health check
GET /available-analyses  # Lista de análises
```

## 🛠️ Exemplo de Uso da API

```python
import requests

# URL da API do agente
API_URL = "https://dashboard-mobility-agent.herokuapp.com"

# Análise de performance
response = requests.post(f"{API_URL}/analyze", json={
    "analysis_type": "performance",
    "parameters": {}
})

result = response.json()
print(result['result'])

# Pergunta específica
response = requests.post(f"{API_URL}/ask", json={
    "question": "Quais são os principais KPIs atuais?",
    "context": {}
})

answer = response.json()
print(answer['result'])
```

## ⚙️ Configurações de Ambiente

### Local (.env)
```env
OPENAI_API_KEY=sua_chave_openai
DASHBOARD_URL=http://localhost:8000
MEMORY_DB_URL=postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db
```

### Produção (Heroku Config Vars)
```env
OPENAI_API_KEY=sua_chave_openai
DASHBOARD_URL=https://seu-dashboard.herokuapp.com
MEMORY_DB_URL=postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db
AGENT_MEMORY_TABLE_PREFIX=agente_
```

## 🔍 Troubleshooting

### Agente não inicializa
1. Verificar `OPENAI_API_KEY`
2. Verificar conectividade com `DASHBOARD_URL`
3. Verificar logs: `heroku logs --tail -a dashboard-mobility-agent`

### Erro de memória
1. Verificar `MEMORY_DB_URL`
2. Criar tabelas: `python dashboard_agent/init_memory.py criar`

### Deploy falha
1. Verificar `requirements.txt`
2. Verificar `Procfile`
3. Verificar se está na pasta `/agente`

## 📈 Monitoramento

```bash
# Ver logs em tempo real
heroku logs --tail -a dashboard-mobility-agent

# Status da aplicação
heroku ps -a dashboard-mobility-agent

# Reiniciar se necessário
heroku restart -a dashboard-mobility-agent
```

## 🎯 Próximos Passos

1. **Integração Frontend**: Conectar dashboard React com API do agente
2. **Webhooks**: Notificações automáticas de insights
3. **Scheduler**: Análises programadas
4. **Cache**: Redis para otimizar performance
