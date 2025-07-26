from fastapi import APIRouter
from backend.app.models.maps import HeatmapResponse, RoutesResponse, GeoAnalysisResponse, TrafficResponse

router = APIRouter()

@router.get("/maps/heatmap", response_model=HeatmapResponse, tags=["Mapas"])
def get_heatmap():
    return HeatmapResponse(points=[{"lat": -23.5, "lng": -46.6, "value": 10}])

@router.get("/maps/routes", response_model=RoutesResponse, tags=["Mapas"])
def get_routes():
    return RoutesResponse(routes=[[{"lat": -23.5, "lng": -46.6}, {"lat": -23.6, "lng": -46.7}]])

@router.get("/maps/geo-analysis", response_model=GeoAnalysisResponse, tags=["Mapas"])
def get_geo_analysis():
    return GeoAnalysisResponse(summary="Análise geográfica simulada", details={"área": 100.0})

@router.get("/maps/traffic", response_model=TrafficResponse, tags=["Mapas"])
def get_traffic():
    return TrafficResponse(forecast=[1.2, 1.5, 1.7], timestamps=["2025-07-24T08:00", "2025-07-24T09:00", "2025-07-24T10:00"])
