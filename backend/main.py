import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.middleware.encoding_middleware import add_encoding_middleware  # DESABILITADO

# Importar módulos da API principais
from app.api import metrics, drivers, dashboard, financeiro, performance, alert, auth  # Voltar para a API real
from app.api import import_ridesdata
from app.api import analise_operacional
from app.api import campanha
from app.api import metas_performance
from app.api import fases_planejamento
from app.api import metas_progressivas
from app.api import driver_personal_details
from app.api import passengers  # NOVO: endpoints para passageiros
from app.api import performance_analytics  # NOVO: endpoints específicos para aba Performance
from app.api import drivers_analytics  # NOVO: endpoints de gráficos para aba Motoristas
from routes import cidades_demografia
from routes import dashboard_executivo
from routes import metas_estrategicas_routes

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
        "https://fastapi.urbanmt.com.br",
        "http://dashbord.urbanmt.com.br",  # HTTP também
        "http://fastapi.urbanmt.com.br"    # HTTP também
    ]

# Em desenvolvimento, permite qualquer origem
if os.getenv("ENVIRONMENT", "development") == "development":
    cors_origins = ["*"]

# LOG de debug para verificar CORS
print(f"🔒 CORS CONFIGURADO - Origens permitidas: {cors_origins}")
print(f"🌍 ENVIRONMENT: {os.getenv('ENVIRONMENT', 'development')}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Adicionar expose_headers
)

# Adicionar middleware para corrigir problemas de codificação
# Middleware de codificação DESABILITADO para evitar Content-Length errors
# add_encoding_middleware(app)

# Incluir rotas principais

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(drivers_analytics.router, prefix="/api", tags=["drivers-analytics"])  # NOVO: analytics de motoristas - DEVE VIR ANTES de drivers.router
app.include_router(drivers.router, prefix="/api/drivers", tags=["drivers"])  # Voltar para API real
app.include_router(driver_personal_details.router, prefix="/api/drivers", tags=["driver-personal-details"])
app.include_router(passengers.router, prefix="/api", tags=["passengers"])  # NOVO: endpoints para passageiros
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(financeiro.router, prefix="/api/financeiro", tags=["financeiro"])
app.include_router(performance.router, prefix="/api/metrics", tags=["performance"])
app.include_router(performance_analytics.router, prefix="/api/analytics", tags=["performance-analytics"])  # NOVO: endpoints específicos para aba Performance
app.include_router(alert.router, prefix="/api/metrics", tags=["alerts"])
app.include_router(import_ridesdata.router, prefix="/api", tags=["importação"])
app.include_router(analise_operacional.router, prefix="/api", tags=["analise-operacional"])
app.include_router(campanha.router, prefix="/api", tags=["campanhas"])
app.include_router(metas_performance.router, prefix="/api/metrics", tags=["metas-performance"])
app.include_router(fases_planejamento.router, prefix="/api", tags=["fases-planejamento"])
app.include_router(metas_progressivas.router, prefix="/api", tags=["metas-progressivas"])
app.include_router(cidades_demografia.router, prefix="/api", tags=["cidades-demografia"])
app.include_router(dashboard_executivo.router, prefix="/api", tags=["dashboard-executivo"])
app.include_router(metas_estrategicas_routes.router, tags=["metas-estrategicas"])

@app.get("/")
async def root():
    return {"message": "Dashboard Mobilidade Urbana API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running correctly"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
