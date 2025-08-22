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
        
        # Processar dados para resposta resumida
        drivers_summary = []
        for driver in drivers_data:
            # Extrair dados básicos do JSON - tratar como string se necessário
            personal_data = driver.personal_data or {}
            if isinstance(personal_data, str):
                try:
                    personal_data = json.loads(personal_data)
                except:
                    personal_data = {}
            
            name = personal_data.get('name', 'N/A')
            phone = personal_data.get('phone', 'N/A')
            
            # Calcular métricas básicas das corridas
            rides_history = driver.rides_history or []
            if isinstance(rides_history, str):
                try:
                    rides_history = json.loads(rides_history)
                except:
                    rides_history = []
            
            total_rides = len(rides_history) if isinstance(rides_history, list) else 0
            total_earnings = 0.0
            if isinstance(rides_history, list):
                total_earnings = sum(
                    ride.get('fare', 0) for ride in rides_history 
                    if isinstance(ride, dict) and isinstance(ride.get('fare'), (int, float))
                )
            
            # Calcular rating médio
            ratings = []
            if isinstance(rides_history, list):
                ratings = [
                    ride.get('rating') for ride in rides_history 
                    if isinstance(ride, dict) and ride.get('rating')
                ]
            average_rating = sum(ratings) / len(ratings) if ratings else None
            
            # Última atividade
            last_activity = None
            if isinstance(rides_history, list) and rides_history:
                try:
                    dates = [
                        ride.get('date', '') for ride in rides_history 
                        if isinstance(ride, dict) and ride.get('date')
                    ]
                    if dates:
                        last_ride_date = max(dates)
                        if last_ride_date:
                            last_activity = datetime.fromisoformat(last_ride_date.replace('Z', '+00:00'))
                except:
                    pass
            
            drivers_summary.append(DriverSummaryResponse(
                driver_id=driver.driver_id,
                name=name,
                phone=phone,
                city=driver.city,
                total_rides=total_rides,
                total_earnings=total_earnings,
                average_rating=average_rating,
                status='active' if total_rides > 0 else 'inactive',
                last_activity=last_activity
            ))
        
        return DriversListResponse(
            drivers=drivers_summary,
            total_count=total_count,
            page=page,
            limit=limit
        )
        
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
        
        # Processar dados para analytics
        personal_data = driver.personal_data or {}
        if isinstance(personal_data, str):
            try:
                personal_data = json.loads(personal_data)
            except:
                personal_data = {}
        
        rides_history = driver.rides_history or []
        if isinstance(rides_history, str):
            try:
                rides_history = json.loads(rides_history)
            except:
                rides_history = []
        
        wallet_transactions = driver.wallet_transactions or []
        if isinstance(wallet_transactions, str):
            try:
                wallet_transactions = json.loads(wallet_transactions)
            except:
                wallet_transactions = []
        
        subscription_history = driver.subscription_history or []
        if isinstance(subscription_history, str):
            try:
                subscription_history = json.loads(subscription_history)
            except:
                subscription_history = []
        
        # Métricas de corridas
        total_rides = len(rides_history) if isinstance(rides_history, list) else 0
        completed_rides = 0
        cancelled_rides = 0
        
        if isinstance(rides_history, list):
            completed_rides = len([r for r in rides_history if isinstance(r, dict) and r.get('status') == 'completed'])
            cancelled_rides = len([r for r in rides_history if isinstance(r, dict) and r.get('status') == 'cancelled'])
        
        completion_rate = (completed_rides / total_rides * 100) if total_rides > 0 else 0
        
        # Métricas financeiras
        total_earnings = 0.0
        if isinstance(rides_history, list):
            total_earnings = sum(
                ride.get('fare', 0) for ride in rides_history 
                if isinstance(ride, dict) and isinstance(ride.get('fare'), (int, float))
            )
        average_ride_value = total_earnings / completed_rides if completed_rides > 0 else 0
        
        # Saldo da carteira (última transação)
        wallet_balance = None
        if isinstance(wallet_transactions, list) and wallet_transactions:
            try:
                valid_transactions = [t for t in wallet_transactions if isinstance(t, dict)]
                if valid_transactions:
                    last_transaction = max(valid_transactions, key=lambda x: x.get('date', ''))
                    wallet_balance = last_transaction.get('balance_after')
            except:
                pass
        
        # Métricas de performance
        ratings = []
        if isinstance(rides_history, list):
            ratings = [
                ride.get('rating') for ride in rides_history 
                if isinstance(ride, dict) and ride.get('rating')
            ]
        average_rating = sum(ratings) / len(ratings) if ratings else None
        
        total_distance = 0.0
        total_duration = 0
        if isinstance(rides_history, list):
            total_distance = sum(
                ride.get('distance', 0) for ride in rides_history 
                if isinstance(ride, dict) and isinstance(ride.get('distance'), (int, float))
            )
            total_duration = sum(
                ride.get('duration', 0) for ride in rides_history 
                if isinstance(ride, dict) and isinstance(ride.get('duration'), (int, float))
            )
        
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
                pass
        
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
                pass
        
        return DriverAnalyticsResponse(
            driver_id=driver.driver_id,
            city=driver.city,
            personal_data=personal_data,
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
