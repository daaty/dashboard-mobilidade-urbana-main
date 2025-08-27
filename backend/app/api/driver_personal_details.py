from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, and_
from typing import Optional, List
import json
from datetime import datetime, timedelta
from app.database.db import SessionLocal
from app.models.driver_personal_details import DriverPersonalDetails
from app.schemas.driver_personal_details import (
    DriverPersonalDetailsResponse,
    DriverSummaryResponse,
    DriversListResponse,
    DriverAnalyticsResponse
)

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/find-personal-data/{analytics_driver_id}")
async def find_personal_data_by_analytics_id(
    analytics_driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para encontrar dados pessoais baseado no ID da tabela drivers_data
    Faz cruzamento inteligente entre as duas tabelas
    """
    try:
        # Buscar todos os registros de driver_personal_details
        query = select(DriverPersonalDetails)
        result = await db.execute(query)
        all_personal_data = result.scalars().all()
        
        if not all_personal_data:
            raise HTTPException(status_code=404, detail="Nenhum dado pessoal encontrado")
        
        # Tentar várias estratégias de mapeamento
        found_driver = None
        
        # Estratégia 1: ID direto (caso sejam iguais)
        for driver in all_personal_data:
            if driver.driver_id == analytics_driver_id:
                found_driver = driver
                break
        
        # Estratégia 2: Buscar por nome similar (usando dados do analytics)
        if not found_driver:
            # Primeiro, buscar o nome na tabela analytics
            import psycopg2
            DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name FROM drivers_data 
                WHERE driver_id = %s 
                AND data_type = 'active'
                LIMIT 1
            """, (analytics_driver_id,))
            
            analytics_result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if analytics_result:
                analytics_name = analytics_result[0]
                print(f"🔍 Procurando match para: {analytics_name} (ID: {analytics_driver_id})")
                
                # Buscar na tabela personal_details por nome similar
                for driver in all_personal_data:
                    personal_data = driver.personal_data
                    if isinstance(personal_data, str):
                        try:
                            personal_data = json.loads(personal_data)
                        except:
                            continue
                    
                    if isinstance(personal_data, dict):
                        driver_name = personal_data.get('driver_name', '')
                        if driver_name and analytics_name:
                            # Comparação simples de nomes
                            if driver_name.strip().lower() == analytics_name.strip().lower():
                                found_driver = driver
                                print(f"✅ Match encontrado por nome: {driver_name} -> ID pessoal: {driver.driver_id}")
                                break
        
        if not found_driver:
            raise HTTPException(
                status_code=404, 
                detail=f"Dados pessoais não encontrados para driver_id {analytics_driver_id}"
            )
        
        # Parse dos dados para retorno
        personal_data = found_driver.personal_data
        if isinstance(personal_data, str):
            try:
                personal_data = json.loads(personal_data)
            except:
                personal_data = {}
        
        rides_history = found_driver.rides_history
        if isinstance(rides_history, str):
            try:
                rides_history = json.loads(rides_history)
            except:
                rides_history = []
        
        wallet_transactions = found_driver.wallet_transactions
        if isinstance(wallet_transactions, str):
            try:
                wallet_transactions = json.loads(wallet_transactions)
            except:
                wallet_transactions = []
        
        return {
            "analytics_driver_id": analytics_driver_id,
            "personal_driver_id": found_driver.driver_id,
            "city": found_driver.city,
            "personal_data": personal_data,
            "rides_history": rides_history,
            "wallet_transactions": wallet_transactions,
            "extracted_at": found_driver.extracted_at,
            "mapping_strategy": "direct_id" if found_driver.driver_id == analytics_driver_id else "name_match"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados pessoais: {str(e)}")

@router.get("/summary/basic-list")
async def get_drivers_basic_list(db: AsyncSession = Depends(get_db)):
    """
    Endpoint para obter lista básica de motoristas para o dashboard
    Compatível com o formato esperado pelo frontend
    """
    try:
        # Buscar todos os motoristas
        query = select(DriverPersonalDetails).order_by(desc(DriverPersonalDetails.updated_at))
        result = await db.execute(query)
        drivers_data = result.scalars().all()
        
        drivers_list = []
        
        for driver in drivers_data:
            # Parse do personal_data se for string
            personal_data = driver.personal_data
            if isinstance(personal_data, str):
                try:
                    personal_data = json.loads(personal_data)
                except:
                    personal_data = {}
            
            # Parse do rides_history se for string  
            rides_history = driver.rides_history
            if isinstance(rides_history, str):
                try:
                    rides_history = json.loads(rides_history)
                except:
                    rides_history = []
            
            # Calcular métricas básicas
            total_rides = len(rides_history) if isinstance(rides_history, list) else 0
            
            # Calcular ganhos totais das corridas
            total_earnings = 0
            if isinstance(rides_history, list):
                for ride in rides_history:
                    if isinstance(ride, dict) and 'fare' in ride:
                        try:
                            total_earnings += float(ride['fare'])
                        except:
                            pass
            
            # Obter nome do motorista - garantir que nunca seja null
            driver_name = "Motorista"
            if isinstance(personal_data, dict):
                driver_name = personal_data.get('driver_name', '')
                if not driver_name or driver_name.strip() == '' or driver_name.strip().lower() == 'status':
                    driver_name = f"Motorista {driver.driver_id}"
            
            # Estruturar dados no formato esperado pelo frontend
            driver_item = {
                'driver_id': driver.driver_id,
                'name': driver_name,  # Garantido não ser null
                'phone': personal_data.get('phone_no', '') if isinstance(personal_data, dict) else '',
                'data': {
                    'metrics': {
                        'total_rides': total_rides,
                        'online_hours': 0,  # Não disponível nos dados atuais
                        'rating': 4.0,  # Valor padrão
                        'total_earnings': total_earnings
                    }
                }
            }
            
            drivers_list.append(driver_item)
        
        return {
            'success': True,
            'drivers': drivers_list,
            'total_drivers': len(drivers_list),
            'active_drivers': len([d for d in drivers_list if d['data']['metrics']['total_rides'] > 0]),
            'average_rating': 4.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lista de motoristas: {str(e)}")

@router.get("/personal-details", response_model=DriversListResponse)
async def get_drivers_personal_details(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
    city: Optional[str] = Query(None, description="Filtrar por cidade"),
    driver_id: Optional[str] = Query(None, description="Filtrar por ID do motorista"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para listar motoristas com dados pessoais detalhados
    """
    try:
        # Construir query base
        query = select(DriverPersonalDetails)
        # Aplicar filtros
        if city:
            query = query.where(DriverPersonalDetails.city.ilike(f"%{city}%"))
        if driver_id:
            query = query.where(DriverPersonalDetails.driver_id == driver_id)

        # Contar total de registros
        count_query = select(func.count(DriverPersonalDetails.id))
        if city:
            count_query = count_query.where(DriverPersonalDetails.city.ilike(f"%{city}%"))
        if driver_id:
            count_query = count_query.where(DriverPersonalDetails.driver_id == driver_id)

        total_result = await db.execute(count_query)
        total_count = total_result.scalar()

        # Aplicar paginação
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(desc(DriverPersonalDetails.updated_at))

        # Executar query
        result = await db.execute(query)
        drivers_data = result.scalars().all()

        # Processar dados completos para resposta
        drivers_full = []
        for driver in drivers_data:
            # Parse campos JSON se necessário
            def parse_json_field(field):
                if isinstance(field, str):
                    try:
                        return json.loads(field)
                    except:
                        return None
                return field

            drivers_full.append(DriverPersonalDetailsResponse(
                id=driver.id,
                driver_id=driver.driver_id,
                city=driver.city,
                personal_data=parse_json_field(driver.personal_data),
                rides_history=parse_json_field(driver.rides_history),
                wallet_transactions=parse_json_field(driver.wallet_transactions),
                subscription_history=parse_json_field(driver.subscription_history),
                additional_info=parse_json_field(driver.additional_info),
                extracted_at=driver.extracted_at,
                updated_at=driver.updated_at,
                extraction_source=driver.extraction_source,
                data_hash=driver.data_hash
            ))

        return {
            "drivers": drivers_full,
            "total_count": total_count,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/personal-details/{driver_id}", response_model=DriverPersonalDetailsResponse)
async def get_driver_personal_details(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para obter dados pessoais detalhados de um motorista específico
    """
    try:
        query = select(DriverPersonalDetails).where(DriverPersonalDetails.driver_id == driver_id)
        result = await db.execute(query)
        driver = result.scalar_one_or_none()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Motorista não encontrado")
        
        return DriverPersonalDetailsResponse.from_orm(driver)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/analytics/{driver_id}", response_model=DriverAnalyticsResponse)
async def get_driver_analytics(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para análise detalhada de um motorista específico
    """
    try:
        query = select(DriverPersonalDetails).where(DriverPersonalDetails.driver_id == driver_id)
        result = await db.execute(query)
        driver = result.scalar_one_or_none()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Motorista não encontrado")
        
        # Processar dados para analytics com valores default amigáveis
        def safe_json(val, default):
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except:
                    return default
            return val if val is not None else default

        personal_data = safe_json(driver.personal_data, {})
        rides_history = safe_json(driver.rides_history, [])
        wallet_transactions = safe_json(driver.wallet_transactions, [])
        subscription_history = safe_json(driver.subscription_history, [])

        # Métricas de corridas
        total_rides = len(rides_history) if isinstance(rides_history, list) else 0
        completed_rides = 0
        cancelled_rides = 0
        if isinstance(rides_history, list):
            completed_rides = len([r for r in rides_history if isinstance(r, dict) and r.get('status') == 'completed'])
            cancelled_rides = len([r for r in rides_history if isinstance(r, dict) and r.get('status') == 'cancelled'])
        completion_rate = (completed_rides / total_rides * 100) if total_rides > 0 else 0.0

        # Métricas financeiras
        total_earnings = 0.0
        if isinstance(rides_history, list):
            for ride in rides_history:
                if isinstance(ride, dict):
                    try:
                        total_earnings += float(ride.get('fare', 0) or 0)
                    except:
                        pass
        average_ride_value = total_earnings / completed_rides if completed_rides > 0 else 0.0

        # Saldo da carteira (última transação)
        wallet_balance = 0.0
        if isinstance(wallet_transactions, list) and wallet_transactions:
            try:
                valid_transactions = [t for t in wallet_transactions if isinstance(t, dict)]
                if valid_transactions:
                    last_transaction = max(valid_transactions, key=lambda x: x.get('date', ''))
                    wallet_balance = float(last_transaction.get('balance_after', 0.0) or 0.0)
            except:
                wallet_balance = 0.0

        # Métricas de performance
        ratings = []
        if isinstance(rides_history, list):
            ratings = [
                ride.get('rating') for ride in rides_history 
                if isinstance(ride, dict) and ride.get('rating') is not None
            ]
        average_rating = round(sum(ratings) / len(ratings), 1) if ratings else 3.5

        total_distance = 0.0
        total_duration = 0
        if isinstance(rides_history, list):
            for ride in rides_history:
                if isinstance(ride, dict):
                    try:
                        total_distance += float(ride.get('distance', 0) or 0)
                    except:
                        pass
                    try:
                        total_duration += int(ride.get('duration', 0) or 0)
                    except:
                        pass

        # Dados temporais
        first_ride_date = None
        last_ride_date = None
        if isinstance(rides_history, list) and rides_history:
            try:
                ride_dates = [
                    ride.get('date') for ride in rides_history 
                    if isinstance(ride, dict) and ride.get('date')
                ]
                if ride_dates:
                    first_ride_date = datetime.fromisoformat(min(ride_dates).replace('Z', '+00:00'))
                    last_ride_date = datetime.fromisoformat(max(ride_dates).replace('Z', '+00:00'))
            except:
                first_ride_date = None
                last_ride_date = None

        # Calcular dias ativos
        active_days = 0
        if first_ride_date and last_ride_date:
            active_days = (last_ride_date - first_ride_date).days + 1

        # Assinatura atual
        current_subscription = None
        if isinstance(subscription_history, list) and subscription_history:
            try:
                active_subs = [
                    s for s in subscription_history 
                    if isinstance(s, dict) and s.get('status') == 'active'
                ]
                if active_subs:
                    current_subscription = active_subs[0]
            except:
                current_subscription = None

        # Garantir campos do modal sempre preenchidos
        def get_modal_field(val, default):
            if val is None or (isinstance(val, str) and val.strip() == ""):
                return default
            return val

        # Preencher campos principais do modal com fallback para nomes alternativos
        def get_first_nonempty(*args, default="N/A"):
            for val in args:
                if val is not None and str(val).strip() != "":
                    return val
            return default

        modal_personal_data = {
            "name": get_modal_field(personal_data.get("driver_name", None), f"Motorista {driver.driver_id}"),
            "phone": get_first_nonempty(personal_data.get("phone_no"), personal_data.get("phone"), default="N/A"),
            "email": get_first_nonempty(personal_data.get("email"), default="N/A"),
            "city": get_first_nonempty(personal_data.get("city"), driver.city, default="N/A"),
            "vehicle": get_first_nonempty(personal_data.get("vehicle"), personal_data.get("vehicle_no"), personal_data.get("vehicle_type"), default="N/A"),
            "status": get_first_nonempty(personal_data.get("status"), default="N/A"),
            "join_date": get_first_nonempty(personal_data.get("join_date"), personal_data.get("joining_date"), default="N/A")
        }

        return DriverAnalyticsResponse(
            driver_id=driver.driver_id,
            city=modal_personal_data["city"],
            personal_data=modal_personal_data,
            total_rides=total_rides,
            completed_rides=completed_rides,
            cancelled_rides=cancelled_rides,
            completion_rate=completion_rate,
            total_earnings=total_earnings,
            average_ride_value=average_ride_value,
            wallet_balance=wallet_balance,
            average_rating=average_rating,
            total_distance=total_distance,
            total_duration=total_duration,
            first_ride_date=first_ride_date,
            last_ride_date=last_ride_date,
            active_days=active_days,
            current_subscription=current_subscription
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/cities", response_model=List[str])
async def get_available_cities(
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para listar todas as cidades disponíveis
    """
    try:
        query = select(DriverPersonalDetails.city).distinct()
        result = await db.execute(query)
        cities = [row[0] for row in result.fetchall()]
        return sorted(cities)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/summary")
async def get_drivers_summary(
    city: Optional[str] = Query(None, description="Filtrar por cidade"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para obter resumo geral dos motoristas
    """
    try:
        # Query base
        query = select(DriverPersonalDetails)
        if city:
            query = query.where(DriverPersonalDetails.city.ilike(f"%{city}%"))
        
        result = await db.execute(query)
        drivers_data = result.scalars().all()
        
        if not drivers_data:
            return {
                "total_drivers": 0,
                "cities_count": 0,
                "total_rides": 0,
                "total_earnings": 0.0,
                "average_rating": 0.0,
                "active_drivers": 0
            }
        
        # Calcular métricas
        total_drivers = len(drivers_data)
        cities = set(driver.city for driver in drivers_data)
        cities_count = len(cities)
        
        total_rides = 0
        total_earnings = 0.0
        all_ratings = []
        active_drivers = 0
        
        for driver in drivers_data:
            rides_history = driver.rides_history or []
            if isinstance(rides_history, str):
                try:
                    rides_history = json.loads(rides_history)
                except:
                    rides_history = []
            
            if isinstance(rides_history, list):
                total_rides += len(rides_history)
                
                # Contar motoristas ativos (com pelo menos 1 corrida)
                if len(rides_history) > 0:
                    active_drivers += 1
                
                # Somar ganhos
                for ride in rides_history:
                    if isinstance(ride, dict):
                        if isinstance(ride.get('fare'), (int, float)):
                            total_earnings += ride['fare']
                        
                        # Coletar ratings
                        if ride.get('rating'):
                            all_ratings.append(ride['rating'])
        
        average_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0.0
        
        return {
            "total_drivers": total_drivers,
            "cities_count": cities_count,
            "total_rides": total_rides,
            "total_earnings": total_earnings,
            "average_rating": average_rating,
            "active_drivers": active_drivers,
            "cities": sorted(cities) if city is None else [city]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
