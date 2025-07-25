from pydantic import BaseModel
from typing import List, Optional

class PredictRequest(BaseModel):
    origem: str
    destino: str
    horario: str  # ISO 8601
    historico_corridas: Optional[List[float]] = None

class PredictResponse(BaseModel):
    previsao_corridas: int
    confianca: float
    mensagem: Optional[str] = None
