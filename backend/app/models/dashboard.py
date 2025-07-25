from pydantic import BaseModel
from typing import Dict, Any

class FinanceiroResponse(BaseModel):
    receita_total: float
    despesas: float
    lucro: float

class OperacionalResponse(BaseModel):
    viagens: int
    frota_ativa: int
    km_rodados: float

class ExecutivoResponse(BaseModel):
    resumo: str
    indicadores: Dict[str, Any]

class PreditivoResponse(BaseModel):
    previsao_receita: float
    previsao_viagens: int
