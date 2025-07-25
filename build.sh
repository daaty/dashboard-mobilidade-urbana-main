#!/bin/bash
# 🚀 Script de Build para Easypanel

set -e

echo "🚀 Construindo Dashboard de Mobilidade Urbana para Easypanel..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando!${NC}"
    exit 1
fi

# Limpar builds anteriores
echo -e "${YELLOW}🧹 Limpando builds anteriores...${NC}"
docker system prune -f >/dev/null 2>&1 || true

# Build da imagem
echo -e "${BLUE}🏗️ Construindo imagem Docker...${NC}"
docker build -t dashboard-mobilidade-urbana:latest . \
    --build-arg NODE_ENV=production \
    --build-arg FLASK_ENV=production

# Verificar se build foi bem-sucedido
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build completado com sucesso!${NC}"
    
    # Mostrar informações da imagem
    echo -e "${BLUE}📊 Informações da imagem:${NC}"
    docker images dashboard-mobilidade-urbana:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    
    echo ""
    echo -e "${GREEN}🎉 Imagem pronta para deploy no Easypanel!${NC}"
    echo -e "${YELLOW}📋 Próximos passos:${NC}"
    echo "   1. Faça push do código para seu repositório Git"
    echo "   2. No Easypanel, crie um novo app usando Git"
    echo "   3. Configure as variáveis de ambiente necessárias"
    echo "   4. O Easypanel irá automaticamente usar o Dockerfile"
    
    echo ""
    echo -e "${BLUE}🔧 Variáveis de ambiente recomendadas para Easypanel:${NC}"
    echo "   FLASK_ENV=production"
    echo "   DATABASE_URL=postgresql://user:pass@host:5432/db"
    echo "   REDIS_URL=redis://host:6379/0"
    echo "   SECRET_KEY=sua_chave_secreta_aqui"
    
else
    echo -e "${RED}❌ Falha no build!${NC}"
    exit 1
fi
