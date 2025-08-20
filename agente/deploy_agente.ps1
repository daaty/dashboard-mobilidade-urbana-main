# 🚀 DEPLOY DO AGENTE INTELIGENTE NO HEROKU (Windows PowerShell)
# Script para fazer deploy independente do agente

Write-Host "🤖 DEPLOY DO AGENTE INTELIGENTE - HEROKU" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Verificar se está na pasta do agente
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Execute este script na pasta /agente" -ForegroundColor Red
    exit 1
}

# Nome da aplicação no Heroku
$APP_NAME = "dashboard-mobility-agent"

Write-Host "📋 Configurando deploy..." -ForegroundColor Yellow

# 1. Inicializar git se necessário
if (-not (Test-Path ".git")) {
    Write-Host "🔧 Inicializando repositório git..." -ForegroundColor Blue
    git init
    git add .
    git commit -m "Initial commit - Agente Inteligente"
}

# 2. Criar app no Heroku (se não existir)
Write-Host "🚀 Criando/verificando app no Heroku..." -ForegroundColor Blue
$result = heroku create $APP_NAME --region us 2>&1
if ($LASTEXITCODE -ne 0 -and $result -notmatch "already exists") {
    Write-Host "⚠️ App já existe ou erro na criação: $result" -ForegroundColor Yellow
}

# 3. Configurar variáveis de ambiente
Write-Host "⚙️ Configurando variáveis de ambiente..." -ForegroundColor Blue

# Solicitar API key se não estiver configurada
$OPENAI_API_KEY = $env:OPENAI_API_KEY
if (-not $OPENAI_API_KEY) {
    $OPENAI_API_KEY = Read-Host "🔑 Digite sua OpenAI API Key"
}

# Configurar variáveis no Heroku
heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" -a $APP_NAME
heroku config:set DASHBOARD_URL="https://dashboard-mobilidade-urbana-main-4e5d29b0c6cb.herokuapp.com" -a $APP_NAME
heroku config:set MEMORY_DB_URL="postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db" -a $APP_NAME
heroku config:set AGENT_MEMORY_TABLE_PREFIX="agente_" -a $APP_NAME

# 4. Configurar buildpack Python
Write-Host "🐍 Configurando buildpack Python..." -ForegroundColor Blue
heroku buildpacks:set heroku/python -a $APP_NAME

# 5. Deploy
Write-Host "🚀 Fazendo deploy..." -ForegroundColor Green
git add .
$commitMessage = "Deploy agente inteligente - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m $commitMessage

# Adicionar remote do Heroku se não existir
git remote remove heroku 2>$null
heroku git:remote -a $APP_NAME

# Push para Heroku
git push heroku main --force

Write-Host ""
Write-Host "✅ DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "🌐 URL do Agente: https://$APP_NAME.herokuapp.com" -ForegroundColor Cyan
Write-Host "📖 Documentação: https://$APP_NAME.herokuapp.com/docs" -ForegroundColor Cyan
Write-Host "❤️ Health Check: https://$APP_NAME.herokuapp.com/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Comandos úteis:" -ForegroundColor Yellow
Write-Host "heroku logs --tail -a $APP_NAME  # Ver logs" -ForegroundColor White
Write-Host "heroku ps -a $APP_NAME           # Ver status" -ForegroundColor White
Write-Host "heroku restart -a $APP_NAME      # Reiniciar" -ForegroundColor White

# Perguntar se deseja abrir a documentação
$openDocs = Read-Host "`n🌐 Deseja abrir a documentação da API? (s/n)"
if ($openDocs -eq 's' -or $openDocs -eq 'S' -or $openDocs -eq 'sim') {
    Start-Process "https://$APP_NAME.herokuapp.com/docs"
}
