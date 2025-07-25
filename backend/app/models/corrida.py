from pydantic import BaseModel
from typing import Optional

class CorridaAnalise(BaseModel):
    corrida_id: int
    motorista: str
    passageiro: str
    valor: float
    distancia_km: float
    duracao_min: float
    avaliacao: Optional[float]
    status: str
