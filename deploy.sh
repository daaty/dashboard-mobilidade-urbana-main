#!/bin/bash
# 🚀 Script de Deploy para Easypanel
# Dashboard de Mobilidade Urbana

set -e  # Parar em caso de erro

echo "🚀 INICIANDO DEPLOY - DASHBOARD MOBILIDADE URBANA"
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado!"
    exit 1
fi

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    log_error "Git não está instalado!"
    exit 1
fi

# Informações do projeto
PROJECT_NAME="dashboard-mobilidade-urbana"
DOCKER_TAG="latest"
REGISTRY=""  # Easypanel vai usar o registry configurado

log_info "Projeto: $PROJECT_NAME"
log_info "Tag: $DOCKER_TAG"

# 1. Verificar status do Git
log_info "Verificando status do Git..."
if [ -n "$(git status --porcelain)" ]; then
    log_warning "Existem mudanças não commitadas!"
    echo "Mudanças pendentes:"
    git status --short
    
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deploy cancelado pelo usuário."
        exit 0
    fi
fi

# 2. Build da imagem Docker
log_info "Construindo imagem Docker..."
docker build -t $PROJECT_NAME:$DOCKER_TAG .

if [ $? -eq 0 ]; then
    log_success "Imagem Docker construída com sucesso!"
else
    log_error "Falha na construção da imagem Docker!"
    exit 1
fi

# 3. Testar a imagem localmente (opcional)
log_info "Testando imagem localmente..."
CONTAINER_ID=$(docker run -d -p 8080:8080 $PROJECT_NAME:$DOCKER_TAG)

# Aguardar container inicializar
sleep 10

# Testar health check
if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
    log_success "Health check passou! Container funcionando."
    docker stop $CONTAINER_ID > /dev/null
    docker rm $CONTAINER_ID > /dev/null
else
    log_warning "Health check falhou. Verificando logs..."
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID > /dev/null
    docker rm $CONTAINER_ID > /dev/null
    
    read -p "Continuar mesmo com falha no health check? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deploy cancelado devido à falha no health check."
        exit 1
    fi
fi

# 4. Preparar para Easypanel
log_info "Preparando informações para Easypanel..."

echo ""
echo "🎯 INFORMAÇÕES PARA EASYPANEL:"
echo "================================"
echo "📂 Repository: $(git config --get remote.origin.url)"
echo "🌿 Branch: $(git branch --show-current)"
echo "🐳 Dockerfile: ./Dockerfile"
echo "🔌 Port: 8080"
echo "🏥 Health Check: /api/health"
echo ""

# 5. Mostrar variáveis de ambiente necessárias
echo "🔧 VARIÁVEIS DE AMBIENTE NECESSÁRIAS:"
echo "====================================="
echo "FLASK_ENV=production"
echo "DATABASE_URL=<sua_database_url>"
echo "SECRET_KEY=<sua_secret_key>"
echo "CORS_ORIGINS=<seus_dominios>"
echo ""

# 6. Instruções finais
echo "📋 PRÓXIMOS PASSOS NO EASYPANEL:"
echo "================================"
echo "1. 🔗 Conecte o repositório Git no Easypanel"
echo "2. 📁 Configure o Dockerfile path: ./Dockerfile"
echo "3. 🔌 Configure a porta: 8080"
echo "4. 🏥 Configure health check: /api/health"
echo "5. 🔧 Adicione as variáveis de ambiente listadas acima"
echo "6. 🚀 Execute o deploy!"
echo ""

# 7. Commit automático das mudanças de deploy
if [ -n "$(git status --porcelain)" ]; then
    log_info "Fazendo commit das configurações de deploy..."
    git add .
    git commit -m "🐳 Configuração para deploy no Easypanel com Dockerfile

- Dockerfile multi-stage otimizado
- Permissões adequadas para containers
- Health check configurado
- Servir arquivos estáticos via Flask
- Scripts de deploy automatizado"
    
    log_success "Commit realizado com sucesso!"
    log_info "Não esqueça de fazer push: git push origin $(git branch --show-current)"
fi

log_success "Deploy preparation completed! 🎉"
echo ""
echo "🔗 Para fazer deploy no Easypanel:"
echo "   1. Acesse seu painel do Easypanel"
echo "   2. Conecte este repositório"
echo "   3. Use as configurações mostradas acima"
echo ""
