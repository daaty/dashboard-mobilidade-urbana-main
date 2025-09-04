from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json

router = APIRouter()

@router.get("/kpis")
def get_simple_kpis():
    """Endpoint ultra simples para KPIs"""
    data = {
        "success": True,
        "data": {
            "total_drivers": 118,
            "active_drivers": 8,
            "inactive_drivers": 110,
            "online_drivers": 5,
            "total_rides": 13,
            "cancelled_rides": 0,
            "total_rides_completed": 13,
            "avg_hours_online": 0.3,
            "avg_rating": 4.6,
            "average_rating": 4.6,
            "total_revenue": 195.0,
            "acceptance_rate": 100.0,
            "revenue_per_hour": 6.0,
            "total_distance": 0.0,
            "avg_rides_per_driver": 0.1,
            "total_online_hours": 2.4,
            "kpi_metrics": {
                "activation_rate": 6.8,
                "excellence_rate": 100.0,
                "performance_trend": "stable",
                "efficiency_score": 85
            },
            "performance_metrics": {
                "excellent_drivers": 3,
                "good_drivers": 4,
                "average_drivers": 1,
                "below_average_drivers": 0
            },
            "drivers_by_status": {
                "ativo": 8,
                "inativo": 110
            }
        }
    }
    
    return JSONResponse(content=data)

@router.get("/list")
def get_simple_drivers():
    """Endpoint ultra simples para lista de motoristas"""
    data = {
        "success": True,
        "data": {
            "drivers": [
                {
                    "driver_id": "17147322",
                    "name": "João Silva",
                    "rating": 4.8,
                    "total_rides": 5,
                    "cancelled_rides": 0,
                    "hours_online": 1.2,
                    "revenue": 75.0,
                    "city": "São Paulo",
                    "status": "active",
                    "performance_category": "excellent",
                    "data": {
                        "metrics": {
                            "online_hours": 1.2,
                            "user_cancelled": 0,
                            "driver_cancelled": 0,
                            "total_rides": 5
                        }
                    }
                },
                {
                    "driver_id": "17147323",
                    "name": "Maria Santos",
                    "rating": 4.5,
                    "total_rides": 3,
                    "cancelled_rides": 0,
                    "hours_online": 0.8,
                    "revenue": 45.0,
                    "city": "Rio de Janeiro",
                    "status": "active",
                    "performance_category": "good",
                    "data": {
                        "metrics": {
                            "online_hours": 0.8,
                            "user_cancelled": 0,
                            "driver_cancelled": 0,
                            "total_rides": 3
                        }
                    }
                }
            ],
            "total_count": 118,
            "offset": 0,
            "limit": 50
        }
    }
    
    return JSONResponse(content=data)

@router.get("/cities")
def get_simple_cities():
    """Endpoint ultra simples para cidades"""
    data = {
        "success": True,
        "data": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador"]
    }
    
    return JSONResponse(content=data)
