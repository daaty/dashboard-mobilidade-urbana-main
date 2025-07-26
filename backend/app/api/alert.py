from fastapi import APIRouter
from typing import List
from app.models.alert import AlertMetric

router = APIRouter()

@router.get("/alertas", response_model=List[AlertMetric])
def get_alerts():
    # Mock de alertas
    return [
        AlertMetric(id=1, type="sistema", message="API em modo de manutenção", level="info", timestamp="2025-07-24T10:00:00Z"),
        AlertMetric(id=2, type="performance", message="Tempo de resposta acima do esperado", level="warning", timestamp="2025-07-24T09:50:00Z"),
        AlertMetric(id=3, type="segurança", message="Tentativa de acesso não autorizado", level="critical", timestamp="2025-07-24T09:45:00Z"),
    ]
