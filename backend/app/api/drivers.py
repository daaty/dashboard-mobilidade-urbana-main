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
        
        # Processar dados dos motoristas
        drivers_processed = set()
        all_drivers = []
        
        for driver_record in drivers_data:
            # Filtro por data
            if hasattr(driver_record, 'scraped_at') and driver_record.scraped_at:
                if driver_record.scraped_at < data_limite:
                    continue
            
            try:
                # O campo additional_data contém os dados JSON
                driver_data = driver_record.additional_data
                if isinstance(driver_data, str):
                    driver_data = json.loads(driver_data)
                
                # Extrair informações do motorista baseado na estrutura real
                driver_id = driver_record.driver_id
                driver_name = driver_record.name
                
                if not driver_id or driver_id in drivers_processed:
                    continue
                
                drivers_processed.add(driver_id)
                
                # Extrair dados do JSON additional_data com fallbacks seguros
                status = driver_data.get('status', '0')
                rating = 0.0
                total_rides = 0
                efficiency_score = 0.0
                
                # Tentar extrair rating e corridas dos dados JSON
                try:
                    # Verifica se existe campo 'rating' ou 'avaliacao'
                    if 'rating' in driver_data:
                        rating = float(driver_data['rating'])
                    elif 'avaliacao' in driver_data:
                        rating = float(driver_data['avaliacao'])
                    elif status and status != '0':
                        # Se status for numérico, pode ser o rating
                        rating = float(status)
                except:
                    rating = 0.0
                
                # Tentar extrair total de corridas
                try:
                    if 'total_rides' in driver_data:
                        total_rides = int(driver_data['total_rides'])
                    elif 'corridas' in driver_data:
                        total_rides = int(driver_data['corridas'])
                    elif 'viagens' in driver_data:
                        total_rides = int(driver_data['viagens'])
                except:
                    total_rides = 0
                
                # Calcular efficiency score baseado em dados disponíveis
                try:
                    if 'efficiency_score' in driver_data:
                        efficiency_score = float(driver_data['efficiency_score'])
                    else:
                        # Calcular score baseado em rating e total de corridas
                        efficiency_score = (rating * 10 + total_rides * 0.1)
                        efficiency_score = min(efficiency_score, 100)
                except:
                    efficiency_score = 0.0
                
                # Determinar status do motorista de forma mais robusta
                if 'status' in driver_data and driver_data['status']:
                    driver_status = driver_data['status'].lower()
                    if driver_status in ['ativo', 'active', '1', 'online']:
                        driver_status = 'ativo'
                    else:
                        driver_status = 'inativo'
                else:
                    driver_status = 'ativo' if driver_record.data_type == 'active' else 'inativo'
                
                # Extrair informações adicionais com validação
                last_ride = driver_data.get('last_ride', '')
                last_login = driver_data.get('last_login', '')
                vehicle_info = driver_record.mobile if hasattr(driver_record, 'mobile') else ''
                
                driver_info = {
                    'id': driver_id,
                    'name': driver_name if driver_name and driver_name != 'None' else f"Motorista {driver_id}",
                    'status': driver_status,
                    'rating': rating,
                    'total_rides': total_rides,
                    'efficiency_score': efficiency_score,
                    'phone': driver_record.email if hasattr(driver_record, 'email') else '',
                    'vehicle_info': vehicle_info,
                    'last_ride': last_ride,
                    'last_login': last_login,
                    'created_at': driver_record.created_at if hasattr(driver_record, 'created_at') else None,
                    'updated_at': driver_record.updated_at if hasattr(driver_record, 'updated_at') else None
                }
                
                all_drivers.append(driver_info)
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Erro ao processar dados do motorista: {e}")
                continue
        
        # Calcular métricas
        total_drivers = len(all_drivers)
        active_drivers = len([d for d in all_drivers if d['status'] == 'active'])
        
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
            "average_rating": round(average_rating, 2),
            "total_rides_completed": total_rides_all,
            "avg_rides_per_driver": round(avg_rides_per_driver, 2),
            "top_drivers": [
                {
                    "name": d['name'],
                    "rating": d['rating'],
                    "total_rides": d['total_rides'],
                    "efficiency": d['efficiency_score'],
                    "avg_rating": d['rating']
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
