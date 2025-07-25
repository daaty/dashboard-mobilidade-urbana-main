#!/bin/bash
# 🚀 Script de Deploy Simplificado para Easypanel

set -e

echo "🚀 Preparando deploy do Dashboard de Mobilidade Urbana para Easypanel..."

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Não é um repositório Git!${NC}"
    echo "Execute: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Commit mudanças se necessário
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️ Há mudanças não commitadas${NC}"
    read -p "Fazer commit automaticamente? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
        echo -e "${GREEN}✅ Commit realizado${NC}"
    fi
fi

# Push para repositório
echo -e "${BLUE}📤 Fazendo push...${NC}"
git push origin main

echo ""
echo -e "${GREEN}🎉 Código enviado com sucesso!${NC}"
echo ""
echo -e "${BLUE}📋 Configuração no Easypanel:${NC}"
echo "1. Criar nova aplicação"
echo "2. Deploy from Git"
echo "3. Repository URL: $(git config --get remote.origin.url 2>/dev/null || echo 'SEU_REPO_AQUI')"
echo "4. Branch: main"
echo "5. Dockerfile será usado automaticamente"
echo ""
echo -e "${YELLOW}🔧 Variáveis de ambiente:${NC}"
echo "FLASK_ENV=production"
echo "SECRET_KEY=sua_chave_super_secreta"
echo "DATABASE_URL=postgresql://user:pass@host:5432/db"
echo "REDIS_URL=redis://host:6379/0"
echo ""
echo -e "${GREEN}✅ Pronto para deploy no Easypanel!${NC}"
