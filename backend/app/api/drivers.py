from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import json
from datetime import datetime, timedelta
from app.database.db import SessionLocal
from app.models.drivers_data import DriversData

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/overview")
async def get_drivers_overview(
    periodo: Optional[int] = Query(30, description="Número de dias para análise"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para métricas gerais dos motoristas
    """
    try:
        # Data limite baseada no período
        data_limite = datetime.now() - timedelta(days=periodo)
        data_limite_str = data_limite.strftime('%Y-%m-%d %H:%M:%S')
        
        # Buscar todos os registros da tabela drivers_data
        result = await db.execute(select(DriversData))
        drivers_data = result.scalars().all()
        
        if not drivers_data:
            return {
                "total_drivers": 0,
                "active_drivers": 0,
                "average_rating": 0.0,
                "top_drivers": [],
                "drivers_by_status": {},
                "periodo_dias": periodo
            }
        
        # Processar dados dos motoristas com deduplicação inteligente
        unique_drivers = {}  # Usar telefone como chave para deduplicação
        drivers_processed = set()
        all_drivers = []
        
        for driver_record in drivers_data:
            # Filtro por data
            if hasattr(driver_record, 'scraped_at') and driver_record.scraped_at:
                if driver_record.scraped_at < data_limite:
                    continue
            
            try:
                # Extrair informações do motorista baseado na estrutura real
                driver_id = driver_record.driver_id
                driver_name = driver_record.name
                
                # Pular registros inválidos
                if not driver_id or driver_id in ['---', '0', 'Driver']:
                    continue
                
                # O campo additional_data pode ser dict ou string JSON
                driver_data = driver_record.additional_data
                if isinstance(driver_data, str):
                    driver_data = json.loads(driver_data)
                elif not isinstance(driver_data, dict):
                    driver_data = {}
                
                # Verificar estrutura: se tem 'profile' (nova estrutura) ou 'raw_row' (estrutura antiga)
                has_new_structure = 'profile' in driver_data
                has_old_structure = 'raw_row' in driver_data
                
                # Para nova estrutura (dados importados)
                if has_new_structure:
                    profile = driver_data.get('profile', {})
                    performance = driver_data.get('performance', {})
                    raw_data = driver_data.get('raw_data', {})
                    
                    # Extrair dados do perfil
                    real_name = driver_name or f"Motorista {driver_id}"
                    phone = driver_record.mobile or ''
                    status = profile.get('status', 'active' if raw_data.get('Active Days', 0) > 0 else 'inactive')
                    
                    # Calcular rating baseado na performance
                    success_rides = float(raw_data.get('Success Rides', 0))
                    total_requests = max(float(raw_data.get('Request Sent', 0)), float(raw_data.get('Requests Received', 0)))
                    driver_cancelled = float(raw_data.get('Driver Cancelled Rides', 0))
                    user_cancelled = float(raw_data.get('User Cancelled Rides', 0))
                    missed_rides = float(raw_data.get('Missed Rides', 0))
                    
                    # Simular rating baseado na performance (igual ao frontend)
                    if total_requests > 0 or success_rides > 0:
                        cancellation_rate = ((driver_cancelled + user_cancelled) / total_requests) if total_requests > 0 else 0
                        miss_rate = (missed_rides / total_requests) if total_requests > 0 else 0
                        rating = max(1.0, min(5.0, 5.0 - (cancellation_rate * 3) - (miss_rate * 2)))
                    else:
                        rating = 0.0
                    
                    city = raw_data.get('CITY', profile.get('city', ''))
                    vehicle_type = raw_data.get('Vehicle', profile.get('vehicle_type', ''))
                    
                    # Métricas de performance do raw_data (dados reais do Excel) - já calculadas acima
                    active_days = float(raw_data.get('Active Days', 0))
                    
                    # Calcular métricas derivadas
                    success_rate = (success_rides / total_requests * 100) if total_requests > 0 else 0.0
                    total_rides = success_rides  # Corridas completadas
                    
                    # Usar dados de performance se disponível, senão usar raw_data
                    if performance:
                        total_rides = performance.get('total_rides', total_rides)
                        success_rides = performance.get('success_rides', success_rides)
                        success_rate = performance.get('success_rate', success_rate)
                    
                    # Chave para deduplicação
                    if phone and phone.startswith('+55'):
                        dedup_key = phone
                    else:
                        dedup_key = f"id_{driver_id}"
                    
                    # Adicionar à lista processada
                    unique_drivers[dedup_key] = {
                        'driver_record': driver_record,
                        'driver_data': driver_data,
                        'phone': phone,
                        'name': real_name,
                        'driver_id': driver_id,
                        'status': status,
                        'rating': rating,
                        'city': city,
                        'vehicle_type': vehicle_type,
                        'total_rides': total_rides,
                        'success_rides': success_rides,
                        'success_rate': success_rate,
                        'active_days': active_days,
                        'total_requests': total_requests,
                        'driver_cancelled': driver_cancelled,
                        'user_cancelled': user_cancelled,
                        'missed_rides': missed_rides
                    }
                    continue
                
                # Lógica antiga para estrutura com raw_row
                elif has_old_structure:
                    # Verificar se tem status online
                    has_online_status = False
                    raw_row = driver_data.get('raw_row', [])
                    if isinstance(raw_row, list):
                        for item in raw_row:
                            if isinstance(item, str) and item.lower() == 'online':
                                has_online_status = True
                                break
                    
                    # Se não tem status online, pular
                    if not has_online_status:
                        continue
                    
                    # Extrair telefone válido para deduplicação
                    phone = driver_record.email if hasattr(driver_record, 'email') else ''
                    real_phone = None
                    
                    # Procurar telefone válido no raw_row
                    if isinstance(raw_row, list):
                        for item in raw_row:
                            if isinstance(item, str) and item.startswith('+556') and len(item) >= 13:
                                real_phone = item
                                break
                    
                    # Usar o telefone válido encontrado
                    if real_phone:
                        phone = real_phone
                    
                    # Extrair nome real do motorista
                    real_name = driver_name
                    if isinstance(raw_row, list):
                        # Procurar nome real no raw_row (geralmente após o telefone)
                        for i, item in enumerate(raw_row):
                            if isinstance(item, str) and len(item) > 3 and not item.startswith('+') and not item.isdigit() and item not in ['Online', 'Offline']:
                                # Verificar se parece com nome (tem espaços ou maiúsculas)
                                if ' ' in item or (item[0].isupper() and any(c.islower() for c in item)):
                                    real_name = item
                                    break
                    
                    # Se nome ainda é inválido, usar o ID se for nome
                    if not real_name or real_name in ['0', '1', 'None', 'null']:
                        if isinstance(driver_id, str) and len(driver_id) > 3 and not driver_id.startswith('+'):
                            real_name = driver_id
                    
                    # Chave para deduplicação: priorizar telefone, depois nome
                    dedup_key = None
                    if phone and phone.startswith('+556'):
                        dedup_key = phone
                    elif real_name and real_name not in ['0', '1', 'None', 'null']:
                        dedup_key = real_name.lower()
                    else:
                        dedup_key = driver_id
                    
                    # Se já processamos este motorista, priorizar registro mais recente com nome completo
                    if dedup_key in unique_drivers:
                        existing = unique_drivers[dedup_key]
                        # Priorizar registro com nome real vs ID como nome
                        if (real_name and real_name not in ['0', '1', 'None', 'null'] and 
                            existing['name'] in ['0', '1', 'None', 'null']):
                            # Substituir por registro com nome melhor
                            pass
                        else:
                            # Manter o existente
                            continue
                    
                    unique_drivers[dedup_key] = {
                        'driver_record': driver_record,
                        'driver_data': driver_data,
                        'phone': phone,
                        'name': real_name,
                        'driver_id': driver_id,
                        'status': 'active',  # Default para estrutura antiga
                        'rating': 0.0,
                        'city': '',
                        'vehicle_type': '',
                        'total_rides': 0,
                        'success_rides': 0,
                        'success_rate': 0.0
                    }
                else:
                    # Estrutura não reconhecida, pular
                    continue
                
            except Exception as e:
                print(f"Erro ao processar dados do motorista {driver_record.driver_id}: {e}")
                continue
        
        # Processar apenas os motoristas únicos
        for dedup_key, driver_info in unique_drivers.items():
            try:
                driver_record = driver_info['driver_record']
                driver_data = driver_info['driver_data']
                phone = driver_info['phone']
                real_name = driver_info['name']
                driver_id = driver_info['driver_id']
                
                # Usar dados processados da nova estrutura ou valores padrão para estrutura antiga
                status = driver_info.get('status', 'active')
                rating = driver_info.get('rating', 0.0)  # Usar rating calculado ou 0 como padrão
                total_rides = driver_info.get('total_rides', 0)
                success_rides = driver_info.get('success_rides', 0)
                success_rate = driver_info.get('success_rate', 0.0)
                city = driver_info.get('city', '')
                vehicle_type = driver_info.get('vehicle_type', '')
                
                # Calcular efficiency_score baseado nas métricas
                if total_rides > 0:
                    efficiency_score = min(100, (success_rate + (rating * 20)))
                else:
                    efficiency_score = rating * 20
                
                # Determinar status final
                driver_status = 'ativo' if status == 'active' or total_rides > 0 else 'inativo'
                
                # Informações adicionais
                last_ride = ''
                last_login = ''
                if driver_data and 'import_timestamp' in driver_data:
                    last_login = driver_data['import_timestamp']
                
                # Usar o nome real extraído
                clean_name = real_name if real_name and real_name not in ['None', '0', 'null', '1'] else f"Motorista {driver_id}"
                
                driver_info_final = {
                    'id': driver_id,
                    'name': clean_name,
                    'status': driver_status,
                    'rating': rating,
                    'total_rides': total_rides,
                    'success_rides': success_rides,
                    'success_rate': success_rate,
                    'efficiency_score': efficiency_score,
                    'phone': phone,
                    'city': city,
                    'vehicle_type': vehicle_type,
                    'vehicle_info': vehicle_type,
                    'last_ride': last_ride,
                    'last_login': last_login,
                    'created_at': driver_record.scraped_at if hasattr(driver_record, 'scraped_at') else None,
                    'updated_at': driver_record.scraped_at if hasattr(driver_record, 'scraped_at') else None,
                    'data_type': driver_record.data_type
                }
                
                all_drivers.append(driver_info_final)
                
            except Exception as e:
                print(f"Erro ao processar dados do motorista único: {e}")
                continue
        
        # Calcular métricas
        total_drivers = len(all_drivers)
        active_drivers = len([d for d in all_drivers if d['status'] == 'ativo'])
        
        # Média de avaliações
        ratings = [d['rating'] for d in all_drivers if d['rating'] > 0]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Top 5 motoristas por avaliação
        top_drivers = sorted(
            [d for d in all_drivers if d['rating'] > 0], 
            key=lambda x: x['rating'], 
            reverse=True
        )[:5]
        
        # Contagem por status
        drivers_by_status = {}
        for driver in all_drivers:
            status = driver['status']
            drivers_by_status[status] = drivers_by_status.get(status, 0) + 1
        
        # Estatísticas de corridas
        total_rides_all = sum(d['total_rides'] for d in all_drivers)
        avg_rides_per_driver = total_rides_all / total_drivers if total_drivers > 0 else 0
        
        # Performance metrics com categorização detalhada
        excellent_drivers = len([d for d in all_drivers if d['rating'] >= 4.5])
        good_drivers = len([d for d in all_drivers if 4.0 <= d['rating'] < 4.5])
        average_drivers = len([d for d in all_drivers if 3.5 <= d['rating'] < 4.0])
        below_average_drivers = len([d for d in all_drivers if 0 < d['rating'] < 3.5])
        
        # KPIs avançados
        activation_rate = (active_drivers / total_drivers * 100) if total_drivers > 0 else 0.0
        excellence_rate = (excellent_drivers / total_drivers * 100) if total_drivers > 0 else 0.0
        
        # Trend de performance baseado na avaliação média
        if average_rating >= 4.0:
            performance_trend = "positive"
        elif average_rating >= 3.5:
            performance_trend = "neutral"
        else:
            performance_trend = "negative"
        
        # Score de eficiência (combinação de rating e produtividade)
        efficiency_scores = [d['efficiency_score'] for d in all_drivers if d['efficiency_score'] > 0]
        avg_efficiency = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0.0
        
        return {
            "total_drivers": total_drivers,
            "active_drivers": active_drivers,
            "inactive_drivers": total_drivers - active_drivers,
            "online_drivers": active_drivers,  # Todos os ativos estão online
            "average_rating": round(average_rating, 2),
            "total_rides_completed": total_rides_all,
            "avg_rides_per_driver": round(avg_rides_per_driver, 2),
            "top_drivers": [
                {
                    "name": d['name'],
                    "rating": d['rating'],
                    "total_rides": d['total_rides'],
                    "efficiency": d['efficiency_score'],
                    "avg_rating": d['rating'],
                    "status": d['status']
                } for d in top_drivers
            ],
            "drivers_by_status": drivers_by_status,
            "performance_metrics": {
                "excellent_drivers": excellent_drivers,
                "good_drivers": good_drivers,
                "average_drivers": average_drivers,
                "below_average_drivers": below_average_drivers
            },
            "kpi_metrics": {
                "activation_rate": round(activation_rate, 1),
                "excellence_rate": round(excellence_rate, 1),
                "performance_trend": performance_trend,
                "efficiency_score": round(avg_efficiency, 1)
            },
            "periodo_dias": periodo
        }
        
    except Exception as e:
        print(f"Erro no endpoint drivers overview: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/by-city")
async def get_drivers_by_city(
    cidade: Optional[str] = Query(None, description="Nome da cidade para filtrar motoristas"),
    db: AsyncSession = Depends(get_db)
):
    """
    Buscar motoristas por cidade específica usando campo driver_ratings
    """
    try:
        if not cidade:
            raise HTTPException(status_code=400, detail="Parâmetro cidade é obrigatório")
            
        # Normalizar entrada da cidade
        cidade_busca = cidade.strip()
        
        # Buscar todos os registros da tabela drivers_data
        result = await db.execute(select(DriversData))
        rows = result.scalars().all()
        
        # Processar registros e filtrar por cidade
        motoristas = {"active": 0, "enrollment": 0, "leaderboard": 0, "total": 0}
        
        for row in rows:
            try:
                # Parse do JSON do additional_data (pode ser string ou dict)
                if isinstance(row.additional_data, str):
                    additional_data = json.loads(row.additional_data)
                else:
                    additional_data = row.additional_data
                
                cidade_motorista = additional_data.get('driver_ratings', '')
                
                # Verificar se a cidade bate (case insensitive)
                if cidade_busca.upper() in cidade_motorista.upper() or cidade_motorista.upper() in cidade_busca.upper():
                    data_type = row.data_type
                    
                    if data_type in motoristas:
                        motoristas[data_type] += 1
                        motoristas["total"] += 1
                        
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        return {
            "success": True,
            "cidade": cidade,
            "motoristas": motoristas,
            "total_ativos": motoristas["active"],
            "total_cadastrados": motoristas["total"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro no endpoint drivers by city: {e}")
        return {
            "success": False,
            "error": str(e),
            "cidade": cidade or "N/A",
            "motoristas": {"active": 0, "enrollment": 0, "leaderboard": 0, "total": 0},
            "total_ativos": 0,
            "total_cadastrados": 0
        }
