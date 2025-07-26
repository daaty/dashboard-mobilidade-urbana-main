from fastapi import APIRouter
from backend.app.models.recommendation import RecommendationRequest, RecommendationResponse

router = APIRouter()

@router.post("/recommendation", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest):
    # Mock de recomendação
    return RecommendationResponse(
        recomendacao="Sugestão: aumentar frota no horário de pico.",
        score=0.78,
        mensagem="Recomendação mockada para teste."
    )
