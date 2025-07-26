from fastapi import APIRouter
from backend.app.models.anomaly import AnomalyDetectionRequest, AnomalyDetectionResponse

router = APIRouter()

@router.post("/ia/anomaly", response_model=AnomalyDetectionResponse, tags=["Inteligência Artificial"])
def detect_anomaly(request: AnomalyDetectionRequest):
    # Mock: detecta valores acima do threshold como anomalias
    anomalies = [i for i, v in enumerate(request.data) if abs(v) > request.threshold]
    scores = [abs(v) for v in request.data]
    return AnomalyDetectionResponse(anomalies=anomalies, scores=scores)
