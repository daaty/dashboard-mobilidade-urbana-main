from fastapi import APIRouter
from typing import List
from backend.app.models.performance import PerformanceMetric

router = APIRouter()

@router.get("/performance", response_model=List[PerformanceMetric])
def get_performance_metrics():
    # Mock de dados de performance
    return [
        PerformanceMetric(name="Tempo Médio de Resposta", value=120, unit="ms"),
        PerformanceMetric(name="Taxa de Erro", value=0.2, unit="%"),
        PerformanceMetric(name="Requisições por Minuto", value=1500, unit="rpm"),
    ]
