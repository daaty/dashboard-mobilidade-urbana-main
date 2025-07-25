from fastapi import APIRouter
from app.models.sentiment import SentimentRequest, SentimentResponse

router = APIRouter()

@router.post("/sentiment", response_model=SentimentResponse)
def analyze_sentiment(payload: SentimentRequest):
    # Mock de análise de sentimento
    return SentimentResponse(
        sentimento="positivo",
        score=0.92,
        mensagem="Análise mockada para teste."
    )
