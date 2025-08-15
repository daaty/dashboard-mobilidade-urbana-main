# 🚀 INSTRUÇÕES PARA EXECUTAR O SISTEMA

## 📋 **PASSO A PASSO:**

### 1️⃣ **Terminal 1 - Backend (FastAPI)**
```powershell
# A partir da raiz do projeto
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxx] using WatchFiles
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2️⃣ **Terminal 2 - Frontend (React/Vite)**
```powershell
# A partir da raiz do projeto
cd frontend
npm run dev
```

**Resultado esperado:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

## 🔍 **VERIFICAR SE ESTÁ FUNCIONANDO:**

### ✅ **Backend (FastAPI):**
- Acesse: http://localhost:8000/docs
- Teste endpoint: http://localhost:8000/api/cidades

### ✅ **Frontend (React):**
- Acesse: http://localhost:3000
- Navegue para: http://localhost:3000/#/metas-cidades

---

## 🎯 **COMANDOS ESPECÍFICOS:**

Para executar APENAS o backend:
```powershell
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Para executar APENAS o frontend:
```powershell
cd frontend && npm run dev
```

---

## 🚨 **TROUBLESHOOTING:**

### Se der erro "Port already in use":
```powershell
# Matar processo na porta 8000
netstat -ano | findstr :8000
taskkill /PID [NUMERO_DO_PID] /F
```

### Se der erro de módulos:
```powershell
# Ativar ambiente virtual
.venv\Scripts\Activate.ps1

# Instalar dependências backend
cd backend && pip install -r requirements.txt

# Instalar dependências frontend  
cd frontend && npm install
```

---

## 📊 **SISTEMA FUNCIONANDO:**

Quando ambos estiverem rodando, você terá:

✅ **37 campanhas** dinâmicas carregadas  
✅ **10 cidades** integradas (7 + 3 importantes)  
✅ **Dashboard 100% dinâmico** sem hardcode  
✅ **Dados reais** das corridas preservados  

🎉 **Sistema pronto para uso!**
