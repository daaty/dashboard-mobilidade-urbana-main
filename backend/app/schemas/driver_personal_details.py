from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class PersonalDataSchema(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    birth_date: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    
class RideHistorySchema(BaseModel):
    ride_id: Optional[str] = None
    date: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[int] = None
    fare: Optional[float] = None
    status: Optional[str] = None
    rating: Optional[float] = None

class WalletTransactionSchema(BaseModel):
    transaction_id: Optional[str] = None
    date: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    balance_after: Optional[float] = None

class SubscriptionSchema(BaseModel):
    subscription_id: Optional[str] = None
    plan_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None

class DriverPersonalDetailsResponse(BaseModel):
    id: int
    driver_id: str
    city: str
    personal_data: Dict[str, Any]
    rides_history: Optional[List[Dict[str, Any]]] = None
    wallet_transactions: Optional[List[Dict[str, Any]]] = None
    subscription_history: Optional[List[Dict[str, Any]]] = None
    additional_info: Optional[Dict[str, Any]] = None
    extracted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extraction_source: Optional[str] = None
    data_hash: str
    
    class Config:
        from_attributes = True

class DriverSummaryResponse(BaseModel):
    driver_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    city: str
    total_rides: int = 0
    total_earnings: float = 0.0
    average_rating: Optional[float] = None
    status: Optional[str] = None
    last_activity: Optional[datetime] = None
    
class DriversListResponse(BaseModel):
    drivers: List[DriverSummaryResponse]
    total_count: int
    page: int
    limit: int
    
class DriverAnalyticsResponse(BaseModel):
    driver_id: str
    city: str
    personal_data: Dict[str, Any]
    
    # Métricas de corridas
    total_rides: int = 0
    completed_rides: int = 0
    cancelled_rides: int = 0
    completion_rate: float = 0.0
    
    # Métricas financeiras
    total_earnings: float = 0.0
    average_ride_value: float = 0.0
    wallet_balance: Optional[float] = None
    
    # Métricas de performance
    average_rating: Optional[float] = None
    total_distance: float = 0.0
    total_duration: int = 0  # em minutos
    
    # Dados temporais
    first_ride_date: Optional[datetime] = None
    last_ride_date: Optional[datetime] = None
    active_days: int = 0
    
    # Assinatura
    current_subscription: Optional[Dict[str, Any]] = None
