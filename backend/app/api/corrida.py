from fastapi import APIRouter
from typing import List
from backend.app.models.corrida import CorridaAnalise

router = APIRouter()

@router.get("/analise-corridas", response_model=List[CorridaAnalise])
def get_analise_corridas():
    # Mock de análise de corridas
    return [
        CorridaAnalise(corrida_id=1, motorista="João", passageiro="Maria", valor=25.5, distancia_km=12.3, duracao_min=22, avaliacao=4.8, status="finalizada"),
        CorridaAnalise(corrida_id=2, motorista="Carlos", passageiro="Ana", valor=18.0, distancia_km=8.7, duracao_min=15, avaliacao=4.5, status="finalizada"),
        CorridaAnalise(corrida_id=3, motorista="Pedro", passageiro="Lucas", valor=32.0, distancia_km=20.1, duracao_min=30, avaliacao=None, status="cancelada"),
    ]
