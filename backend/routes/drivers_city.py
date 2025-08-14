from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..config.database import get_db
import json
from typing import Optional

router = APIRouter(prefix="/api/drivers", tags=["drivers"])

@router.get("/by-city")
async def get_drivers_by_city(
    cidade: Optional[str] = Query(None, description="Nome da cidade para filtrar motoristas"),
    db: Session = Depends(get_db)
):
    """
    Buscar motoristas por cidade específica
    """
    try:
        # Query base para buscar motoristas por cidade
        if cidade:
            # Buscar motoristas de uma cidade específica
            query = text("""
                SELECT 
                    data_type,
                    COUNT(*) as total,
                    additional_data
                FROM drivers_data 
                WHERE additional_data::text LIKE :cidade_pattern
                GROUP BY data_type, additional_data
                ORDER BY data_type
            """)
            result = db.execute(query, {"cidade_pattern": f'%{cidade}%'})
        else:
            # Buscar todos os motoristas agrupados por tipo
            query = text("""
                SELECT 
                    data_type,
                    COUNT(*) as total,
                    additional_data
                FROM drivers_data 
                GROUP BY data_type, additional_data
                ORDER BY data_type
            """)
            result = db.execute(query)
        
        rows = result.fetchall()
        
        # Processar resultados e extrair cidades
        motoristas_por_cidade = {}
        total_ativos = 0
        total_enrollment = 0
        
        for row in rows:
            data_type = row.data_type
            count = row.total
            additional_data_str = row.additional_data
            
            try:
                # Parse do JSON do additional_data
                additional_data = json.loads(additional_data_str)
                cidade_motorista = additional_data.get('driver_ratings', 'Unknown')
                
                # Normalizar nome da cidade
                cidade_norm = cidade_motorista.strip()
                
                if cidade_norm not in motoristas_por_cidade:
                    motoristas_por_cidade[cidade_norm] = {
                        'active': 0,
                        'enrollment': 0,
                        'leaderboard': 0,
                        'total': 0
                    }
                
                # Contar por tipo
                if data_type in ['active', 'enrollment', 'leaderboard']:
                    motoristas_por_cidade[cidade_norm][data_type] += count
                    motoristas_por_cidade[cidade_norm]['total'] += count
                    
                    if data_type == 'active':
                        total_ativos += count
                    elif data_type == 'enrollment':
                        total_enrollment += count
                        
            except json.JSONDecodeError:
                continue
        
        # Se foi solicitada cidade específica, retornar só ela
        if cidade:
            cidade_encontrada = None
            for cidade_key in motoristas_por_cidade.keys():
                if cidade.upper() in cidade_key.upper() or cidade_key.upper() in cidade.upper():
                    cidade_encontrada = motoristas_por_cidade[cidade_key]
                    break
            
            if cidade_encontrada:
                return {
                    "success": True,
                    "cidade": cidade,
                    "motoristas": cidade_encontrada,
                    "total_ativos": cidade_encontrada['active'],
                    "total_cadastrados": cidade_encontrada['total']
                }
            else:
                return {
                    "success": False,
                    "cidade": cidade,
                    "motoristas": {"active": 0, "enrollment": 0, "leaderboard": 0, "total": 0},
                    "total_ativos": 0,
                    "total_cadastrados": 0
                }
        
        # Retornar todas as cidades
        return {
            "success": True,
            "motoristas_por_cidade": motoristas_por_cidade,
            "resumo": {
                "total_cidades": len(motoristas_por_cidade),
                "total_ativos_geral": total_ativos,
                "total_enrollment_geral": total_enrollment
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "motoristas_por_cidade": {},
            "total_ativos": 0,
            "total_cadastrados": 0
        }
