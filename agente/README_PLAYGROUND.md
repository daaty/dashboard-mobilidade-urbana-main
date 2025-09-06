# 🎮 Playground do Agente Inteligente

## 🎯 **O que é?**

Um **playground interativo** para monitorar e interagir com o agente inteligente AGNO em tempo real. É como um "painel de controle" onde você pode:

- 💬 **Conversar com o agente** via chat web
- 🛠️ **Monitorar tool calls** em tempo real
- 📊 **Ver estatísticas** de performance
- 📋 **Acompanhar logs** detalhados
- 🔍 **Debugar problemas** facilmente

## 🚀 **Como usar?**

### **Método 1: Script automático (Windows)**

```powershell
# No PowerShell
.\start_playground.ps1
```

### **Método 2: Script automático (Linux/Mac)**

```bash
# No terminal
chmod +x start_playground.sh
./start_playground.sh
```

### **Método 3: Manual**

```bash
# 1. Instalar dependências
pip install agno>=0.1.0 openai>=1.3.0 fastapi>=0.104.0 uvicorn>=0.24.0

# 2. Configurar .env (veja seção abaixo)

# 3. Iniciar playground
python playground.py
```

## ⚙️ **Configuração (.env)**

Crie um arquivo `.env` na pasta agente:

```env
# 🤖 CONFIGURAÇÕES DO AGENTE INTELIGENTE

# OpenAI API Key (obrigatório)
OPENAI_API_KEY=sua_chave_openai_aqui

# URL do Dashboard (onde está a API FastAPI)
DASHBOARD_URL=https://fastapi.urbanmt.com.br

# Base de dados para memória do agente (opcional)
MEMORY_DB_URL=postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db
AGENT_MEMORY_TABLE_PREFIX=agente_

# Configurações do Playground
PLAYGROUND_HOST=0.0.0.0
PLAYGROUND_PORT=8002
```

## 🌐 **Acessando o Playground**

Após iniciar o playground:

- **Interface Principal**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/api/health

## 🎮 **Funcionalidades**

### **1. Chat Interativo**
- Converse com o agente em linguagem natural
- Veja respostas em tempo real
- Histórico de conversas

### **2. Monitor de Tool Calls**
- Acompanhe quando ferramentas são chamadas
- Veja duração e status de cada call
- Debug de problemas com ferramentas

### **3. Logs em Tempo Real**
- Logs categorizados (INFO, ERROR, SUCCESS, etc.)
- Timestamps precisos
- Export automático para arquivo

### **4. Estatísticas**
- Total de interações
- Tempo médio de resposta
- Ferramentas mais utilizadas
- Taxa de sucesso

### **5. Análises Rápidas**
Botões para análises comuns:
- 📊 Performance Geral
- 💰 Saúde Financeira  
- 🌍 Oportunidades de Expansão
- 📋 Relatório Executivo

## 🧪 **Testando o Playground**

```bash
# Testar se tudo está funcionando
python test_playground.py

# Testar em URL específica
python test_playground.py http://localhost:8002
```

## 🛠️ **Arquitetura**

### **Componentes:**

