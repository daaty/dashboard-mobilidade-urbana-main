@echo off
REM Script de inicialização do Dashboard de Mobilidade Urbana para Windows
REM Inicia tanto o backend Flask quanto o frontend Vite

echo 🚀 Iniciando Dashboard de Mobilidade Urbana...
echo ================================================

REM Verifica se o Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale o Python.
    pause
    exit /b 1
)

REM Verifica se o npm está disponível
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm não encontrado. Por favor, instale o Node.js e npm.
    pause
    exit /b 1
)

REM Verifica se as dependências Python estão instaladas
if not exist "backend\requirements.txt" (
    echo ❌ arquivo requirements.txt não encontrado em backend/
    pause
    exit /b 1
)

echo 📦 Verificando dependências Python...
pip install -q -r backend\requirements.txt

REM Verifica se as dependências npm estão instaladas
if not exist "node_modules" (
    echo 📦 Instalando dependências npm...
    npm install
)

echo 🐍 Iniciando servidor Flask (Backend) na porta 5000...
start "Flask Backend" cmd /k "python main.py"

echo ⚡ Iniciando servidor Vite (Frontend) na porta 3000...
start "Vite Frontend" cmd /k "npm run dev"

echo ================================================
echo ✅ Serviços iniciados com sucesso!
echo 📊 Dashboard (Produção): http://localhost:5000
echo 🔧 Dashboard (Desenvolvimento): http://localhost:3000
echo ================================================
echo 💡 Feche as janelas dos terminais para parar os serviços
echo.

pause
