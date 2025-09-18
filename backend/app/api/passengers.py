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

class PassengerFilters(BaseModel):
    period: Optional[str] = "3_months"
    city: Optional[str] = "all"
    status: Optional[str] = "all"
    order_by: Optional[str] = "rides_count"

class PassengerKPI(BaseModel):
    total_passengers: int
    active_passengers: int
    total_rides: int
    total_revenue: float
    avg_rides_per_passenger: float
    avg_revenue_per_passenger: float
    avg_rating: float
    cities_count: int
    registered_this_month: int
    blocked_passengers: int

class PassengerDetails(BaseModel):
    passenger_id: str
    user_name: Optional[str]
    user_email: Optional[str]
    user_phone: Optional[str]
    city: str
    total_rides: int
    total_spent: float
    avg_rating: Optional[float]
    date_registered: Optional[str]
    status: str
    app_version: Optional[str]
    device_type: Optional[str]

class PassengerUpdateData(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None  
    user_phone: Optional[str] = None
    city: Optional[str] = None
    blocked: Optional[str] = None  # "Yes" ou "No"

class CityDistribution(BaseModel):
    city: str
    passenger_count: int
    total_rides: int
    total_revenue: float
    avg_rides_per_passenger: float
    percentage: float
    new_passengers_count: int
    new_passengers_percentage: float

# ===== FUNÇÕES AUXILIARES =====

def normalize_city_name(city_name: str) -> str:
    """Normaliza nomes de cidades para lidar com problemas de codificação e comparação"""
    if not city_name or city_name.strip() == '' or city_name.strip().upper() == 'N/A':
        return "Não informado"
    
    city_name = city_name.strip()
    
    # Correções específicas para problemas de codificação conhecidos
    replacements = {
        'Guarant� do Norte': 'Guarantã do Norte',
        'Matup�': 'Matupá',
        '�': 'ã',  # Correção geral para caracteres mal codificados
    }
    
    for old, new in replacements.items():
        city_name = city_name.replace(old, new)
    
    # Normalização para comparação: converter para maiúsculo e remover acentos
    city_name = city_name.upper()
    accent_replacements = {
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C',
        'Ñ': 'N'
    }
    
    for old, new in accent_replacements.items():
        city_name = city_name.replace(old, new)
    
    return city_name

def calculate_date_range(period: str) -> tuple:
    """Calcula o range de datas baseado no período"""
    today = datetime.now()
    
    if period == "today" or period == "hoje":
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == "7_days":
        start_date = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == "30_days":
        start_date = (today - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == "3_months":
        start_date = (today - timedelta(days=150)).replace(hour=0, minute=0, second=0, microsecond=0)  # Ampliado para incluir dados históricos
        end_date = today
    elif period == "6_months":
        start_date = (today - timedelta(days=180)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == "12_months":
        start_date = (today - timedelta(days=365)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == "all_time":
        start_date = datetime(2020, 1, 1)  # Data muito antiga para incluir tudo
        end_date = today
    else:
        start_date = (today - timedelta(days=150)).replace(hour=0, minute=0, second=0, microsecond=0)  # Padrão ampliado
        end_date = today
    
    return start_date, end_date

def count_new_passengers(personal_data_list: list, start_date: datetime, end_date: datetime) -> int:
    """Conta passageiros registrados no período especificado"""
    new_count = 0
    
    for personal_data in personal_data_list:
        if not personal_data:
            continue
            
        date_registered = personal_data.get('date_registered')
        if not date_registered:
            continue
            
        try:
            # Parse da data: "DD/MM/YYYY" ou "DD/MM/YYYY HH:MM"
            date_str = date_registered.split(' ')[0]  # Remove horário se houver
            reg_date = datetime.strptime(date_str, '%d/%m/%Y')
            
            if start_date <= reg_date <= end_date:
                new_count += 1
        except Exception:
            # Se não conseguir parsear a data, ignora
            continue
    
    return new_count

def process_rides_history(rides_history: list, start_date: datetime = None, end_date: datetime = None) -> dict:
    """Processa histórico de corridas de um passageiro"""
    if not rides_history:
        return {"total_rides": 0, "total_revenue": 0.0, "avg_rating": 0.0, "avg_distance": 0.0}
    
    total_rides = 0
    total_revenue = 0.0
    total_distance = 0.0
    ratings = []
    
    for ride in rides_history:
        try:
            # Parse da data: "18/08/2025 12:12 pm"
            date_str = ride.get('date', '')
            if date_str and start_date and end_date:
                try:
                    ride_date = datetime.strptime(date_str.split(' ')[0], '%d/%m/%Y')
                    if not (start_date <= ride_date <= end_date):
                        continue
                except:
                    pass  # Se não conseguir parsear a data, inclui mesmo assim
            
            total_rides += 1
            
            # Processar valor da corrida
            user_fare = ride.get('user_fare', '0')
            try:
                fare = float(str(user_fare).replace(',', '.'))
                total_revenue += fare
            except:
                pass
            
            # Processar distância
            ride_distance = ride.get('ride_distance', '0')
            try:
                distance = float(str(ride_distance).replace(',', '.'))
                total_distance += distance
            except:
                pass
            
            # Processar rating
            user_rating = ride.get('user_rating', '--')
            if user_rating != '--' and '/' in str(user_rating):
                try:
                    rating = float(str(user_rating).split('/')[0])
                    ratings.append(rating)
                except:
                    pass
                    
        except Exception as e:
            continue
    
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    avg_distance = total_distance / total_rides if total_rides > 0 else 0.0
    
    return {
        "total_rides": total_rides,
        "total_revenue": total_revenue,
        "avg_rating": avg_rating,
        "avg_distance": avg_distance
    }

def extract_personal_data_info(personal_data: dict) -> dict:
    """Extrai informações importantes do personal_data JSONB"""
    if not personal_data:
        return {}
    
    return {
        "user_name": personal_data.get('user_name'),
        "user_email": personal_data.get('user_email'),
        "user_phone": personal_data.get('user_phone'),
        "date_registered": personal_data.get('date_registered'),
        "app_version": personal_data.get('app_version'),
        "device_type": personal_data.get('device_type'),
        "blocked": personal_data.get('blocked', 'No') == 'Yes',
        "os_version": personal_data.get('os_version'),
        "internal_wallet_balance": personal_data.get('internal_wallet_balance', '0')
    }

# ===== ENDPOINTS =====

@router.get("/passengers/kpis", response_model=PassengerKPI)
async def get_passengers_kpis(
    period: str = Query("3_months", description="Período: today, 7_days, 30_days, 3_months, 6_months, 12_months"),
    city: str = Query("all", description="Cidade específica ou 'all'"),
    db: Session = Depends(get_db)
):
    """Retorna KPIs principais dos passageiros"""
    try:
        start_date, end_date = calculate_date_range(period)
        
        # Query base
        city_filter = f"AND city = '{city}'" if city != "all" else ""
        
        query = text(f"""
            SELECT 
                COUNT(*) as total_passengers,
                SUM(CASE 
                    WHEN personal_data->>'blocked' = 'No' 
                    AND jsonb_array_length(COALESCE(rides_history, '[]'::jsonb)) > 0 
                    THEN 1 ELSE 0 
                END) as active_passengers,
                COUNT(DISTINCT COALESCE(NULLIF(TRIM(personal_data->>'city'), ''), 'Não informado')) as cities_count,
                SUM(CASE 
                    WHEN personal_data->>'blocked' = 'Yes' 
                    THEN 1 ELSE 0 
                END) as blocked_passengers
            FROM passenger_personal_details 
            WHERE personal_data->>'city' IS NOT NULL 
            AND personal_data->>'city' != ''
            AND UPPER(personal_data->>'city') != 'N/A'
            AND TRIM(personal_data->>'city') != ''
            {city_filter}
        """)
        
        result = db.execute(query).fetchone()
        
        # Calcular métricas de corridas e receita processando os dados JSONB
        rides_query = text(f"""
            SELECT rides_history, personal_data
            FROM passenger_personal_details 
            WHERE rides_history IS NOT NULL 
            AND jsonb_array_length(rides_history) > 0
            AND personal_data->>'city' IS NOT NULL 
            AND personal_data->>'city' != ''
            AND UPPER(personal_data->>'city') != 'N/A'
            AND TRIM(personal_data->>'city') != ''
            {city_filter}
        """)
        
        rides_results = db.execute(rides_query).fetchall()
        
        total_rides = 0
        total_revenue = 0.0
        all_ratings = []
        registered_this_month = 0
        
        for row in rides_results:
            rides_data = process_rides_history(row.rides_history, start_date, end_date)
            total_rides += rides_data["total_rides"]
            total_revenue += rides_data["total_revenue"]
            
            if rides_data["avg_rating"] > 0:
                all_ratings.append(rides_data["avg_rating"])
            
            # Verificar registros do mês atual
            personal_info = extract_personal_data_info(row.personal_data)
            if personal_info.get('date_registered'):
                try:
                    # Assumindo formato de data brasileiro: DD/MM/YYYY
                    reg_date = datetime.strptime(personal_info['date_registered'].split(' ')[0], '%d/%m/%Y')
                    if reg_date.month == datetime.now().month and reg_date.year == datetime.now().year:
                        registered_this_month += 1
                except:
                    pass
        
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0.0
        avg_rides_per_passenger = total_rides / result.total_passengers if result.total_passengers > 0 else 0.0
        avg_revenue_per_passenger = total_revenue / result.total_passengers if result.total_passengers > 0 else 0.0
        
        return PassengerKPI(
            total_passengers=result.total_passengers,
            active_passengers=result.active_passengers,
            total_rides=total_rides,
            total_revenue=total_revenue,
            avg_rides_per_passenger=avg_rides_per_passenger,
            avg_revenue_per_passenger=avg_revenue_per_passenger,
            avg_rating=avg_rating,
            cities_count=result.cities_count,
            registered_this_month=registered_this_month,
            blocked_passengers=result.blocked_passengers
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar KPIs dos passageiros: {str(e)}")

@router.get("/passengers/by-city", response_model=List[CityDistribution])
async def get_passengers_by_city(
    period: str = Query("3_months", description="Período para análise de corridas"),
    db: Session = Depends(get_db)
):
    """Retorna distribuição de passageiros por cidade"""
    try:
        start_date, end_date = calculate_date_range(period)
        
        # Buscar dados por cidade
        query = text("""
            SELECT 
                COALESCE(NULLIF(TRIM(personal_data->>'city'), ''), 'Não informado') as raw_city,
                COUNT(DISTINCT passenger_id) as passenger_count
            FROM passenger_personal_details
            WHERE personal_data->>'city' IS NOT NULL 
            AND personal_data->>'city' != ''
            AND UPPER(personal_data->>'city') != 'N/A'
            AND TRIM(personal_data->>'city') != ''
            GROUP BY raw_city
            ORDER BY passenger_count DESC
        """)
        
        city_results = db.execute(query).fetchall()
        total_passengers = sum(row.passenger_count for row in city_results)
        
        # Para cada cidade, processar as corridas usando a mesma lógica do KPIs
        city_distributions = []
        
        for city_row in city_results:
            # Buscar dados de corridas para esta cidade
            rides_query = text("""
                SELECT rides_history, personal_data
                FROM passenger_personal_details 
                WHERE rides_history IS NOT NULL 
                AND jsonb_array_length(rides_history) > 0
                AND personal_data->>'city' IS NOT NULL 
                AND personal_data->>'city' != ''
                AND UPPER(personal_data->>'city') != 'N/A'
                AND TRIM(personal_data->>'city') != ''
                AND COALESCE(NULLIF(TRIM(personal_data->>'city'), ''), 'Não informado') = :city
            """)
            
            rides_results = db.execute(rides_query, {"city": city_row.raw_city}).fetchall()
            
            total_rides = 0
            total_revenue = 0.0
            personal_data_list = []
            
            for row in rides_results:
                rides_data = process_rides_history(row.rides_history, start_date, end_date)
                total_rides += rides_data["total_rides"]
                total_revenue += rides_data["total_revenue"]
                personal_data_list.append(row.personal_data)
            
            # Buscar TODOS os dados pessoais desta cidade (incluindo quem não tem corridas)
            all_personal_query = text("""
                SELECT personal_data
                FROM passenger_personal_details 
                WHERE personal_data->>'city' IS NOT NULL 
                AND personal_data->>'city' != ''
                AND UPPER(personal_data->>'city') != 'N/A'
                AND TRIM(personal_data->>'city') != ''
                AND COALESCE(NULLIF(TRIM(personal_data->>'city'), ''), 'Não informado') = :city
            """)
            
            all_personal_results = db.execute(all_personal_query, {"city": city_row.raw_city}).fetchall()
            all_personal_data = [row.personal_data for row in all_personal_results]
            
            # Calcular novos passageiros
            new_passengers = count_new_passengers(all_personal_data, start_date, end_date)
            new_passengers_pct = (new_passengers / city_row.passenger_count * 100) if city_row.passenger_count > 0 else 0.0
            
            # Normalizar nome da cidade
            normalized_city = normalize_city_name(city_row.raw_city)
            
            avg_rides = total_rides / city_row.passenger_count if city_row.passenger_count > 0 else 0.0
            percentage = (city_row.passenger_count / total_passengers * 100) if total_passengers > 0 else 0.0
            
            city_distributions.append(CityDistribution(
                city=normalized_city,
                passenger_count=city_row.passenger_count,
                total_rides=total_rides,
                total_revenue=total_revenue,
                avg_rides_per_passenger=avg_rides,
                percentage=percentage,
                new_passengers_count=new_passengers,
                new_passengers_percentage=new_passengers_pct
            ))
        
        return city_distributions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar distribuição por cidade: {str(e)}")

@router.get("/passengers/list", response_model=List[PassengerDetails])
async def get_passengers_list(
    city: str = Query("all", description="Cidade específica ou 'all'"),
    search: str = Query("", description="Buscar por nome do passageiro"),
    limit: int = Query(50, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação"),
    order_by: str = Query("rides_count", description="Ordenar por: rides_count, revenue, registration_date"),
    db: Session = Depends(get_db)
):
    """Retorna lista de passageiros com detalhes"""
    try:
        # Buscar todos os passageiros sem limite para permitir filtros completos
        query = text("""
            SELECT 
                passenger_id,
                city,
                personal_data,
                rides_history
            FROM passenger_personal_details 
            ORDER BY passenger_id DESC
        """)
        
        results = db.execute(query).fetchall()
        
        # Aplicar filtro por cidade se necessário
        if city != "all":
            filtered_results = []
            normalized_city_param = normalize_city_name(city)
            for row in results:
                row_city_normalized = normalize_city_name(row.city or "")
                if row_city_normalized == normalized_city_param:
                    filtered_results.append(row)
            results = filtered_results
        
        passengers = []
        for row in results:
            personal_info = extract_personal_data_info(row.personal_data or {})
            rides_data = process_rides_history(row.rides_history or [])
            
            passenger = PassengerDetails(
                passenger_id=row.passenger_id,
                user_name=personal_info.get('user_name'),
                user_email=personal_info.get('user_email'),
                user_phone=personal_info.get('user_phone'),
                city=row.city or "N/A",
                total_rides=rides_data["total_rides"],
                total_spent=rides_data["total_revenue"],
                avg_rating=rides_data["avg_rating"] if rides_data["avg_rating"] > 0 else None,
                date_registered=personal_info.get('date_registered'),
                status="Bloqueado" if personal_info.get('blocked') == 'Yes' else "Ativo",
                app_version=personal_info.get('app_version'),
                device_type=personal_info.get('device_type')
            )
            passengers.append(passenger)
        
        # Aplicar filtro por busca de nome se necessário
        if search.strip():
            search_normalized = search.strip().lower()
            filtered_passengers = []
            for passenger in passengers:
                passenger_name = passenger.user_name or ""
                if search_normalized in passenger_name.lower():
                    filtered_passengers.append(passenger)
            passengers = filtered_passengers
        
        # Ordenar baseado no parâmetro
        if order_by == "rides_count":
            passengers.sort(key=lambda x: x.total_rides, reverse=True)
        elif order_by == "revenue":
            passengers.sort(key=lambda x: x.total_spent, reverse=True)
        elif order_by == "registration_date":
            passengers.sort(key=lambda x: x.date_registered or "", reverse=True)
        
        # Aplicar paginação após todos os filtros
        start_index = offset
        end_index = offset + limit
        passengers = passengers[start_index:end_index]
        
        return passengers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lista de passageiros: {str(e)}")

@router.get("/passengers/top-performers")
async def get_top_performing_passengers(
    metric: str = Query("rides", description="Métrica: rides, revenue, rating"),
    limit: int = Query(10, description="Número de top passageiros"),
    period: str = Query("3_months", description="Período de análise"),
    db: Session = Depends(get_db)
):
    """Retorna top passageiros por diferentes métricas"""
    try:
        start_date, end_date = calculate_date_range(period)
        
        query = text("""
            SELECT 
                passenger_id,
                city,
                personal_data,
                rides_history
            FROM passenger_personal_details 
            WHERE rides_history IS NOT NULL 
            AND jsonb_array_length(rides_history) > 0
        """)
        
        results = db.execute(query).fetchall()
        
        passengers_data = []
        for row in results:
            personal_info = extract_personal_data_info(row.personal_data or {})
            rides_data = process_rides_history(row.rides_history, start_date, end_date)
            
            # Só incluir passageiros com atividade no período
            if rides_data["total_rides"] > 0:
                passenger_info = {
                    "passenger_id": row.passenger_id,
                    "user_name": personal_info.get('user_name', f"Passageiro {row.passenger_id}"),
                    "city": row.city,
                    "total_rides": rides_data["total_rides"],
                    "total_revenue": rides_data["total_revenue"],
                    "avg_rating": rides_data["avg_rating"],
                    "avg_distance": rides_data["avg_distance"]
                }
                passengers_data.append(passenger_info)
        
        # Ordenar baseado na métrica escolhida
        if metric == "rides":
            passengers_data.sort(key=lambda x: x["total_rides"], reverse=True)
        elif metric == "revenue":
            passengers_data.sort(key=lambda x: x["total_revenue"], reverse=True)
        elif metric == "rating":
            passengers_data = [p for p in passengers_data if p["avg_rating"] > 0]
            passengers_data.sort(key=lambda x: x["avg_rating"], reverse=True)
        
        return passengers_data[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar top passageiros: {str(e)}")

@router.get("/passengers/analytics")
async def get_passengers_analytics(
    period: str = Query("3_months", description="Período de análise"),
    city: str = Query("all", description="Cidade específica ou 'all'"),
    db: Session = Depends(get_db)
):
    """Retorna analytics avançados dos passageiros"""
    try:
        start_date, end_date = calculate_date_range(period)
        city_filter = "AND city = :city" if city != "all" else ""
        
        # Query base
        query = text(f"""
            SELECT 
                personal_data,
                rides_history,
                city
            FROM passenger_personal_details 
            WHERE rides_history IS NOT NULL 
            AND jsonb_array_length(rides_history) > 0
            {city_filter}
        """)
        
        params = {}
        if city != "all":
            params["city"] = city
            
        results = db.execute(query, params).fetchall()
        
        # Processar analytics
        total_rides = 0
        total_revenue = 0.0
        payment_methods = {}
        device_types = {}
        ratings_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        distance_ranges = {"0-5km": 0, "5-10km": 0, "10-20km": 0, "20km+": 0}
        revenue_ranges = {"0-50": 0, "50-100": 0, "100-200": 0, "200+": 0}
        
        for row in results:
            personal_info = extract_personal_data_info(row.personal_data or {})
            rides_data = process_rides_history(row.rides_history, start_date, end_date)
            
            if rides_data["total_rides"] > 0:
                total_rides += rides_data["total_rides"]
                total_revenue += rides_data["total_revenue"]
                
                # Análise de device types
                device = personal_info.get('device_type', 'Unknown')
                device_types[device] = device_types.get(device, 0) + 1
                
                # Análise detalhada das corridas
                for ride in (row.rides_history or []):
                    # Método de pagamento
                    preferred_mode = ride.get('preferred_mode', 'Unknown')
                    payment_methods[preferred_mode] = payment_methods.get(preferred_mode, 0) + 1
                    
                    # Rating
                    user_rating = ride.get('user_rating', '--')
                    if user_rating != '--' and '/' in str(user_rating):
                        try:
                            rating = int(float(str(user_rating).split('/')[0]))
                            if 1 <= rating <= 5:
                                ratings_distribution[rating] += 1
                        except:
                            pass
                    
                    # Distância
                    try:
                        distance = float(str(ride.get('ride_distance', '0')).replace(',', '.'))
                        if distance < 5:
                            distance_ranges["0-5km"] += 1
                        elif distance < 10:
                            distance_ranges["5-10km"] += 1
                        elif distance < 20:
                            distance_ranges["10-20km"] += 1
                        else:
                            distance_ranges["20km+"] += 1
                    except:
                        pass
                    
                    # Receita por corrida
                    try:
                        fare = float(str(ride.get('user_fare', '0')).replace(',', '.'))
                        if fare < 50:
                            revenue_ranges["0-50"] += 1
                        elif fare < 100:
                            revenue_ranges["50-100"] += 1
                        elif fare < 200:
                            revenue_ranges["100-200"] += 1
                        else:
                            revenue_ranges["200+"] += 1
                    except:
                        pass
        
        return {
            "summary": {
                "total_rides": total_rides,
                "total_revenue": total_revenue,
                "avg_revenue_per_ride": total_revenue / total_rides if total_rides > 0 else 0,
                "period": period,
                "city": city
            },
            "payment_methods": dict(sorted(payment_methods.items(), key=lambda x: x[1], reverse=True)),
            "device_types": dict(sorted(device_types.items(), key=lambda x: x[1], reverse=True)),
            "ratings_distribution": ratings_distribution,
            "distance_ranges": distance_ranges,
            "revenue_ranges": revenue_ranges
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar analytics: {str(e)}")

@router.get("/passengers/{passenger_id}")
async def get_passenger_details(
    passenger_id: str,
    db: Session = Depends(get_db)
):
    """Retorna detalhes completos de um passageiro específico"""
    try:
        query = text("""
            SELECT *
            FROM passenger_personal_details 
            WHERE passenger_id = :passenger_id
        """)
        
        result = db.execute(query, {"passenger_id": passenger_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Passageiro não encontrado")
        
        personal_info = extract_personal_data_info(result.personal_data or {})
        rides_data = process_rides_history(result.rides_history or [])
        
        return {
            "passenger_id": result.passenger_id,
            "personal_info": personal_info,
            "city": result.city,
            "rides_summary": rides_data,
            "rides_history": result.rides_history or [],
            "registration_info": {
                "extracted_at": result.extracted_at.isoformat() if result.extracted_at else None,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None,
                "extraction_source": result.extraction_source
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar detalhes do passageiro: {str(e)}")

@router.get("/passengers/find-personal-data/{passenger_id}")
async def find_passenger_personal_data(
    passenger_id: str,
    db: Session = Depends(get_db)
):
    """Endpoint para encontrar dados pessoais de um passageiro específico"""
    try:
        query = text("""
            SELECT *
            FROM passenger_personal_details
            WHERE passenger_id = :passenger_id
        """)
        
        result = db.execute(query, {"passenger_id": passenger_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Dados pessoais não encontrados para passenger_id {passenger_id}")
        
        # Parse dos dados pessoais
        personal_data = result.personal_data
        if isinstance(personal_data, str):
            try:
                personal_data = json.loads(personal_data)
            except json.JSONDecodeError:
                personal_data = {}
        
        # Retornar dados no formato esperado pelo frontend
        return {
            "passenger_id": result.passenger_id,
            "personal_driver_id": result.passenger_id,  # Para compatibilidade
            "analytics_passenger_id": result.passenger_id,
            "city": result.city,
            "personal_data": personal_data,
            "extraction_source": result.extraction_source,
            "extracted_at": result.extracted_at.isoformat() if result.extracted_at else None,
            "updated_at": result.updated_at.isoformat() if result.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados pessoais do passageiro: {str(e)}")

@router.put("/passengers/{passenger_id}")
async def update_passenger(
    passenger_id: str,
    update_data: PassengerUpdateData,
    db: Session = Depends(get_db)
):
    """Atualiza dados de um passageiro específico"""
    try:
        # Buscar o passageiro existente
        query = text("""
            SELECT passenger_id, city, personal_data, extraction_source, extracted_at, updated_at
            FROM passenger_personal_details 
            WHERE passenger_id = :passenger_id
        """)
        
        result = db.execute(query, {"passenger_id": passenger_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Passageiro não encontrado: {passenger_id}")
        
        # Parse dos dados pessoais existentes
        personal_data = result.personal_data
        if isinstance(personal_data, str):
            try:
                personal_data = json.loads(personal_data)
            except json.JSONDecodeError:
                personal_data = {}
        
        # Atualizar apenas os campos fornecidos
        updates = {}
        if update_data.city is not None:
            updates["city"] = update_data.city
            
        # Atualizar campos nos personal_data
        if update_data.user_name is not None:
            personal_data["user_name"] = update_data.user_name
        if update_data.user_email is not None:
            personal_data["user_email"] = update_data.user_email
        if update_data.user_phone is not None:
            personal_data["user_phone"] = update_data.user_phone
        if update_data.blocked is not None:
            personal_data["blocked"] = update_data.blocked
            
        # Sempre atualizar personal_data e updated_at
        updates["personal_data"] = json.dumps(personal_data)
        updates["updated_at"] = datetime.now()
        
        # Construir a query de update dinamicamente
        set_clause = ", ".join([f"{key} = :{key}" for key in updates.keys()])
        update_query = text(f"""
            UPDATE passenger_personal_details 
            SET {set_clause}
            WHERE passenger_id = :passenger_id
        """)
        
        # Adicionar passenger_id aos parâmetros
        updates["passenger_id"] = passenger_id
        
        # Executar update
        db.execute(update_query, updates)
        db.commit()
        
        return {"message": "Passageiro atualizado com sucesso", "passenger_id": passenger_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar passageiro: {str(e)}")