from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
from ..database.db import get_db
from pydantic import BaseModel

router = APIRouter()

# ===== MODELOS PYDANTIC =====

class DriversFilters(BaseModel):
    period: Optional[str] = "3_months"
    city: Optional[str] = "all"
    status: Optional[str] = "all"
    performance: Optional[str] = "all"
    revenue_range: Optional[str] = "all"
    order_by: Optional[str] = "rating"

class DriverKPI(BaseModel):
    total_drivers: int
    active_drivers: int
    total_rides: int
    cancelled_rides: int
    avg_hours_online: float
    avg_rating: float
    total_revenue: float
    acceptance_rate: float
    revenue_per_hour: float
    total_distance: float

class DriverDetails(BaseModel):
    driver_id: str
    name: str
    rating: float
    total_rides: int
    cancelled_rides: int
    hours_online: float
    revenue: float
    city: str
    status: str
    performance_category: str

# ===== FUNÇÕES AUXILIARES =====

def calculate_date_range(period: str) -> tuple:
    """Calcula o range de datas baseado no período"""
    today = datetime.now()
    
    if period == "hoje":
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == "7_days":
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == "30_days":
        start_date = today - timedelta(days=30)
        end_date = today
    elif period == "3_months":
        start_date = today - timedelta(days=90)
        end_date = today
    elif period == "6_months":
        start_date = today - timedelta(days=180)
        end_date = today
    elif period == "12_months":
        start_date = today - timedelta(days=365)
        end_date = today
    else:
        start_date = today - timedelta(days=90)
        end_date = today
    
    return start_date, end_date

def process_rides_data(rides_data: list, start_date: datetime, end_date: datetime) -> dict:
    """Processa dados de corridas para calcular métricas"""
    total_rides = 0
    cancelled_rides = 0
    total_revenue = 0.0
    total_distance = 0.0
    
    for ride in rides_data:
        try:
            if not ride.get('drop_time'):
                continue
                
            # Parse formato: "29/07/2025 : 6:00 pm"
            date_part = ride['drop_time'].split(' : ')[0]
            ride_date = datetime.strptime(date_part, '%d/%m/%Y')
            
            if start_date <= ride_date <= end_date:
                total_rides += 1
                
                # Verifica se foi cancelada
                if ride.get('status') == 'cancelled':
                    cancelled_rides += 1
                
                # Soma receita
                if ride.get('total_amount'):
                    total_revenue += float(ride['total_amount'])
                
                # Soma distância
                if ride.get('distance'):
                    total_distance += float(ride['distance'])
                    
        except (ValueError, TypeError, AttributeError):
            continue
    
    return {
        'total_rides': total_rides,
        'cancelled_rides': cancelled_rides,
        'total_revenue': total_revenue,
        'total_distance': total_distance
    }

def get_performance_category(rating: float) -> str:
    """Categoriza performance baseado no rating"""
    if rating >= 4.5:
        return "excellent"
    elif rating >= 4.0:
        return "good"
    elif rating >= 3.5:
        return "medium"
    else:
        return "below"

# ===== ENDPOINTS =====

