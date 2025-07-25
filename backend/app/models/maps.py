from pydantic import BaseModel
from typing import List, Dict

class HeatmapResponse(BaseModel):
    points: List[Dict[str, float]]  # Ex: [{"lat": -23.5, "lng": -46.6, "value": 10}]

class RoutesResponse(BaseModel):
    routes: List[List[Dict[str, float]]]  # Lista de rotas, cada rota é uma lista de pontos

class GeoAnalysisResponse(BaseModel):
    summary: str
    details: Dict[str, float]

class TrafficResponse(BaseModel):
    forecast: List[float]
    timestamps: List[str]
