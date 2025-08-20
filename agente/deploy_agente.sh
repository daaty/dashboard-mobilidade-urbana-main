#!/bin/bash

# 🚀 DEPLOY DO AGENTE INTELIGENTE NO HEROKU
# Script para fazer deploy independente do agente

echo "🤖 DEPLOY DO AGENTE INTELIGENTE - HEROKU"
echo "======================================="

# Verificar se está na pasta do agente
if [ ! -f "main.py" ]; then
    echo "❌ Execute este script na pasta /agente"
    exit 1
fi

# Nome da aplicação no Heroku
APP_NAME="dashboard-mobility-agent"

echo "📋 Configurando deploy..."

# 1. Inicializar git se necessário
if [ ! -d ".git" ]; then
    echo "🔧 Inicializando repositório git..."
    git init
    git add .
    git commit -m "Initial commit - Agente Inteligente"
fi

# 2. Criar app no Heroku (se não existir)
echo "🚀 Criando/verificando app no Heroku..."
heroku create $APP_NAME --region us 2>/dev/null || echo "App já existe"

# 3. Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."

# Solicitar API key se não estiver configurada
if [ -z "$OPENAI_API_KEY" ]; then
    echo "🔑 Configure sua OpenAI API Key:"
    read -p "OPENAI_API_KEY: " OPENAI_API_KEY
fi

# Configurar variáveis no Heroku
heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" -a $APP_NAME
heroku config:set DASHBOARD_URL="https://dashboard-mobilidade-urbana-main-4e5d29b0c6cb.herokuapp.com" -a $APP_NAME
heroku config:set MEMORY_DB_URL="postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db" -a $APP_NAME
heroku config:set AGENT_MEMORY_TABLE_PREFIX="agente_" -a $APP_NAME

# 4. Configurar buildpack Python
echo "🐍 Configurando buildpack Python..."
heroku buildpacks:set heroku/python -a $APP_NAME

# 5. Deploy
echo "🚀 Fazendo deploy..."
git add .
git commit -m "Deploy agente inteligente - $(date)"

# Adicionar remote do Heroku se não existir
git remote remove heroku 2>/dev/null
heroku git:remote -a $APP_NAME

# Push para Heroku
git push heroku main --force

echo ""
echo "✅ DEPLOY CONCLUÍDO!"
echo "🌐 URL do Agente: https://$APP_NAME.herokuapp.com"
echo "📖 Documentação: https://$APP_NAME.herokuapp.com/docs"
echo "❤️ Health Check: https://$APP_NAME.herokuapp.com/health"
echo ""
echo "📋 Comandos úteis:"
echo "heroku logs --tail -a $APP_NAME  # Ver logs"
echo "heroku ps -a $APP_NAME           # Ver status"
echo "heroku restart -a $APP_NAME      # Reiniciar"
