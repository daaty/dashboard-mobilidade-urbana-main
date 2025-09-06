# 🎮 SCRIPT PARA INICIAR O PLAYGROUND DO AGENTE (Windows PowerShell)
# Configura e inicia o playground com todas as dependências

Write-Host "🎮 INICIANDO PLAYGROUND DO AGENTE INTELIGENTE" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Verificar se estamos no diretório correto
if (!(Test-Path "playground.py")) {
    Write-Host "❌ Erro: Execute este script na pasta 'agente'" -ForegroundColor Red
    exit 1
}

# Verificar se o arquivo .env existe
if (!(Test-Path ".env")) {
    Write-Host "📝 Criando arquivo .env..." -ForegroundColor Yellow
    
    $envContent = @"
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
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Arquivo .env criado! Configure suas variáveis antes de continuar." -ForegroundColor Green
}

# Verificar se as dependências estão instaladas
Write-Host "🔍 Verificando dependências..." -ForegroundColor Yellow

$missingPackages = @()

# Verificar pacotes Python
try { python -c "import agno" 2>$null } catch { $missingPackages += "agno" }
try { python -c "import openai" 2>$null } catch { $missingPackages += "openai" }
try { python -c "import fastapi" 2>$null } catch { $missingPackages += "fastapi" }
try { python -c "import uvicorn" 2>$null } catch { $missingPackages += "uvicorn" }

if ($missingPackages.Count -gt 0) {
    Write-Host "📦 Instalando dependências faltantes: $($missingPackages -join ', ')" -ForegroundColor Yellow
    
    $packagesToInstall = @(
        "agno>=0.1.0",
        "openai>=1.3.0", 
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "websockets>=11.0.0"
    )
    
    foreach ($package in $packagesToInstall) {
        pip install $package
    }
}

Write-Host "✅ Dependências verificadas!" -ForegroundColor Green

# Verificar se a chave OpenAI está configurada
$envContent = Get-Content ".env" -Raw
if ($envContent -match "sua_chave_openai_aqui") {
    Write-Host "⚠️  ATENÇÃO: Configure sua OPENAI_API_KEY no arquivo .env antes de continuar!" -ForegroundColor Yellow
    Write-Host "📝 Abrindo arquivo .env para edição..." -ForegroundColor Cyan
    
    # Tentar abrir editor
    if (Get-Command "code" -ErrorAction SilentlyContinue) {
        code .env
    } elseif (Get-Command "notepad" -ErrorAction SilentlyContinue) {
        notepad .env
    } else {
        Write-Host "💡 Edite manualmente o arquivo .env e configure sua OpenAI API Key" -ForegroundColor Cyan
    }
    
    Read-Host "Pressione Enter quando terminar de configurar o arquivo .env"
}

# Testar configuração do agente
Write-Host "🧪 Testando configuração do agente..." -ForegroundColor Yellow

$testScript = @"
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
dashboard_url = os.getenv('DASHBOARD_URL')

if not api_key or api_key == 'sua_chave_openai_aqui':
    print('❌ OPENAI_API_KEY não configurada!')
    exit(1)

if not dashboard_url:
    print('❌ DASHBOARD_URL não configurada!')
    exit(1)

print('✅ Configuração OK!')
print(f'📡 Dashboard URL: {dashboard_url}')
print(f'🔑 OpenAI API Key: {api_key[:10]}...')
"@

$testResult = python -c $testScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Configuração inválida. Corrija o arquivo .env e tente novamente." -ForegroundColor Red
    exit 1
}

Write-Host $testResult -ForegroundColor Green

# Iniciar o playground
Write-Host ""
Write-Host "🚀 INICIANDO PLAYGROUND..." -ForegroundColor Cyan
Write-Host "🌐 Interface Web: http://localhost:8002" -ForegroundColor Green
Write-Host "📊 API Docs: http://localhost:8002/docs" -ForegroundColor Green  
Write-Host "💬 WebSocket: ws://localhost:8002/ws" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Para parar o playground: Ctrl+C" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Gray

# Executar o playground
python playground.py
