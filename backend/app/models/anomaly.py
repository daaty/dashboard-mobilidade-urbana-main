from pydantic import BaseModel
from typing import List, Optional

class AnomalyDetectionRequest(BaseModel):
    data: List[float]
    threshold: Optional[float] = 2.0

class AnomalyDetectionResponse(BaseModel):
    anomalies: List[int]  # Índices dos pontos anômalos
    scores: List[float]   # Score de anomalia para cada ponto
