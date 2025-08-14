from pydantic import BaseModel, ConfigDict
from typing import Optional

class CidadeDemografiaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    cidade: str
    populacao_censo_2022: Optional[int]
    populacao_estimada_2024: Optional[int]
    densidade_demografica: Optional[float]
    publico_alvo_15_44_anos: Optional[int]
    publico_homens: Optional[int]
    publico_mulheres: Optional[int]