1. **playground.py** - Interface web FastAPI + WebSocket
2. **monitor.py** - Wrapper para monitoramento do agente AGNO
3. **dashboard_agent/** - Agente inteligente com ferramentas
4. **test_playground.py** - Suite de testes automatizados

### **Fluxo de dados:**

```
Interface Web ←→ WebSocket ←→ FastAPI ←→ Monitor ←→ Agente AGNO ←→ Ferramentas
```

### **Monitoramento:**

- **Tool Calls**: Intercepta e registra todas as chamadas
- **Timing**: Mede duração de operações
- **Errors**: Captura e categoriza erros
- **Memory**: Tracking de uso de memória do agente

## 🔧 **Troubleshooting**

### **Problema: Agente não inicializa**

```bash
# Verificar configuração
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY', 'NÃO CONFIGURADA'))
print('DASHBOARD_URL:', os.getenv('DASHBOARD_URL', 'NÃO CONFIGURADA'))
"
```

### **Problema: Interface não carrega**

```bash
# Verificar se porta está livre
netstat -an | findstr :8002  # Windows
netstat -an | grep :8002     # Linux/Mac

# Tentar porta alternativa
python playground.py --port 8003
```

### **Problema: WebSocket não conecta**

1. Verificar se firewall está bloqueando
2. Testar com navegador diferente
3. Verificar logs do playground

### **Problema: Ferramentas falham**

```bash
# Testar conectividade com dashboard
python -c "
import requests
url = 'https://fastapi.urbanmt.com.br/api/drivers/overview'
try:
    response = requests.get(url, timeout=10)
    print('Status:', response.status_code)
    print('Data:', response.json() if response.status_code == 200 else 'ERRO')
except Exception as e:
    print('Erro:', e)
"
```

## 📊 **Logs e Debug**

### **Arquivos de log:**
- `playground.log` - Log principal do playground
- `agent_session_*.json` - Sessões exportadas do agente

### **Níveis de log:**
- 🔍 **DEBUG** - Informações detalhadas
- ℹ️ **INFO** - Informações gerais
- ✅ **SUCCESS** - Operações bem-sucedidas
- ⚠️ **WARNING** - Avisos
- ❌ **ERROR** - Erros

### **Debug avançado:**

```python
# No playground, adicionar debug extra
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou modificar playground.py
logger = DebugLogger("playground_debug.log")
logger.debug("Mensagem de debug", {"extra_data": "valor"})
```

## 🚀 **Deploy em Produção**

### **Deploy local (recomendado para desenvolvimento):**

```bash
python playground.py
```

### **Deploy com Docker:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["python", "playground.py"]
```

### **Deploy no Heroku:**

```bash
# Procfile
web: python playground.py --port $PORT

# Configurar variáveis de ambiente no Heroku
heroku config:set OPENAI_API_KEY=sua_chave
heroku config:set DASHBOARD_URL=https://fastapi.urbanmt.com.br
```

## 📈 **Métricas e Performance**

### **Métricas coletadas:**
- Tempo de resposta do agente
- Número de tool calls por interação
- Taxa de sucesso das ferramentas
- Uso de memória
- Throughput (interações/minuto)

### **Otimização:**
- Cache de respostas similares
- Pool de conexões para APIs
- Async processing de tool calls
- Rate limiting inteligente

## 🔗 **Integrações**

### **Com o Dashboard Principal:**
- Consome todas as APIs do dashboard
- Sincronização de dados em tempo real
- Compartilha base de dados (opcional)

### **Com OpenAI:**
- Modelos GPT-4 para reasoning
- Function calling para ferramentas
- Embeddings para memória semântica

### **Com PostgreSQL:**
- Memória persistente do agente
- Histórico de conversas
- Analytics de uso

## 📝 **Próximos Passos**

### **Features planejadas:**
- [ ] Export de sessões para Excel/PDF
- [ ] Integração com Slack/Teams
- [ ] Dashboard de analytics avançado
- [ ] A/B testing de prompts
- [ ] Multi-user support
- [ ] API webhooks para integração

### **Melhorias técnicas:**
- [ ] Cache Redis para performance
- [ ] Monitoring com Prometheus
- [ ] Health checks avançados
- [ ] Auto-scaling baseado em load
- [ ] Rate limiting por usuário

---

## 🆘 **Suporte**

Se tiver problemas:

1. **Verificar logs** no arquivo `playground.log`
2. **Rodar testes** com `python test_playground.py`
3. **Verificar configuração** no arquivo `.env`
4. **Testar conectividade** com o dashboard
5. **Verificar versões** das dependências

**Dica**: O playground salva automaticamente logs detalhados de todas as operações para facilitar o debug! 🔍
