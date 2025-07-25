from pydantic import BaseModel
from typing import Optional

class AlertMetric(BaseModel):
    id: int
    type: str
    message: str
    level: str  # ex: 'info', 'warning', 'critical'
    timestamp: Optional[str]
