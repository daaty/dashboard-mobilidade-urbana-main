from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class CampanhaBase(BaseModel):
    nome: str
    fase: str
    cidade: Optional[str] = None  # Allow None for campaigns without city
    data_inicio: date
    data_fim: date
    tipo_campanha: str
    meta_quantidade: int
    orcamento_previsto: float
    custo_real: Optional[float] = 0
    status: Optional[str] = 'ativa'

class CampanhaCreate(CampanhaBase):
    pass

class CampanhaUpdate(CampanhaBase):
    pass

class CampanhaOut(CampanhaBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
