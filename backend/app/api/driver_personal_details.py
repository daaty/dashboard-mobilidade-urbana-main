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
        
        # BUSCAR DADOS ADICIONAIS DA TABELA drivers_data (email, etc.)
        additional_driver_data = {}
        try:
            import psycopg2
            DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT email, mobile, additional_data 
                FROM drivers_data 
                WHERE driver_id = %s 
                AND data_type = 'active'
                ORDER BY scraped_at DESC 
                LIMIT 1
            """, (analytics_driver_id,))
            
            driver_data_result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if driver_data_result:
                email, mobile, additional_data_str = driver_data_result
                additional_driver_data['email'] = email
                additional_driver_data['mobile'] = mobile
                
                # Parse additional_data JSON
                if additional_data_str:
                    try:
                        additional_data = json.loads(additional_data_str)
                        additional_driver_data['additional_data'] = additional_data
                    except:
                        pass
                        
                print(f"✅ Dados adicionais encontrados: email={email}, mobile={mobile}")
                
                # Enriquecer personal_data com dados da tabela drivers_data
                if email and email not in ['', 'N/A', None]:
                    personal_data['email'] = email
                if mobile and mobile not in ['', 'N/A', None]:
                    personal_data['mobile'] = mobile
                    
        except Exception as e:
            print(f"⚠️ Erro ao buscar dados adicionais: {e}")
        
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
            "additional_driver_data": additional_driver_data,
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
            
            # Calcular ganhos totais das corridas - APENAS CORRIDAS CONCLUÍDAS
            total_earnings = 0
            completed_rides = 0  # Contador de corridas realmente concluídas
            
            if isinstance(rides_history, list):
                for ride in rides_history:
                    if isinstance(ride, dict) and 'fare' in ride:
                        # Verificar se a corrida foi realmente concluída
                        is_completed = True
                        
                        # Filtros para identificar corridas realmente concluídas:
                        # 1. Deve ter drop_time (horário de término)
                        if 'drop_time' not in ride or not ride['drop_time'] or ride['drop_time'].strip() == '':
                            is_completed = False
                        
                        # 2. Deve ter distância percorrida > 0 (corridas canceladas podem ter distância 0)
                        if 'distance_travelled' in ride:
                            try:
                                distance = float(ride['distance_travelled'])
                                # Se a distância é menor que 0.1 km (100 metros), pode ser corrida cancelada/teste
                                # Motoristas de teste frequentemente têm distâncias de 0.001
                                # Corridas reais normalmente têm pelo menos algumas centenas de metros
                                if distance < 0.1:
                                    is_completed = False
                            except:
                                pass
                        
                        # 3. Se tem avaliação válida do motorista, provavelmente foi concluída
                        if 'driver_rating' in ride and ride['driver_rating'] == '--':
                            # Corridas sem avaliação podem ser suspeitas, mas não vamos descartar automaticamente
                            pass
                        
                        # 4. Verificar se start_end_case indica problema
                        if 'start_end_case' in ride and ride['start_end_case'] != 'NO':
                            is_completed = False
                        
                        # Se passou em todos os filtros, considerar como corrida concluída
                        if is_completed:
                            try:
                                fare_value = float(ride['fare'])
                                # Só somar se a tarifa é > 0
                                if fare_value > 0:
                                    total_earnings += fare_value
                                    completed_rides += 1
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
                        'total_rides': completed_rides,  # Usar apenas corridas concluídas
                        'total_rides_raw': total_rides,  # Total bruto para debug
                        'online_hours': 0,  # Não disponível nos dados atuais
                        'rating': 4.0,  # Valor padrão
                        'total_earnings': total_earnings,  # Ganhos apenas de corridas concluídas
                        'filtered_rides_info': {
                            'total_in_history': total_rides,
                            'completed_rides': completed_rides,
                            'filtered_out': total_rides - completed_rides
                        }
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

@router.get("/test-debug/{driver_id}")
async def test_debug_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de teste para debug de dados específicos
    """
    try:
        query = select(DriverPersonalDetails).where(DriverPersonalDetails.driver_id == driver_id)
        result = await db.execute(query)
        driver = result.scalar_one_or_none()
        
        if not driver:
            return {"error": "Driver não encontrado", "driver_id": driver_id}
        
        # Debug completo
        return {
            "driver_id": driver.driver_id,
            "city": driver.city,
            "personal_data_type": str(type(driver.personal_data)),
            "personal_data_raw": str(driver.personal_data)[:500] if driver.personal_data else "NULL",
            "rides_history_type": str(type(driver.rides_history)),
            "rides_history_length": len(driver.rides_history) if driver.rides_history else "NULL",
            "wallet_transactions_type": str(type(driver.wallet_transactions)),
            "wallet_transactions_length": len(driver.wallet_transactions) if driver.wallet_transactions else "NULL",
            "extracted_at": driver.extracted_at,
            "updated_at": driver.updated_at
        }
        
    except Exception as e:
        return {"error": str(e), "driver_id": driver_id}

