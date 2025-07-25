# Guia de Instalação - Dashboard de Transporte

Este guia fornece instruções passo a passo para instalar e configurar o dashboard em seu ambiente.

## 📋 Pré-requisitos

### Sistema Operacional
- Linux (Ubuntu 22.04 recomendado)
- macOS 10.15+
- Windows 10+ (com WSL2 recomendado)

### Software Necessário
- **Python 3.11+**
- **Node.js 20.18.0+**
- **pnpm** (gerenciador de pacotes)
- **Git** (para controle de versão)

## 🔧 Instalação Passo a Passo

### 1. Preparação do Ambiente

#### Verificar Python
```bash
python3 --version
# Deve retornar Python 3.11.0 ou superior
```

#### Verificar Node.js
```bash
node --version
# Deve retornar v20.18.0 ou superior
```

#### Instalar pnpm (se não estiver instalado)
```bash
npm install -g pnpm
```

### 2. Configuração do Backend

#### 2.1. Navegar para o diretório do backend
```bash
cd dashboard_transporte/backend/dashboard_api
```

#### 2.2. Ativar o ambiente virtual
```bash
source venv/bin/activate
```

#### 2.3. Verificar dependências instaladas
```bash
pip list
```

Dependências principais que devem estar presentes:
- Flask
- flask-cors
- google-auth
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- pandas

#### 2.4. Testar o backend
```bash
python src/main.py
```

Você deve ver:
```
Aviso: Credenciais do Google Sheets não configuradas. Usando dados mock.
Iniciando Flask na porta 5003...
* Serving Flask app 'main'
* Debug mode: on
* Running on http://127.0.0.1:5003
```

#### 2.5. Testar API (em outro terminal)
```bash
curl http://localhost:5003/api/test
```

Resposta esperada:
```json
{"message":"API funcionando","status":"ok"}
```

### 3. Configuração do Frontend

#### 3.1. Navegar para o diretório do frontend
```bash
cd dashboard_transporte/frontend/dashboard-ui
```

#### 3.2. Verificar dependências instaladas
```bash
pnpm list
```

Dependências principais que devem estar presentes:
- react
- vite
- tailwindcss
- recharts
- framer-motion
- lucide-react

#### 3.3. Configurar variáveis de ambiente
```bash
echo 'VITE_API_URL=http://localhost:5003' > .env.local
```

#### 3.4. Iniciar servidor de desenvolvimento
```bash
pnpm run dev --host
```

Você deve ver:
```
VITE v5.x.x ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://xxx.xxx.xxx.xxx:5173/
```

### 4. Verificação da Instalação

#### 4.1. Acessar o dashboard
Abra seu navegador e acesse: `http://localhost:5173`

#### 4.2. Verificar funcionalidades básicas
- ✅ Sidebar deve estar visível com menu de navegação
- ✅ Header deve mostrar data/hora atual
- ✅ Cards de métricas devem aparecer (com dados mock)
- ✅ Navegação entre abas deve funcionar

#### 4.3. Testar responsividade
- Redimensione a janela do navegador
- Teste em diferentes tamanhos de tela
- Verifique se a sidebar colapsa corretamente

## 🔗 Configuração do Google Sheets

### 1. Preparar Credenciais (Opcional para Produção)

Para usar dados reais do Google Sheets, você precisará:

#### 1.1. Criar projeto no Google Cloud Console
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Sheets

#### 1.2. Criar credenciais
1. Vá para "APIs & Services" > "Credentials"
2. Clique em "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure como "Desktop application"
4. Baixe o arquivo JSON de credenciais

#### 1.3. Configurar credenciais no backend
```bash
# Criar diretório de configuração
mkdir -p dashboard_transporte/backend/dashboard_api/src/config

# Copiar arquivo de credenciais
cp /caminho/para/credentials.json dashboard_transporte/backend/dashboard_api/src/config/
```

### 2. Configurar Planilhas

#### 2.1. Criar planilhas no Google Sheets
Crie duas planilhas seguindo a estrutura documentada no README.md

#### 2.2. Obter IDs das planilhas
- URL da planilha: `https://docs.google.com/spreadsheets/d/PLANILHA_ID/edit`
- O ID é a parte entre `/d/` e `/edit`

#### 2.3. Configurar no dashboard
1. Acesse a aba "Configurações" no dashboard
2. Cole os IDs ou URLs completas das planilhas
3. Clique em "Testar Conexão"
4. Clique em "Salvar Configuração"

## 🚨 Solução de Problemas

### Problema: Backend não inicia
**Erro**: `Address already in use`

**Solução**:
```bash
# Verificar processos na porta
netstat -tlnp | grep 5003

# Matar processo se necessário
kill [PID]

# Ou usar porta diferente
# Editar src/main.py e alterar port=5003 para port=5004
```

### Problema: Frontend não carrega
**Erro**: `EADDRINUSE: address already in use`

**Solução**:
```bash
# Matar processos Node.js
pkill -f "vite"

# Ou usar porta diferente
pnpm run dev --port 5174 --host
```

### Problema: Erro de CORS
**Erro**: `Access to fetch at 'http://localhost:5003' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solução**:
- Verificar se `flask-cors` está instalado
- Confirmar que `CORS(app)` está configurado no backend
- Reiniciar o servidor backend

### Problema: Dados não carregam
**Sintomas**: Cards ficam em loading infinito

**Verificações**:
1. Backend está rodando? `curl http://localhost:5003/api/test`
2. URLs da API estão corretas no frontend?
3. Console do navegador mostra erros?

**Solução**:
```bash
# Verificar logs do backend
tail -f dashboard_transporte/backend/dashboard_api/flask.log

# Verificar console do navegador (F12)
```

## 📊 Dados de Teste

O sistema vem com dados mock pré-configurados para teste:

### Corridas Concluídas (5 registros)
- São Paulo: 3 corridas
- Rio de Janeiro: 1 corrida  
- Belo Horizonte: 1 corrida

### Corridas Canceladas (2 registros)
- Motivos: Desistência, Problema no veículo

### Corridas Perdidas (2 registros)
- Motivos: Falha na conexão, Sem motoristas na região

### Metas por Cidade
- São Paulo: Meta 200, Média 150
- Rio de Janeiro: Meta 120, Média 100
- Belo Horizonte: Meta 90, Média 80

## 🔄 Atualizações Futuras

### Para atualizar o sistema:

1. **Backend**:
```bash
cd dashboard_transporte/backend/dashboard_api
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

2. **Frontend**:
```bash
cd dashboard_transporte/frontend/dashboard-ui
pnpm update
```

## 📞 Suporte Técnico

### Logs Importantes
- **Backend**: `dashboard_transporte/backend/dashboard_api/flask.log`
- **Frontend**: Console do navegador (F12)

### Comandos Úteis
```bash
# Verificar status dos serviços
ps aux | grep python  # Backend
ps aux | grep node     # Frontend

# Verificar portas em uso
netstat -tlnp | grep 5003  # Backend
netstat -tlnp | grep 5173  # Frontend

# Reiniciar serviços
# Backend: Ctrl+C e python src/main.py
# Frontend: Ctrl+C e pnpm run dev --host
```

### Informações do Sistema
- **Versão Python**: 3.11.0rc1
- **Versão Node.js**: 20.18.0
- **Sistema**: Ubuntu 22.04 linux/amd64

---

**✅ Instalação concluída com sucesso!**

Agora você pode usar o dashboard para acompanhar as métricas da sua empresa de transporte.

