import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar módulos da API principais
from app.api import metrics, drivers, dashboard, financeiro

app = FastAPI(title="Dashboard Mobilidade Urbana API")

# CORS_ORIGINS do .env ou fallback com domínios de produção
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
else:
    # Fallback para desenvolvimento e produção
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://8tzcwd83-3000.brs.devtunnels.ms",
        "https://dashbord.urbanmt.com.br",
        "https://fastapi.urbanmt.com.br"
    ]

# Em desenvolvimento, permite qualquer origem
if os.getenv("ENVIRONMENT", "development") == "development":
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas principais
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(drivers.router, prefix="/api/drivers", tags=["drivers"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(financeiro.router, prefix="/api/financeiro", tags=["financeiro"])

@app.get("/")
async def root():
    return {"message": "Dashboard Mobilidade Urbana API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running correctly"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
