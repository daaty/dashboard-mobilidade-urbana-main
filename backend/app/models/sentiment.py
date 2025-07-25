from pydantic import BaseModel
from typing import Optional

class SentimentRequest(BaseModel):
    texto: str

class SentimentResponse(BaseModel):
    sentimento: str  # ex: 'positivo', 'negativo', 'neutro'
    score: float
    mensagem: Optional[str] = None
