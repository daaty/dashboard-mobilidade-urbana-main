from fastapi import APIRouter
from backend.app.models.ia import PredictRequest, PredictResponse

router = APIRouter()

@router.post("/predict", response_model=PredictResponse)
def predict_demand(payload: PredictRequest):
    # Mock de previsão
    return PredictResponse(
        previsao_corridas=42,
        confianca=0.87,
        mensagem="Previsão mockada para teste."
    )