@router.get("/kpis")
def get_drivers_kpis(
    period: str = Query("3_months", description="Período de análise"),
    city: str = Query("all", description="Filtro por cidade"),
    status: str = Query("all", description="Filtro por status"),
    db: Session = Depends(get_db)
):
    """
    Retorna KPIs dos motoristas com filtros
    """
    try:
        start_date, end_date = calculate_date_range(period)
        
        # Query para buscar motoristas com dados detalhados
        query = """
        SELECT 
            dd.driver_id,
            dd.name,
            dd.email,
            dd.mobile,
            dd.city as dd_city,
            dpd.city as dpd_city,
            dpd.personal_data,
            dpd.rides_history,
            dpd.wallet_transactions
        FROM drivers_data dd
        LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
        """
        
        # Adicionar filtros
        conditions = []
        params = {}
        
        if city != "all":
            conditions.append("(dd.city = :city OR dpd.city = :city)")
            params['city'] = city
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        result = db.execute(text(query), params)
        drivers_data = result.fetchall()
        
        # Processar dados
        total_drivers = len(drivers_data)
        active_drivers = 0
        total_rides = 0
        cancelled_rides = 0
        total_revenue = 0.0
        total_distance = 0.0
        ratings = []
        hours_online = []
        
        for driver in drivers_data:
            # Verificar se tem dados de corridas
            rides_history = None
            if driver.rides_history:
                try:
                    rides_history = json.loads(driver.rides_history) if isinstance(driver.rides_history, str) else driver.rides_history
                except:
                    rides_history = []
            
            if rides_history:
                active_drivers += 1
                
                # Processar corridas do período
                rides_stats = process_rides_data(rides_history, start_date, end_date)
                total_rides += rides_stats['total_rides']
                cancelled_rides += rides_stats['cancelled_rides']
                total_revenue += rides_stats['total_revenue']
                total_distance += rides_stats['total_distance']
                
                # Calcular rating médio das corridas do período
                period_ratings = []
                for ride in rides_history:
                    try:
                        if ride.get('drop_time'):
                            date_part = ride['drop_time'].split(' : ')[0]
                            ride_date = datetime.strptime(date_part, '%d/%m/%Y')
                            if start_date <= ride_date <= end_date and ride.get('rating'):
                                period_ratings.append(float(ride['rating']))
                    except:
                        continue
                
                if period_ratings:
                    ratings.extend(period_ratings)
        
        # Calcular métricas
        avg_rating = sum(ratings) / len(ratings) if ratings else 3.5
        avg_hours_online = sum(hours_online) / len(hours_online) if hours_online else 0.0
        acceptance_rate = ((total_rides - cancelled_rides) / total_rides * 100) if total_rides > 0 else 0.0
        revenue_per_hour = (total_revenue / sum(hours_online)) if sum(hours_online) > 0 else 0.0
        
        return {
            "success": True,
            "data": {
                "total_drivers": total_drivers,
                "active_drivers": active_drivers,
                "total_rides": total_rides,
                "cancelled_rides": cancelled_rides,
                "avg_hours_online": round(avg_hours_online, 1),
                "avg_rating": round(avg_rating, 1),
                "total_revenue": round(total_revenue, 2),
                "acceptance_rate": round(acceptance_rate, 1),
                "revenue_per_hour": round(revenue_per_hour, 2),
                "total_distance": round(total_distance, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar KPIs: {str(e)}")

@router.get("/list")
def get_drivers_list(
    period: str = Query("3_months", description="Período de análise"),
    city: str = Query("all", description="Filtro por cidade"),
    status: str = Query("all", description="Filtro por status"),
    performance: str = Query("all", description="Filtro por performance"),
    revenue_range: str = Query("all", description="Filtro por faixa de receita"),
    order_by: str = Query("rating", description="Ordenação"),
    limit: int = Query(50, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação"),
    db: Session = Depends(get_db)
):
    """
    Retorna lista de motoristas com filtros e paginação
    """
    try:
        start_date, end_date = calculate_date_range(period)
        
        # Query para buscar motoristas
        query = """
        SELECT 
            dd.driver_id,
            dd.name,
            dd.email,
            dd.mobile,
            dd.city as dd_city,
            dpd.city as dpd_city,
            dpd.personal_data,
            dpd.rides_history,
            dpd.wallet_transactions
        FROM drivers_data dd
        LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
        """
        
        # Adicionar filtros
        conditions = []
        params = {}
        
        if city != "all":
            conditions.append("(dd.city = :city OR dpd.city = :city)")
            params['city'] = city
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        result = db.execute(text(query), params)
        drivers_data = result.fetchall()
        
        # Processar e filtrar dados
        processed_drivers = []
        
        for driver in drivers_data:
            rides_history = []
            if driver.rides_history:
                try:
                    rides_history = json.loads(driver.rides_history) if isinstance(driver.rides_history, str) else driver.rides_history
                except:
                    rides_history = []
            
            # Processar corridas do período
            rides_stats = process_rides_data(rides_history, start_date, end_date)
            
            # Calcular rating médio do período
            period_ratings = []
            for ride in rides_history:
                try:
                    if ride.get('drop_time'):
                        date_part = ride['drop_time'].split(' : ')[0]
                        ride_date = datetime.strptime(date_part, '%d/%m/%Y')
                        if start_date <= ride_date <= end_date and ride.get('rating'):
                            period_ratings.append(float(ride['rating']))
                except:
                    continue
            
            avg_rating = sum(period_ratings) / len(period_ratings) if period_ratings else 3.5
            performance_cat = get_performance_category(avg_rating)
            driver_status = "active" if rides_stats['total_rides'] > 0 else "inactive"
            city_name = driver.dpd_city or driver.dd_city or "N/A"
            
            # Aplicar filtros
            if status != "all" and driver_status != status:
                continue
                
            if performance != "all" and performance_cat != performance:
                continue
                
            # Filtro por faixa de receita
            total_revenue = rides_stats['total_revenue']
            if revenue_range != "all":
                if revenue_range == "0-500" and not (0 <= total_revenue <= 500):
                    continue
                elif revenue_range == "500-1000" and not (500 < total_revenue <= 1000):
                    continue
                elif revenue_range == "1000-2000" and not (1000 < total_revenue <= 2000):
                    continue
                elif revenue_range == "2000+" and total_revenue <= 2000:
                    continue
            
            processed_drivers.append({
                "driver_id": driver.driver_id,
                "name": driver.name or "N/A",
                "rating": round(avg_rating, 1),
                "total_rides": rides_stats['total_rides'],
                "cancelled_rides": rides_stats['cancelled_rides'],
                "hours_online": 0.0,  # TODO: calcular horas online
                "revenue": round(total_revenue, 2),
                "city": city_name,
                "status": driver_status,
                "performance_category": performance_cat
            })
        
        # Ordenação
        if order_by == "rating":
            processed_drivers.sort(key=lambda x: x['rating'], reverse=True)
        elif order_by == "rides":
            processed_drivers.sort(key=lambda x: x['total_rides'], reverse=True)
        elif order_by == "revenue":
            processed_drivers.sort(key=lambda x: x['revenue'], reverse=True)
        elif order_by == "name":
            processed_drivers.sort(key=lambda x: x['name'])
        
        # Paginação
        total_count = len(processed_drivers)
        paginated_drivers = processed_drivers[offset:offset + limit]
        
        return {
            "success": True,
            "data": {
                "drivers": paginated_drivers,
                "total_count": total_count,
                "offset": offset,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lista de motoristas: {str(e)}")

@router.get("/cities")
def get_cities_list(db: Session = Depends(get_db)) -> List[str]:
    """
    Retorna lista de cidades disponíveis
    """
    try:
        query = """
        SELECT DISTINCT 
            COALESCE(dpd.city, dd.city) as city
        FROM drivers_data dd
        LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
        WHERE COALESCE(dpd.city, dd.city) IS NOT NULL
        ORDER BY city
        """
        
        result = db.execute(text(query))
        cities = [row[0] for row in result.fetchall() if row[0]]
        
        return {
            "success": True,
            "data": cities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cidades: {str(e)}")

@router.get("/analytics")
def get_drivers_analytics(
    period: str = Query("3_months", description="Período de análise"),
    city: str = Query("all", description="Filtro por cidade"),
    db: Session = Depends(get_db)
):
    """
    Retorna dados analíticos para gráficos e insights
    """
    try:
        start_date, end_date = calculate_date_range(period)
        
        # Query para buscar dados
        query = """
        SELECT 
            dd.driver_id,
            dd.name,
            dd.city as dd_city,
            dpd.city as dpd_city,
            dpd.rides_history
        FROM drivers_data dd
        LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
        """
        
        # Adicionar filtros
        conditions = []
        params = {}
        
        if city != "all":
            conditions.append("(dd.city = :city OR dpd.city = :city)")
            params['city'] = city
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        result = db.execute(text(query))
        drivers_data = result.fetchall()
        
        # Análises
        status_distribution = {"active": 0, "inactive": 0}
        performance_distribution = {"excellent": 0, "good": 0, "medium": 0, "below": 0}
        city_distribution = {}
        
        for driver in drivers_data:
            rides_history = []
            if driver.rides_history:
                try:
                    rides_history = json.loads(driver.rides_history) if isinstance(driver.rides_history, str) else driver.rides_history
                except:
                    rides_history = []
            
            # Status
            rides_stats = process_rides_data(rides_history, start_date, end_date)
            status = "active" if rides_stats['total_rides'] > 0 else "inactive"
            status_distribution[status] += 1
            
            # Performance
            period_ratings = []
            for ride in rides_history:
                try:
                    if ride.get('drop_time') and ride.get('rating'):
                        date_part = ride['drop_time'].split(' : ')[0]
                        ride_date = datetime.strptime(date_part, '%d/%m/%Y')
                        if start_date <= ride_date <= end_date:
                            period_ratings.append(float(ride['rating']))
                except:
                    continue
            
            avg_rating = sum(period_ratings) / len(period_ratings) if period_ratings else 3.5
            performance_cat = get_performance_category(avg_rating)
            performance_distribution[performance_cat] += 1
            
            # Cidade
            city_name = driver.dpd_city or driver.dd_city or "N/A"
            city_distribution[city_name] = city_distribution.get(city_name, 0) + 1
        
        return {
            "success": True,
            "data": {
                "status_distribution": status_distribution,
                "performance_distribution": performance_distribution,
                "city_distribution": city_distribution,
                "period": period,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar analytics: {str(e)}")
