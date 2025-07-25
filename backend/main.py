

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import metrics, performance, alert, corrida, ia, sentiment, recommendation, anomaly, llm, maps, dashboard, auth


app = FastAPI()

# Adicionar CORS para permitir frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://8tzcwd83-3000.brs.devtunnels.ms"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(performance.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(alert.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(corrida.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(ia.router, prefix="/api/ia", tags=["ia"])
app.include_router(sentiment.router, prefix="/api/ia", tags=["ia"])
app.include_router(recommendation.router, prefix="/api/ia", tags=["ia"])
app.include_router(anomaly.router, prefix="/api/ia", tags=["ia"])
app.include_router(llm.router, prefix="/api/ia", tags=["ia"])
app.include_router(maps.router, prefix="/api/maps", tags=["maps"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
"""
app.include_router(performance.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(alert.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(corrida.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(ia.router, prefix="/api/ia", tags=["ia"])
app.include_router(sentiment.router, prefix="/api/ia", tags=["ia"])
app.include_router(recommendation.router, prefix="/api/ia", tags=["ia"])
app.include_router(anomaly.router, prefix="/api/ia", tags=["ia"])
app.include_router(llm.router, prefix="/api/ia", tags=["ia"])
app.include_router(maps.router, prefix="/api/maps", tags=["maps"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
"""

@app.get("/")
def root():
    return {"message": "FastAPI backend rodando!"}
