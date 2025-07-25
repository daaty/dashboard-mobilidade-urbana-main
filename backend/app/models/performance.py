from pydantic import BaseModel

class PerformanceMetric(BaseModel):
    name: str
    value: float
    unit: str
