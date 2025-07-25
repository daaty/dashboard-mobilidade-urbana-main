from pydantic import BaseModel

class OverviewMetric(BaseModel):
    name: str
    value: float
    unit: str
