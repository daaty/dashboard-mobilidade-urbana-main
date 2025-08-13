from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from app.models.campanha import Campanha
from typing import Optional
import json
from datetime import datetime, timedelta
from services.city_service import get_cities_from_rides_data

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/overview-metas-agregadas")
async def get_overview_metas_agregadas(
    fase: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna visão geral das metas:
    - Motoristas adquiridos vs meta
    - Corridas de lançamento vs meta  
    - CAC por motorista e por corrida
    """
    
    # Buscar campanhas ativas
    query = select(Campanha)
    if fase:
        query = query.where(Campanha.fase == fase)
    
    result = await db.execute(query)
    campanhas = result.scalars().all()
    
    # Calcular métricas agregadas
    total_meta_quantidade = sum(c.meta_quantidade for c in campanhas)
    total_orcamento_previsto = sum(float(c.orcamento_previsto) for c in campanhas)
    total_custo_real = sum(float(c.custo_real or 0) for c in campanhas)
    
    # Buscar corridas reais para calcular realizações
    rides_result = await db.execute(select(RidesData))
    rides = rides_result.scalars().all()
    
    # Contar corridas por cidade
    corridas_por_cidade = {}
    cidades_reais = get_cities_from_rides_data()
    
    for cidade in cidades_reais:
        corridas_por_cidade[cidade] = 0
    
    for r in rides:
        ride_data = r.ride_data
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        
        if table_name == "Completed Rides":
            for rec in new_records:
                cidade = rec[15] if len(rec) > 15 else None
                if cidade and str(cidade).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade).strip()] += 1
    
    total_corridas_realizadas = sum(corridas_por_cidade.values())
    
    # Calcular CAC
    cac_por_corrida = total_custo_real / total_corridas_realizadas if total_corridas_realizadas > 0 else 0
    cac_por_motorista = total_custo_real / len(campanhas) if len(campanhas) > 0 else 0  # Simplificado
    
    return {
        "motoristas_meta": len(campanhas) * 4,  # 4 motoristas por campanha em média
        "motoristas_realizados": len(campanhas) * 3,  # Simulado
        "corridas_meta": total_meta_quantidade,
        "corridas_realizadas": total_corridas_realizadas,
        "cac_corrida": round(cac_por_corrida, 2),
        "cac_motorista": round(cac_por_motorista, 2),
        "orcamento_previsto": total_orcamento_previsto,
        "custo_real": total_custo_real
    }

@router.get("/penetracao-mercado/{cidade}")
async def get_penetracao_mercado(
    cidade: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna dados da cidade específica:
    - População e público-alvo
    - Evolução mensal (meta vs realizado)
    - Percentual de penetração atual
    """
    
    # Dados demográficos por cidade (conforme plano)
    dados_demograficos = {
        "GUARANTA DO NORTE": {
            "populacao_estimada": 32010,
            "publico_alvo": 14045,
            "meta_corridas_mes_1": 70,
            "meta_corridas_mes_2": 140,
            "meta_corridas_mes_3": 280,
            "meta_corridas_mes_6": 1544
        },
        "MATUPA": {
            "populacao_estimada": 15420,
            "publico_alvo": 6980,
            "meta_corridas_mes_1": 35,
            "meta_corridas_mes_2": 70,
            "meta_corridas_mes_3": 140,
            "meta_corridas_mes_6": 770
        },
        "PEIXOTO": {
            "populacao_estimada": 28500,
            "publico_alvo": 12000,
            "meta_corridas_mes_1": 60,
            "meta_corridas_mes_2": 120,
            "meta_corridas_mes_3": 240,
            "meta_corridas_mes_6": 1200
        }
    }
    
    cidade_dados = dados_demograficos.get(cidade.upper(), {
        "populacao_estimada": 20000,
        "publico_alvo": 8000,
        "meta_corridas_mes_1": 50,
        "meta_corridas_mes_2": 100,
        "meta_corridas_mes_3": 200,
        "meta_corridas_mes_6": 1000
    })
    
    # Buscar corridas realizadas da cidade
    rides_result = await db.execute(select(RidesData))
    rides = rides_result.scalars().all()
    
    corridas_realizadas = 0
    for r in rides:
        ride_data = r.ride_data
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        
        if table_name == "Completed Rides":
            for rec in new_records:
                cidade_rec = rec[15] if len(rec) > 15 else None
                if cidade_rec and str(cidade_rec).strip().upper() == cidade.upper():
                    corridas_realizadas += 1
    
    # Calcular penetração
    penetracao_atual = (corridas_realizadas / cidade_dados["publico_alvo"]) * 100 if cidade_dados["publico_alvo"] > 0 else 0
    
    # Evolução mensal (dados simulados para demonstração)
    evolucao_mensal = [
        {"mes": "Mês 1", "meta": cidade_dados["meta_corridas_mes_1"], "realizado": min(corridas_realizadas, cidade_dados["meta_corridas_mes_1"])},
        {"mes": "Mês 2", "meta": cidade_dados["meta_corridas_mes_2"], "realizado": min(max(corridas_realizadas - cidade_dados["meta_corridas_mes_1"], 0), cidade_dados["meta_corridas_mes_2"])},
        {"mes": "Mês 3", "meta": cidade_dados["meta_corridas_mes_3"], "realizado": min(max(corridas_realizadas - cidade_dados["meta_corridas_mes_2"], 0), cidade_dados["meta_corridas_mes_3"])},
    ]
    
    return {
        "cidade": cidade,
        "populacao_estimada": cidade_dados["populacao_estimada"],
        "publico_alvo": cidade_dados["publico_alvo"],
        "corridas_realizadas": corridas_realizadas,
        "penetracao_atual": round(penetracao_atual, 2),
        "evolucao_mensal": evolucao_mensal
    }

@router.get("/tabela-desempenho-campanhas")
async def get_tabela_desempenho_campanhas(
    fase: Optional[str] = Query(None),
    cidade: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna tabela detalhada de todas as campanhas:
    - Por fase, cidade, tipo de meta
    - Atingimento percentual
    - Variação de custo
    """
    
    query = select(Campanha)
    if fase and fase != "todas":
        query = query.where(Campanha.fase == fase)
    if cidade and cidade != "todos":
        query = query.where(Campanha.cidade == cidade)
    
    result = await db.execute(query)
    campanhas = result.scalars().all()
    
    # Buscar dados de corridas para calcular realizações
    rides_result = await db.execute(select(RidesData))
    rides = rides_result.scalars().all()
    
    corridas_por_cidade = {}
    cidades_reais = get_cities_from_rides_data()
    
    for cidade_nome in cidades_reais:
        corridas_por_cidade[cidade_nome] = 0
    
    for r in rides:
        ride_data = r.ride_data
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        
        if table_name == "Completed Rides":
            for rec in new_records:
                cidade_rec = rec[15] if len(rec) > 15 else None
                if cidade_rec and str(cidade_rec).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade_rec).strip()] += 1
    
    tabela_campanhas = []
    for campanha in campanhas:
        realizado = corridas_por_cidade.get(campanha.cidade, 0)
        atingimento = (realizado / campanha.meta_quantidade * 100) if campanha.meta_quantidade > 0 else 0
        variacao_custo = ((float(campanha.custo_real or 0) - float(campanha.orcamento_previsto)) / float(campanha.orcamento_previsto) * 100) if campanha.orcamento_previsto > 0 else 0
        
        tabela_campanhas.append({
            "id": campanha.id,
            "nome": campanha.nome,
            "fase": campanha.fase,
            "cidade": campanha.cidade,
            "tipo_campanha": campanha.tipo_campanha,
            "meta_quantidade": campanha.meta_quantidade,
            "realizado": realizado,
            "atingimento_percentual": round(atingimento, 1),
            "orcamento_previsto": float(campanha.orcamento_previsto),
            "custo_real": float(campanha.custo_real or 0),
            "variacao_custo": round(variacao_custo, 1),
            "status": campanha.status,
            "data_inicio": campanha.data_inicio.isoformat(),
            "data_fim": campanha.data_fim.isoformat()
        })
    
    return {
        "campanhas": tabela_campanhas,
        "total": len(tabela_campanhas)
    }
