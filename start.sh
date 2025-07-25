#!/bin/bash

# Script de inicialização do Dashboard de Mobilidade Urbana
# Inicia tanto o backend Flask quanto o frontend Vite

echo "🚀 Iniciando Dashboard de Mobilidade Urbana..."
echo "================================================"

# Função para limpar processos ao sair
cleanup() {
    echo -e "\n🛑 Parando serviços..."
    # Mata todos os processos filhos
    jobs -p | xargs -r kill
    echo "✅ Serviços parados"
    exit 0
}

# Registra a função de limpeza para diferentes sinais
trap cleanup SIGINT SIGTERM EXIT

# Verifica se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale o Python3."
    exit 1
fi

# Verifica se o npm está disponível
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Por favor, instale o Node.js e npm."
    exit 1
fi

# Verifica se as dependências Python estão instaladas
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ arquivo requirements.txt não encontrado em backend/"
    exit 1
fi

# Instala dependências Python se necessário
echo "📦 Verificando dependências Python..."
pip3 install -q -r backend/requirements.txt

# Verifica se as dependências npm estão instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências npm..."
    npm install
fi

echo "🐍 Iniciando servidor Flask (Backend) na porta 5000..."
python3 main.py &
FLASK_PID=$!

echo "⚡ Iniciando servidor Vite (Frontend) na porta 3000..."
npm run dev &
VITE_PID=$!

echo "================================================"
echo "✅ Serviços iniciados com sucesso!"
echo "📊 Dashboard (Produção): http://localhost:5000"
echo "🔧 Dashboard (Desenvolvimento): http://localhost:3000"
echo "================================================"
echo "💡 Pressione Ctrl+C para parar todos os serviços"
echo ""

# Aguarda qualquer um dos processos terminar
wait $FLASK_PID $VITE_PID
