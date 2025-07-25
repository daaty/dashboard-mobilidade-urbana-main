from pydantic import BaseModel
from typing import Optional

class RecommendationRequest(BaseModel):
    usuario_id: int
    contexto: Optional[str] = None

class RecommendationResponse(BaseModel):
    recomendacao: str
    score: float
    mensagem: Optional[str] = None
