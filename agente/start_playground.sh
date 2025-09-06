#!/bin/bash

# 🎮 SCRIPT PARA INICIAR O PLAYGROUND DO AGENTE
# Configura e inicia o playground com todas as dependências

echo "🎮 INICIANDO PLAYGROUND DO AGENTE INTELIGENTE"
echo "=" * 50

# Verificar se estamos no diretório correto
if [ ! -f "playground.py" ]; then
    echo "❌ Erro: Execute este script na pasta 'agente'"
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << EOL
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
EOL
    echo "✅ Arquivo .env criado! Configure suas variáveis antes de continuar."
fi

# Verificar se as dependências estão instaladas
echo "🔍 Verificando dependências..."

# Lista de pacotes obrigatórios
required_packages="agno openai fastapi uvicorn python-dotenv websockets alpinejs"

missing_packages=""

# Verificar cada pacote (simplificado)
if ! python -c "import agno" 2>/dev/null; then
    missing_packages="$missing_packages agno"
fi

if ! python -c "import openai" 2>/dev/null; then
    missing_packages="$missing_packages openai"
fi

if ! python -c "import fastapi" 2>/dev/null; then
    missing_packages="$missing_packages fastapi"
fi

if ! python -c "import uvicorn" 2>/dev/null; then
    missing_packages="$missing_packages uvicorn"
fi

if [ -n "$missing_packages" ]; then
    echo "📦 Instalando dependências faltantes: $missing_packages"
    pip install $missing_packages
    
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar dependências. Instalando manualmente..."
        pip install agno>=0.1.0
        pip install openai>=1.3.0
        pip install fastapi>=0.104.0
        pip install uvicorn>=0.24.0
        pip install python-dotenv>=1.0.0
        pip install websockets>=11.0.0
    fi
fi

echo "✅ Dependências verificadas!"

# Verificar se a chave OpenAI está configurada
if grep -q "sua_chave_openai_aqui" .env; then
    echo "⚠️  ATENÇÃO: Configure sua OPENAI_API_KEY no arquivo .env antes de continuar!"
    echo "📝 Editando arquivo .env..."
    
    # Abrir editor (se disponível)
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    elif command -v code &> /dev/null; then
        code .env
    else
        echo "💡 Edite manualmente o arquivo .env e configure sua OpenAI API Key"
        read -p "Pressione Enter quando terminar..."
    fi
fi

# Testar configuração do agente
echo "🧪 Testando configuração do agente..."
python -c "
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
"

if [ $? -ne 0 ]; then
    echo "❌ Configuração inválida. Corrija o arquivo .env e tente novamente."
    exit 1
fi

# Iniciar o playground
echo ""
echo "🚀 INICIANDO PLAYGROUND..."
echo "🌐 Interface Web: http://localhost:8002"
echo "📊 API Docs: http://localhost:8002/docs"
echo "💬 WebSocket: ws://localhost:8002/ws"
echo ""
echo "💡 Para parar o playground: Ctrl+C"
echo "=" * 50

# Executar o playground
python playground.py
