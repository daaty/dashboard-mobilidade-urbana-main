# 🚀 GUIA DE DEPLOY - EASYPANEL

> **Dashboard de Mobilidade Urbana - Deploy no Easypanel**  
> **Versão**: 1.0  
> **Data**: Julho 2025  

---

## 📋 **PRÉ-REQUISITOS**

- ✅ Conta no Easypanel configurada
- ✅ Repositório Git com o código (GitHub/GitLab)
- ✅ Dockerfile criado (✅ já incluído)
- ✅ Banco PostgreSQL disponível
- ✅ Redis disponível (opcional)

---

## 🚀 **PASSO A PASSO - DEPLOY**

### **1. Preparar o Código (Opcional)**
```bash
# No diretório do projeto - apenas para teste local
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
```

> 💡 **IMPORTANTE**: O script `deploy_easypanel.sh` é usado apenas para **testes locais**.  
> No Easypanel, o repositório Git é clonado automaticamente e o **Dockerfile** já configura todas as permissões necessárias com `chmod +x`.

### **2. Configurar no Easypanel**

#### **2.1 Criar Nova Aplicação**
1. Acesse seu painel do Easypanel
2. Clique em **"Create App"**
3. Escolha **"Deploy from Git"**

#### **2.2 Configurar Repositório**
- **Repository URL**: `https://github.com/SEU_USUARIO/dashboard-mobilidade-urbana`
- **Branch**: `main`
- **Build Pack**: `Docker` (será detectado automaticamente)

#### **2.3 Configurar Variáveis de Ambiente**
```env
FLASK_ENV=production
SECRET_KEY=sua_chave_super_secreta_aqui_2025
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0
PORT=8080
```

### **3. Deploy Automático**
- O Easypanel detectará o `Dockerfile`
- Build será executado automaticamente
- Aplicação ficará disponível na URL fornecida

---

## 🔧 **COMO FUNCIONA NO EASYPANEL**

### **Fluxo de Deploy Automático**
1. **Git Clone**: Easypanel clona seu repositório
2. **Dockerfile Detection**: Detecta automaticamente o Dockerfile
3. **Build Process**: Executa `docker build .`
4. **Permission Setup**: Dockerfile configura permissões com `chmod +x`
5. **Container Start**: Inicia o container na porta 8080

### **Permissões no Dockerfile**
```dockerfile
# ✅ Permissões são configuradas DENTRO do Dockerfile
RUN chmod +x /app/deploy_easypanel.sh \
    && chmod +x /app/build.sh
```

> 🎯 **Vantagem**: Não precisa de comandos externos. Tudo é automatizado!

---

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **Recursos Recomendados**
- **CPU**: 1-2 vCPUs
- **RAM**: 1-2 GB
- **Storage**: 10 GB
- **Porta**: 8080 (configurada no Dockerfile)

### **Health Check**
- **Endpoint**: `/api/health`
- **Intervalo**: 30s
- **Timeout**: 10s

### **Backup e Persistência**
- **Dados**: Salvos no PostgreSQL
- **Logs**: Disponíveis no painel Easypanel
- **Uploads**: Diretório `/app/uploads` (volume persistente recomendado)

---

## 🗄️ **BANCO DE DADOS**

### **PostgreSQL Configuration**
```sql
-- Schema será criado automaticamente pelo Flask
-- Dados iniciais são carregados do dados_exemplo.csv
```

### **Variáveis de Conexão**
```env
DATABASE_URL=postgresql://usuario:senha@host:5432/database_name
```

---

## 🔍 **MONITORAMENTO**

### **Logs da Aplicação**
```bash
# No painel Easypanel - seção Logs
# Filtros disponíveis: Error, Warning, Info
```

### **Métricas Importantes**
- **Response Time**: < 2s
- **Memory Usage**: < 80%
- **CPU Usage**: < 70%
- **Uptime**: > 99%

### **Endpoints de Monitoramento**
- **Health Check**: `GET /api/health`
- **Metrics**: `GET /api/metrics/overview`
- **Status**: `GET /api/dashboard/status`

---

## 🐛 **TROUBLESHOOTING**

### **Problema: Build Falha**
```bash
# Verificar logs de build no Easypanel
# Comum: dependências Python ou Node.js
```

### **Problema: App não inicia**
```bash
# Verificar variáveis de ambiente
# Verificar conexão com banco de dados
# Verificar logs de runtime
```

### **Problema: 502 Bad Gateway**
```bash
# App não está escutando na porta 8080
# Verificar health check /api/health
# Verificar se gunicorn está rodando
```

### **Problema: Banco de dados não conecta**
```bash
# Verificar DATABASE_URL
# Verificar se PostgreSQL está acessível
# Verificar firewall/security groups
```

---

## 🔄 **ATUALIZAÇÕES**

### **Deploy de Nova Versão**
1. Fazer commit das mudanças
2. Push para repositório
3. Easypanel detecta automaticamente
4. Build e deploy automático

### **Rollback**
1. No painel Easypanel
2. Seção "Deployments"
3. Selecionar versão anterior
4. Clique em "Deploy"

---

## 📊 **ESTRUTURA DE ARQUIVOS**

```
dashboard-mobilidade-urbana/
├── Dockerfile                 # ✅ Configuração Docker
├── deploy_easypanel.sh       # ✅ Script de deploy
├── docker-compose.yml        # Para desenvolvimento local
├── .dockerignore             # Otimização de build
├── main.py                   # Aplicação principal
├── backend/                  # Backend Flask
│   ├── requirements.txt      # Dependências Python
│   └── ...
├── src/                      # Frontend React
├── package.json              # Dependências Node.js
└── database/                 # Schema SQL
```

---

## 🎯 **CHECKLIST FINAL**

### **Antes do Deploy**
- [ ] Código commitado e enviado para Git
- [ ] Dockerfile testado localmente
- [ ] Variáveis de ambiente definidas
- [ ] PostgreSQL configurado
- [ ] SECRET_KEY gerada

### **Após o Deploy**
- [ ] App acessível na URL fornecida
- [ ] Health check funcionando (`/api/health`)
- [ ] Dashboard carregando corretamente
- [ ] API respondendo (`/api/dashboard/overview`)
- [ ] Logs sem erros críticos

---

## 📞 **SUPORTE**

### **Recursos Úteis**
- **Documentação Easypanel**: [docs.easypanel.io](https://docs.easypanel.io)
- **Logs da Aplicação**: Painel Easypanel > Logs
- **Monitoramento**: Painel Easypanel > Metrics

### **Comandos Úteis**
```bash
# Testar build local
docker build -t dashboard-test .

# Testar health check
curl http://localhost:8080/api/health

# Ver logs de produção
# (Disponível no painel Easypanel)
```

---

> **✅ STATUS**: Pronto para deploy  
> **🎯 URL DE PRODUÇÃO**: Será fornecida pelo Easypanel  
> **📅 ÚLTIMA ATUALIZAÇÃO**: Julho 2025  

**🚀 Dashboard pronto para rodar no Easypanel com Docker!**