@router.get("/personal-details")
async def get_drivers_personal_details(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
    city: Optional[str] = Query(None, description="Filtrar por cidade"),
    driver_id: Optional[str] = Query(None, description="Filtrar por ID do motorista"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para listar motoristas com dados pessoais detalhados - ATUALIZADO
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

        # Processar dados completos para resposta (incluindo dados JSON parseados)
        drivers_full = []
        for driver in drivers_data:
            # Debug: log dos dados brutos
            if driver.driver_id == "17147322":
                print(f"🔍 DEBUG - Driver {driver.driver_id}:")
                print(f"   personal_data type: {type(driver.personal_data)}")
                print(f"   personal_data value: {driver.personal_data}")
                print(f"   rides_history type: {type(driver.rides_history)}")
                print(f"   rides_history length: {len(driver.rides_history) if driver.rides_history else 'NULL'}")
            
            # Parse campos JSON se necessário
            def parse_json_field(field):
                if isinstance(field, str):
                    try:
                        return json.loads(field)
                    except json.JSONDecodeError:
                        return {}
                return field if field is not None else {}

            # Parse de todos os campos JSON
            personal_data = parse_json_field(driver.personal_data)
            rides_history = parse_json_field(driver.rides_history)
            wallet_transactions = parse_json_field(driver.wallet_transactions)
            subscription_history = parse_json_field(driver.subscription_history)
            additional_info = parse_json_field(driver.additional_info)

            # Debug adicional para o driver específico
            if driver.driver_id == "17147322":
                print(f"   parsed personal_data: {personal_data}")
                print(f"   parsed rides_history length: {len(rides_history) if isinstance(rides_history, list) else 'NOT LIST'}")

            # Garantir que rides_history seja uma lista
            if not isinstance(rides_history, list):
                rides_history = []
                
            # Garantir que wallet_transactions seja uma lista
            if not isinstance(wallet_transactions, list):
                wallet_transactions = []

            # Calcular métricas básicas para compatibilidade
            total_rides = len(rides_history)
            total_earnings = 0.0
            
            # Calcular ganhos totais das corridas
            for ride in rides_history:
                if isinstance(ride, dict) and 'fare' in ride:
                    try:
                        total_earnings += float(ride['fare'])
                    except (ValueError, TypeError):
                        pass

            # Extrair nome do motorista
            driver_name = "Motorista"
            if isinstance(personal_data, dict):
                driver_name = personal_data.get('driver_name', f"Motorista {driver.driver_id}")
                if not driver_name or driver_name.strip() == '':
                    driver_name = f"Motorista {driver.driver_id}"

            # Extrair telefone
            phone = ""
            if isinstance(personal_data, dict):
                phone = personal_data.get('phone_no', '') or personal_data.get('phone', '')

            # Debug final para o driver específico
            if driver.driver_id == "17147322":
                print(f"   final driver_name: {driver_name}")
                print(f"   final phone: {phone}")
                print(f"   final total_rides: {total_rides}")
                print(f"   final total_earnings: {total_earnings}")

            drivers_full.append({
                "id": driver.id,
                "driver_id": driver.driver_id,
                "name": driver_name,
                "phone": phone,
                "city": driver.city,
                "total_rides": total_rides,
                "total_earnings": total_earnings,
                "average_rating": 3.5,  # Valor padrão
                "status": personal_data.get('status', 'unknown') if isinstance(personal_data, dict) else 'unknown',
                "last_activity": personal_data.get('last_ride_on', None) if isinstance(personal_data, dict) else None,
                "personal_data": personal_data,
                "rides_history": rides_history,
                "wallet_transactions": wallet_transactions,
                "subscription_history": subscription_history,
                "additional_info": additional_info,
                "extracted_at": driver.extracted_at,
                "updated_at": driver.updated_at,
                "extraction_source": driver.extraction_source,
                "data_hash": driver.data_hash
            })

        return {
            "success": True,
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
        
        # Aplicar a mesma lógica de filtro usada na listagem
        if isinstance(rides_history, list):
            for ride in rides_history:
                if isinstance(ride, dict) and 'fare' in ride:
                    # Verificar se a corrida foi realmente concluída
                    is_completed = True
                    
                    # 1. Deve ter drop_time (horário de término)
                    if 'drop_time' not in ride or not ride['drop_time'] or ride['drop_time'].strip() == '':
                        is_completed = False
                    
                    # 2. Deve ter distância percorrida > 0.1 km (100 metros)
                    if 'distance_travelled' in ride:
                        try:
                            distance = float(ride['distance_travelled'])
                            if distance < 0.1:  # Filtrar corridas de teste
                                is_completed = False
                        except:
                            is_completed = False
                    
                    # 3. Verificar se start_end_case indica problema
                    if 'start_end_case' in ride and ride['start_end_case'] != 'NO':
                        is_completed = False
                    
                    if is_completed:
                        completed_rides += 1
                    else:
                        cancelled_rides += 1  # Considerar como cancelada se não passou nos filtros
        
        completion_rate = (completed_rides / total_rides * 100) if total_rides > 0 else 0.0

        # Métricas financeiras - calcular earnings apenas de corridas concluídas
        total_earnings = 0.0
        if isinstance(rides_history, list):
            for ride in rides_history:
                if isinstance(ride, dict) and 'fare' in ride:
                    # Aplicar os mesmos filtros para considerar apenas corridas concluídas
                    is_completed = True
                    
                    if 'drop_time' not in ride or not ride['drop_time'] or ride['drop_time'].strip() == '':
                        is_completed = False
                    
                    if 'distance_travelled' in ride:
                        try:
                            distance = float(ride['distance_travelled'])
                            if distance < 0.1:
                                is_completed = False
                        except:
                            is_completed = False
                    
                    if 'start_end_case' in ride and ride['start_end_case'] != 'NO':
                        is_completed = False
                    
                    # Só somar earnings de corridas realmente concluídas
                    if is_completed:
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


@router.get("/credits-analysis")
async def get_credits_analysis(
    city: Optional[str] = Query(None, description="Filtrar por cidade"),
    period_days: Optional[int] = Query(30, description="Período em dias para análise de transações"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para análise completa de créditos dos motoristas
    Analisa credit_wallet_balance e wallet_transactions
    """
    try:
        print(f"🔍 Iniciando análise de créditos - cidade: {city}, período: {period_days} dias")
        
        # Buscar todos os dados pessoais dos motoristas
        query = select(DriverPersonalDetails)
        result = await db.execute(query)
        drivers_data = result.scalars().all()
        
        print(f"📊 Encontrados {len(drivers_data)} registros de motoristas")
        
        # Variáveis para estatísticas gerais
        total_drivers = 0
        total_credits_balance = 0
        total_credits_charged = 0  # Total de créditos carregados (tipo "C")
        total_credits_spent = 0    # Total de créditos gastos (tipo "D")
        drivers_with_credits = 0
        drivers_by_city = {}
        transactions_by_type = {}
        transactions_by_period = {}
        
        # Data de corte para análise de período
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        for driver in drivers_data:
            try:
                # Parse dos dados pessoais
                personal_data = None
                if driver.personal_data:
                    if isinstance(driver.personal_data, str):
                        personal_data = json.loads(driver.personal_data)
                    else:
                        personal_data = driver.personal_data
                
                if not personal_data or not isinstance(personal_data, dict):
                    continue
                
                # Extrair cidade do driver
                driver_city = personal_data.get('city', 'Unknown')
                
                # Aplicar filtro de cidade se especificado (ignorar quando city for "all" ou None)
                if city and city.lower() != 'all' and driver_city.lower() != city.lower():
                    continue
                
                total_drivers += 1
                
                # Inicializar dados da cidade se não existir
                if driver_city not in drivers_by_city:
                    drivers_by_city[driver_city] = {
                        'drivers_count': 0,
                        'total_balance': 0,
                        'total_charged': 0,
                        'total_spent': 0,
                        'avg_balance': 0
                    }
                
                drivers_by_city[driver_city]['drivers_count'] += 1
                
                # Extrair saldo atual de créditos
                credit_balance = 0
                if 'credit_wallet_balance' in personal_data:
                    try:
                        credit_balance = float(personal_data['credit_wallet_balance'])
                    except (ValueError, TypeError):
                        credit_balance = 0
                
                if credit_balance > 0:
                    drivers_with_credits += 1
                
                total_credits_balance += credit_balance
                drivers_by_city[driver_city]['total_balance'] += credit_balance
                
                # Analisar transações de wallet
                wallet_transactions = []
                if driver.wallet_transactions:
                    if isinstance(driver.wallet_transactions, str):
                        wallet_transactions = json.loads(driver.wallet_transactions)
                    else:
                        wallet_transactions = driver.wallet_transactions
                
                if isinstance(wallet_transactions, list):
                    for transaction in wallet_transactions:
                        if not isinstance(transaction, dict):
                            continue
                        
                        transaction_type = transaction.get('type', 'Unknown')
                        amount = 0
                        transaction_time_str = transaction.get('transaction_time', '')
                        
                        try:
                            amount = float(transaction.get('amount', 0))
                        except (ValueError, TypeError):
                            amount = 0
                        
                        # Verificar se a transação está no período especificado
                        transaction_date = None
                        if transaction_time_str:
                            try:
                                # Formato esperado: "2025-07-29 18:00:13"
                                transaction_date = datetime.strptime(transaction_time_str, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                # Tentar outros formatos se necessário
                                pass
                        
                        # Contar todas as transações para estatísticas gerais
                        if transaction_type not in transactions_by_type:
                            transactions_by_type[transaction_type] = {'count': 0, 'total_amount': 0}
                        
                        transactions_by_type[transaction_type]['count'] += 1
                        transactions_by_type[transaction_type]['total_amount'] += amount
                        
                        # Separar por tipo para totais gerais
                        if transaction_type == 'C':  # Crédito (carregamento)
                            total_credits_charged += amount
                            drivers_by_city[driver_city]['total_charged'] += amount
                        elif transaction_type == 'D':  # Débito (gasto)
                            total_credits_spent += amount
                            drivers_by_city[driver_city]['total_spent'] += amount
                        
                        # Análise por período (apenas transações no período especificado)
                        if transaction_date and transaction_date >= cutoff_date:
                            month_key = transaction_date.strftime('%Y-%m')
                            if month_key not in transactions_by_period:
                                transactions_by_period[month_key] = {'C': 0, 'D': 0}
                            transactions_by_period[month_key][transaction_type] = transactions_by_period[month_key].get(transaction_type, 0) + amount
                
            except Exception as e:
                print(f"⚠️ Erro ao processar driver {driver.driver_id}: {e}")
                continue
        
        # Calcular médias por cidade
        for city_name, city_data in drivers_by_city.items():
            if city_data['drivers_count'] > 0:
                city_data['avg_balance'] = round(city_data['total_balance'] / city_data['drivers_count'], 2)
        
        # Calcular estatísticas finais
        avg_credits_per_driver = round(total_credits_balance / total_drivers, 2) if total_drivers > 0 else 0
        credits_utilization_rate = round((drivers_with_credits / total_drivers * 100), 2) if total_drivers > 0 else 0
        net_credits_flow = total_credits_charged - total_credits_spent
        
        print(f"✅ Análise concluída - {total_drivers} motoristas processados")
        
        return {
            "status": "success",
            "data": {
                "summary": {
                    "total_drivers": total_drivers,
                    "total_credits_in_circulation": round(total_credits_balance, 2),
                    "total_credits_charged": round(total_credits_charged, 2),
                    "total_credits_spent": round(total_credits_spent, 2),
                    "net_credits_flow": round(net_credits_flow, 2),
                    "drivers_with_credits": drivers_with_credits,
                    "avg_credits_per_driver": avg_credits_per_driver,
                    "credits_utilization_rate": credits_utilization_rate
                },
                "by_city": drivers_by_city,
                "transactions_analysis": {
                    "by_type": transactions_by_type,
                    "by_period": transactions_by_period,
                    "period_days": period_days
                },
                "filter": {
                    "city": city if city else "Todas as cidades",
                    "period_days": period_days
                }
            }
        }
        
    except Exception as e:
        print(f"❌ Erro na análise de créditos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar créditos: {str(e)}")
