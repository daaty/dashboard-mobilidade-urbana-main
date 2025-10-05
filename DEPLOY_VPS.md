# 🚀 GUIA DE DEPLOY NA VPS

## 1️⃣ Fazer commit e push das mudanças

```bash
git add .
git commit -m "fix: corrigir CORS para produção e motoristas ativos"
git push origin dashboard-executivo-styling
```

## 2️⃣ Na VPS, fazer pull das mudanças

```bash
cd /caminho/do/projeto
git pull origin dashboard-executivo-styling
```

## 3️⃣ Configurar variáveis de ambiente na VPS

Crie ou edite o arquivo `.env` no diretório `backend/`:

```bash
cd backend
nano .env
```

Cole o conteúdo (IMPORTANTE - use o .env.production como base):

```env
ENVIRONMENT=production
CORS_ORIGINS=https://dashbord.urbanmt.com.br,https://fastapi.urbanmt.com.br
DB_HOST=148.230.73.27
DB_PORT=5432
DB_NAME=n8n_db
DB_USER=n8n_user
DB_PASSWORD=n8n_pw
JWT_SECRET=seu_secret_key_super_seguro_aqui_producao
```

Salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

## 4️⃣ Reiniciar o backend

Se estiver usando **PM2**:
```bash
pm2 restart fastapi
pm2 logs fastapi
```

Se estiver usando **systemd**:
```bash
sudo systemctl restart fastapi
sudo systemctl status fastapi
```

Se estiver rodando manualmente:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 5️⃣ Verificar logs

Procure pela linha:
```
🔒 CORS CONFIGURADO - Origens permitidas: ['https://dashbord.urbanmt.com.br', ...]
```

## 6️⃣ Testar no navegador

1. Acesse https://dashbord.urbanmt.com.br
2. Tente fazer login
3. Se ainda der erro de CORS, verifique:
   - O backend está rodando em HTTPS? (deve ser fastapi.urbanmt.com.br com SSL)
   - O Nginx/Apache está configurado corretamente?
   - As variáveis de ambiente estão corretas?

## 🔧 SOLUÇÃO RÁPIDA - Se ainda não funcionar

Adicione temporariamente no backend/main.py (linha ~41):

```python
# TEMPORÁRIO - Permitir todas as origens
cors_origins = ["*"]
```

Isso vai funcionar imediatamente, mas não é seguro para produção final.

## 🎯 VERIFICAR NGINX (se estiver usando)

O Nginx pode estar bloqueando CORS. Adicione no arquivo de configuração:

```nginx
location /api {
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
    
    if ($request_method = 'OPTIONS') {
        return 204;
    }
    
    proxy_pass http://localhost:8000;
}
```

Depois:
```bash
sudo nginx -t
sudo systemctl reload nginx
```
