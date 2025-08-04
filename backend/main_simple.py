"""
Backend simples e funcional para o Dashboard
"""
import sys
import os
sys.path.append('..')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar os módulos da API
from app.api.metrics import router as metrics_router
from app.api.drivers import router as drivers_router  
from app.api.dashboard import router as dashboard_router
from app.api.financeiro import router as financeiro_router

# Criar aplicação FastAPI
app = FastAPI(title="Dashboard Mobilidade Urbana API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])
app.include_router(drivers_router, prefix="/api/drivers", tags=["drivers"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(financeiro_router, prefix="/api/financeiro", tags=["financeiro"])

@app.get("/")
async def root():
    return {"message": "Dashboard API funcionando!", "status": "OK"}

@app.get("/health")
async def health():
    return {"status": "healthy", "api": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
