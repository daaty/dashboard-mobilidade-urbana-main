from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from typing import List, Dict, Any, Optional
from ..config.database import get_db

router = APIRouter()

@router.get("/api/drivers/by-city")
async def get_drivers_by_city(
    cidade: Optional[str] = Query(None, description="Nome da cidade para filtrar motoristas"),
    db: Session = Depends(get_db)
):
    """
    Buscar motoristas por cidade específica usando campo driver_ratings
    """
    try:
        # Query para buscar motoristas por cidade
        if cidade:
            # Normalizar entrada da cidade
            cidade_busca = cidade.strip()
            
            # Buscar motoristas de uma cidade específica
            query = text("""
                SELECT 
                    data_type,
                    COUNT(*) as total
                FROM drivers_data 
                WHERE additional_data::text LIKE :cidade_pattern
                GROUP BY data_type
                ORDER BY data_type
            """)
            result = db.execute(query, {"cidade_pattern": f'%{cidade_busca}%'})
        else:
            return {"error": "Parâmetro cidade é obrigatório"}
        
        rows = result.fetchall()
        
        # Processar resultados
        motoristas = {"active": 0, "enrollment": 0, "leaderboard": 0, "total": 0}
        
        for row in rows:
            data_type = row.data_type
            count = row.total
            
            if data_type in motoristas:
                motoristas[data_type] = count
                motoristas["total"] += count
        
        return {
            "success": True,
            "cidade": cidade,
            "motoristas": motoristas,
            "total_ativos": motoristas["active"],
            "total_cadastrados": motoristas["total"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cidade": cidade or "N/A",
            "motoristas": {"active": 0, "enrollment": 0, "leaderboard": 0, "total": 0},
            "total_ativos": 0,
            "total_cadastrados": 0
        }

@router.get("/api/drivers/by-city/{cidade}")
async def get_drivers_by_city(cidade: str, db: Session = Depends(get_db)):
    """
    Buscar motoristas ativos por cidade
    """
    try:
        # Query para buscar motoristas ativos por cidade
        query = text("""
            SELECT 
                driver_id,
                name,
                email,
                mobile,
                additional_data,
                data_type,
                page_source
            FROM drivers_data 
            WHERE data_type = 'active'
            AND additional_data LIKE :cidade_pattern
        """)
        
        # Executar query
        result = db.execute(query, {"cidade_pattern": f'%"driver_ratings":"{cidade}"%'})
        rows = result.fetchall()
        
        motoristas = []
        for row in rows:
            try:
                # Parse do JSON additional_data
                additional_data = json.loads(row.additional_data) if row.additional_data else {}
                
                motorista = {
                    "driver_id": row.driver_id,
                    "name": row.name,
                    "email": row.email,
                    "mobile": row.mobile,
                    "data_type": row.data_type,
                    "page_source": row.page_source,
                    "city": additional_data.get("driver_ratings", ""),
                    "status": additional_data.get("status", ""),
                    "last_login": additional_data.get("last_login", ""),
                    "last_ride": additional_data.get("last_ride", ""),
                    "vehicle_number": additional_data.get("vehicle_number", ""),
                    "rides_in_last_30_days": additional_data.get("rides_in_last_30_days", ""),
                    "rides_in_last_7_days": additional_data.get("rides_in_last_7_days", "")
                }
                motoristas.append(motorista)
                
            except json.JSONDecodeError:
                continue
        
        return {
            "success": True,
            "cidade": cidade,
            "total_motoristas": len(motoristas),
            "motoristas": motoristas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar motoristas: {str(e)}")

@router.get("/api/drivers/cities")
async def get_drivers_cities(db: Session = Depends(get_db)):
    """
    Listar cidades com motoristas ativos
    """
    try:
        query = text("""
            SELECT DISTINCT additional_data
            FROM drivers_data 
            WHERE data_type = 'active'
            AND additional_data IS NOT NULL
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        cidades = set()
        for row in rows:
            try:
                additional_data = json.loads(row.additional_data)
                cidade = additional_data.get("driver_ratings", "")
                if cidade:
                    cidades.add(cidade)
            except json.JSONDecodeError:
                continue
        
        return {
            "success": True,
            "cidades": sorted(list(cidades))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cidades: {str(e)}")
