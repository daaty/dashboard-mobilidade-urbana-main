from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from typing import Optional

import json
from datetime import datetime, timedelta
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.city_service import get_cities_from_rides_data

def extract_datetime_from_record(rec, index):
    """Extrai data/hora de um registro, lidando com AMBOS os formatos (scraper + frontend)"""
    if index >= len(rec):
        return None
    
    value = str(rec[index]).strip()
    
    # Formato do scraper: "202508202025-08-20 16:59:50"
    scraper_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", value)
    if scraper_match:
        return scraper_match.group(1)
    
    # Formato do frontend: "2025-08-20 16:59:50" (sem prefixo)
    frontend_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", value)
    if frontend_match:
        return frontend_match.group(1)
    
    return None

def extract_city_from_record(rec):
    """Detecta cidade baseada nos dados do registro"""
    # Diferentes índices dependendo do tipo de corrida
    possible_city_indices = [15, 17, 8, 9, 10]  # Diferentes posições onde a cidade pode estar
    
    for idx in possible_city_indices:
        if idx < len(rec) and rec[idx]:
            city_str = str(rec[idx]).strip().upper()
            # Limpar dados de cidade
            if city_str in ["MATUPA", "MATUPÁ"]:
                return "MATUPA"
            elif city_str == "PEIXOTO":
                return "PEIXOTO"
            elif "GUARANTA" in city_str:
                return "GUARANTA DO NORTE"
    
    # Fallback: detectar pela localização (índices 5 e 6)
    if len(rec) > 6:
        local_str = str(rec[5]) if len(rec) > 5 else ""
        destino_str = str(rec[6]) if len(rec) > 6 else ""
        local_destino = (local_str + " " + destino_str).upper()
        
        if "MATUPA" in local_destino or "MATUPÁ" in local_destino:
            return "MATUPA"
        elif "PEIXOTO" in local_destino:
            return "PEIXOTO"
        elif "GUARANTA" in local_destino:
            return "GUARANTA DO NORTE"
    
    return "Unnamed"  # Default se não conseguir detectar


def get_user_info_from_record(rec):
    """Heurística para extrair usuario_id e nome do passageiro de registros heterogêneos.
    Retorna (usuario_id, nome)
    """
    usuario_id = None
    nome = None
    try:
        # Caso comum: rec[5] pode conter id numérico ou telefone; rec[3] costuma ser o nome
        if len(rec) > 5 and rec[5] and str(rec[5]).strip():
            if str(rec[5]).isdigit():
                usuario_id = str(rec[5])
                if len(rec) > 3 and rec[3] and not str(rec[3]).isdigit():
                    nome = rec[3]
            else:
                # rec[5] pode ser o nome do passageiro
                nome = rec[5]
                # tentar preencher usuario_id com rec[1]
                if len(rec) > 1 and str(rec[1]).isdigit():
                    usuario_id = str(rec[1])

        # fallbacks para nome
        if not nome:
            if len(rec) > 1 and rec[1] and not str(rec[1]).isdigit():
                nome = rec[1]
            elif len(rec) > 3 and rec[3] and not str(rec[3]).isdigit():
                nome = rec[3]
            elif len(rec) > 0 and rec[0]:
                nome = rec[0]

        # fallback para usuario_id: procurar campo numérico entre 1..3
        if not usuario_id:
            for idx in (1, 2, 3):
                if len(rec) > idx and rec[idx] and str(rec[idx]).isdigit():
                    usuario_id = str(rec[idx])
                    break
    except Exception:
        # Silenciar falhas na heurística e retornar valores parciais
        pass
    return usuario_id, nome

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

# Endpoint de metas por cidade (dados reais)
@router.get("/metas-cidades")
async def get_metas_cidades(db: AsyncSession = Depends(get_db)):
    """Endpoint para retornar metas por cidade usando dados reais das 3 cidades disponíveis."""
    
    # Usar o city_service para obter apenas as cidades reais
    cidades_reais = get_cities_from_rides_data()
    
    # Buscar todos os registros da tabela rides_data
    result = await db.execute(select(RidesData))
    rides = result.scalars().all()

    # Inicializar dados para as 3 cidades reais
    corridas_por_cidade = {}
    for cidade in cidades_reais:
        corridas_por_cidade[cidade] = {"concluidas": 0, "canceladas": 0, "perdidas": 0}
    
    for r in rides:
        ride_data = r.ride_data
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        
        # Processar corridas concluídas
        if table_name in ["Completed Rides", "corridas_concluidas"]:
            for rec in new_records:
                cidade = rec[15] if len(rec) > 15 else None
                if cidade and str(cidade).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade).strip()]["concluidas"] += 1
        
        # Processar corridas canceladas
        elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
            for rec in new_records:
                cidade = rec[17] if len(rec) > 17 else None  # Usar índice correto do city_service
                if cidade and str(cidade).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade).strip()]["canceladas"] += 1
        
        # Processar corridas perdidas
        elif table_name in ["Missed Rides", "corridas_perdidas"]:
            for rec in new_records:
                cidade = rec[8] if len(rec) > 8 else None  # Usar índice correto do city_service
                if cidade and str(cidade).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade).strip()]["perdidas"] += 1

    # Definir metas por cidade (configuração para as 3 cidades reais)
    metas_cidades = {
        "GUARANTA DO NORTE": {"meta": 500, "publico_alvo": 2000},
        "MATUPA": {"meta": 500, "publico_alvo": 2000},
        "PEIXOTO": {"meta": 500, "publico_alvo": 2000}
    }
    
    # Construir resposta apenas com as 3 cidades reais
    cidades = []
    for cidade_nome, dados in corridas_por_cidade.items():
        realizado = dados["concluidas"]
        meta_info = metas_cidades.get(cidade_nome, {"meta": 500, "publico_alvo": 2000})
        meta = meta_info["meta"]
        
        # Calcular percentual
        percentual = (realizado / meta * 100) if meta > 0 else 0
        
        # Determinar status
        if percentual >= 100:
            status = "success"
        elif percentual >= 80:
            status = "warning"
        else:
            status = "danger"
        
        cidade_data = {
            "cidade": cidade_nome,
            "status": status,
            "meta_corridas": meta,
            "meta_receita": meta * 25.0,  # Assumindo R$ 25 por corrida
            "publico_alvo": meta_info["publico_alvo"],
            "progresso_atual": percentual,
            "realizado": realizado,
            "meta": meta,
            "percentual": percentual,
            "concluidas": dados["concluidas"],
            "canceladas": dados["canceladas"],
            "perdidas": dados["perdidas"],
            "metas_mensais": [
                {"mes": "Jan", "valor": int(meta/12)},
                {"mes": "Fev", "valor": int(meta/12)},
                {"mes": "Mar", "valor": int(meta/12)},
                {"mes": "Abr", "valor": int(meta/12)},
                {"mes": "Mai", "valor": int(meta/12)},
                {"mes": "Jun", "valor": int(meta/12)}
            ]
        }
        cidades.append(cidade_data)
    
    # Se não há dados, retornar estrutura básica para as 3 cidades principais
    if not cidades:
        cidades = []
        for cidade_nome, meta_info in metas_cidades.items():
            cidades.append({
                "cidade": cidade_nome,
                "status": "danger",
                "meta_corridas": meta_info["meta"],
                "meta_receita": meta_info["meta"] * 25.0,
                "publico_alvo": meta_info["publico_alvo"],
                "progresso_atual": 0.0,
                "realizado": 0,
                "meta": meta_info["meta"],
                "percentual": 0.0,
                "concluidas": 0,
                "canceladas": 0,
                "perdidas": 0,
                "metas_mensais": [
                    {"mes": "Jan", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Fev", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Mar", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Abr", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Mai", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Jun", "valor": int(meta_info["meta"]/12)}
                ]
            })
    
    return JSONResponse(content=cidades)
    # Garantir que todos os campos numéricos estejam presentes e válidos
    for c in cidades:
        if c.get("progresso_atual") is None:
            c["progresso_atual"] = 0.0
        if c.get("meta_corridas") is None:
            c["meta_corridas"] = 0
        if c.get("meta_receita") is None:
            c["meta_receita"] = 0.0
        if c.get("publico_alvo") is None:
            c["publico_alvo"] = 0
        if c.get("realizado") is None:
            c["realizado"] = 0
        if c.get("meta") is None:
            c["meta"] = c.get("meta_corridas", 0)
        
        # Calcular percentual com base no realizado/meta
        if c["meta"] > 0:
            c["percentual"] = (c["realizado"] / c["meta"]) * 100
        else:
            c["percentual"] = 0.0
            
        # Ajustar status baseado no percentual
        if c["percentual"] >= 100:
            c["status"] = "success"
        elif c["percentual"] >= 80:
            c["status"] = "warning"
        else:
            c["status"] = "danger"
            
    return JSONResponse(content=cidades)

@router.get("/metas-cidades")
async def get_metas_cidades():
    """Endpoint para retornar metas por cidade (mock inicial)."""
    cidades = [
        {
            "cidade": "Monte Verde",
            "status": "success",
            "meta_corridas": 1200,
            "meta_receita": 30000,
            "publico_alvo": 5000,
            "progresso_atual": 80.5,
            "metas_mensais": [
                {"mes": "Jan", "valor": 200},
                {"mes": "Fev", "valor": 250},
                {"mes": "Mar", "valor": 300},
                {"mes": "Abr", "valor": 250},
                {"mes": "Mai", "valor": 100},
                {"mes": "Jun", "valor": 100}
            ]
        },
        {
            "cidade": "Colíder",
            "status": "warning",
            "meta_corridas": 900,
            "meta_receita": 18000,
            "publico_alvo": 4000,
            "progresso_atual": 65.2,
            "metas_mensais": [
                {"mes": "Jan", "valor": 150},
                {"mes": "Fev", "valor": 180},
                {"mes": "Mar", "valor": 200},
                {"mes": "Abr", "valor": 180},
                {"mes": "Mai", "valor": 100},
                {"mes": "Jun", "valor": 90}
            ]
        },
        {
            "cidade": "Alta Floresta",
            "status": "danger",
            "meta_corridas": 700,
            "meta_receita": 12000,
            "publico_alvo": 3500,
            "progresso_atual": 40.0,
            "metas_mensais": [
                {"mes": "Jan", "valor": 100},
                {"mes": "Fev", "valor": 120},
                {"mes": "Mar", "valor": 150},
                {"mes": "Abr", "valor": 130},
                {"mes": "Mai", "valor": 100},
                {"mes": "Jun", "valor": 100}
            ]
        }
    ]
    return JSONResponse(content=cidades)
    return JSONResponse(content=cidades)

def ordenar_por_data(lista):
    return sorted(lista, key=lambda x: x.get("dt_corrida", datetime.min), reverse=True)

async def get_db():
    async with SessionLocal() as session:
        yield session

# Redefinir endpoint de metas por cidade com dados reais
@router.get("/metas-cidades-real")
async def get_metas_cidades_real(db: AsyncSession = Depends(get_db)):
    """Endpoint para retornar metas por cidade usando dados reais das 3 cidades disponíveis."""
    
    # Usar o city_service para obter apenas as cidades reais
    cidades_reais = get_cities_from_rides_data()
    
    # Buscar todos os registros da tabela rides_data
    result = await db.execute(select(RidesData))
    rides = result.scalars().all()

    # Inicializar dados para as 3 cidades reais
    corridas_por_cidade = {}
    for cidade in cidades_reais:
        corridas_por_cidade[cidade] = {"concluidas": 0, "canceladas": 0, "perdidas": 0}
    
    for r in rides:
        ride_data = r.ride_data
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        
        # Processar corridas concluídas
        if table_name in ["Completed Rides", "corridas_concluidas"]:
            for rec in new_records:
                cidade = rec[15] if len(rec) > 15 else None
                if cidade and str(cidade).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade).strip()]["concluidas"] += 1
        
        # Processar corridas canceladas
        elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
            for rec in new_records:
                cidade = rec[17] if len(rec) > 17 else None  # Usar índice correto do city_service
                if cidade and str(cidade).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade).strip()]["canceladas"] += 1
        
        # Processar corridas perdidas
        elif table_name in ["Missed Rides", "corridas_perdidas"]:
            for rec in new_records:
                cidade = rec[8] if len(rec) > 8 else None  # Usar índice correto do city_service
                if cidade and str(cidade).strip() in cidades_reais:
                    corridas_por_cidade[str(cidade).strip()]["perdidas"] += 1

    # Definir metas por cidade (configuração para as 3 cidades reais)
    metas_cidades = {
        "GUARANTA DO NORTE": {"meta": 500, "publico_alvo": 2000},
        "MATUPA": {"meta": 500, "publico_alvo": 2000},
        "PEIXOTO": {"meta": 500, "publico_alvo": 2000}
    }
    
    # Construir resposta apenas com as 3 cidades reais
    cidades = []
    for cidade_nome, dados in corridas_por_cidade.items():
        realizado = dados["concluidas"]
        meta_info = metas_cidades.get(cidade_nome, {"meta": 500, "publico_alvo": 2000})
        meta = meta_info["meta"]
        
        # Calcular percentual
        percentual = (realizado / meta * 100) if meta > 0 else 0
        
        # Determinar status
        if percentual >= 100:
            status = "success"
        elif percentual >= 80:
            status = "warning"
        else:
            status = "danger"
        
        cidade_data = {
            "cidade": cidade_nome,
            "status": status,
            "meta_corridas": meta,
            "meta_receita": meta * 25.0,  # Assumindo R$ 25 por corrida
            "publico_alvo": meta_info["publico_alvo"],
            "progresso_atual": percentual,
            "realizado": realizado,
            "meta": meta,
            "percentual": percentual,
            "concluidas": dados["concluidas"],
            "canceladas": dados["canceladas"],
            "perdidas": dados["perdidas"],
            "metas_mensais": [
                {"mes": "Jan", "valor": int(meta/12)},
                {"mes": "Fev", "valor": int(meta/12)},
                {"mes": "Mar", "valor": int(meta/12)},
                {"mes": "Abr", "valor": int(meta/12)},
                {"mes": "Mai", "valor": int(meta/12)},
                {"mes": "Jun", "valor": int(meta/12)}
            ]
        }
        cidades.append(cidade_data)
    
    # Se não há dados, retornar estrutura básica para as 3 cidades principais
    if not cidades:
        cidades = []
        for cidade_nome, meta_info in metas_cidades.items():
            cidades.append({
                "cidade": cidade_nome,
                "status": "danger",
                "meta_corridas": meta_info["meta"],
                "meta_receita": meta_info["meta"] * 25.0,
                "publico_alvo": meta_info["publico_alvo"],
                "progresso_atual": 0.0,
                "realizado": 0,
                "meta": meta_info["meta"],
                "percentual": 0.0,
                "concluidas": 0,
                "canceladas": 0,
                "perdidas": 0,
                "metas_mensais": [
                    {"mes": "Jan", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Fev", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Mar", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Abr", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Mai", "valor": int(meta_info["meta"]/12)},
                    {"mes": "Jun", "valor": int(meta_info["meta"]/12)}
                ]
            })
    
    return JSONResponse(content=cidades)

@router.get("/cities")
async def get_cities():
    """Retorna lista de cidades extraídas dos dados reais"""
    try:
        cities = get_cities_from_rides_data()
        return {
            "success": True,
            "cities": cities
        }
    except Exception as e:
        return {
            "success": False,
            "cities": [],
            "error": str(e)
        }

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    return {"status": "ok", "message": "Backend funcionando"}

@router.get("/overview")
async def get_metrics_overview(
    db: AsyncSession = Depends(get_db),
    periodo: str = Query("30d", enum=["hoje", "7d", "30d", "3m", "6m", "12m"], description="Período do filtro: hoje, 7d, 30d, 3m, 6m, 12m"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade específica")
):
    # Buscar todos os registros da tabela rides_data
    result = await db.execute(select(RidesData))
    rides = result.scalars().all()

    concluidas, canceladas, perdidas = [], [], []
    concluidas_ant, canceladas_ant, perdidas_ant = [], [], []

    # Definir datas de filtro
    now = datetime.now()
    if periodo == "hoje":
        dt_ini = now.replace(hour=0, minute=0, second=0, microsecond=0)
        dt_fim = now
        dt_ini_ant = dt_ini - timedelta(days=1)
        dt_fim_ant = dt_ini
    elif periodo == "7d":
        dt_ini = now - timedelta(days=7)
        dt_fim = now
        dt_ini_ant = dt_ini - timedelta(days=7)
        dt_fim_ant = dt_ini
    elif periodo == "30d":
        dt_ini = now - timedelta(days=30)
        dt_fim = now
        dt_ini_ant = dt_ini - timedelta(days=30)
        dt_fim_ant = dt_ini
    elif periodo == "3m":
        dt_ini = now - timedelta(days=90)
        dt_fim = now
        dt_ini_ant = dt_ini - timedelta(days=90)
        dt_fim_ant = dt_ini
    elif periodo == "6m":
        dt_ini = now - timedelta(days=180)
        dt_fim = now
        dt_ini_ant = dt_ini - timedelta(days=180)
        dt_fim_ant = dt_ini
    else:  # "12m"
        dt_ini = now - timedelta(days=365)
        dt_fim = now
        dt_ini_ant = dt_ini - timedelta(days=365)
        dt_fim_ant = dt_ini

    # Função para gerar avatar fictício baseado no nome
    def gerar_avatar(nome):
        if not nome or not isinstance(nome, str):
            return "https://ui-avatars.com/api/?name=User&background=random"
        nome_url = str(nome).replace(" ", "+")
        return f"https://ui-avatars.com/api/?name={nome_url}&background=random"

    # Extrair e processar os dados do campo ride_data (JSON) - apenas UMA vez, com deduplicação e nome do passageiro
    ids_concluidas = set()
    ids_canceladas = set()
    ids_perdidas = set()
    for r in rides:
        ride_data = r.ride_data
        scraped_at = r.scraped_at if hasattr(r, 'scraped_at') else None
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        # Completed Rides (aceita nomes em português e inglês)
        if table_name in ["Completed Rides", "corridas_concluidas"]:
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                
                # DEDUPLICAÇÃO: Pular se ID já foi processado
                if id_corrida in ids_concluidas:
                    continue
                    
                # Forçar índice fixo: Completed -> nome em rec[3] (fallback para rec[2])
                usuario_id = None
                nome_passageiro = None
                telefone = None
                if len(rec) > 3 and rec[3] and not str(rec[3]).isdigit():
                    nome_passageiro = rec[3]
                elif len(rec) > 2 and rec[2] and not str(rec[2]).isdigit():
                    nome_passageiro = rec[2]
                # tentar detectar telefone em posições comuns (3 ou 4)
                if len(rec) > 3 and isinstance(rec[3], str) and rec[3].strip().startswith('+'):
                    telefone = rec[3]
                elif len(rec) > 4 and isinstance(rec[4], str) and rec[4].strip().startswith('+'):
                    telefone = rec[4]
                # usuario_id tentar detectar nas posições 1..3
                for idx in (1,2,3):
                    if len(rec) > idx and rec[idx] and str(rec[idx]).isdigit():
                        usuario_id = rec[idx]
                        break
                # Usar nome do passageiro como principal, motorista como fallback
                nome_motorista = rec[1] if len(rec) > 1 else None
                nome = nome_passageiro or nome_motorista or "Usuário"
                
                # Corrigir índices para corridas concluídas baseado na estrutura real da VPS
                # Para dados do Excel: [6] = data_solicitacao, [7] = data_conclusao 
                # Para dados do Scraper: [7] = data_solicitacao, [8] = data_conclusao
                hora_solicitacao = None
                hora_conclusao = None
                
                # Detectar se é dado do scraper ou Excel pela fonte
                if r.source == "monitoring-service-adapted":
                    # Dados do scraper
                    hora_solicitacao = rec[7] if len(rec) > 7 else None
                    hora_conclusao = rec[8] if len(rec) > 8 else None
                else:
                    # Dados do Excel
                    hora_solicitacao = rec[6] if len(rec) > 6 else None
                    hora_conclusao = rec[7] if len(rec) > 7 else None
                
                dt_corrida = None
                hora_formatada = None
                
                # Usar hora de conclusão como principal, solicitação como fallback
                hora = hora_conclusao or hora_solicitacao
                
                if hora:
                    # Usar função unificada para extrair datetime
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = str(hora)  # fallback
                    else:
                        hora_formatada = str(hora)  # fallback
                        
                # Detectar cidade usando função unificada
                cidade_detectada = extract_city_from_record(rec)
                
                item = {
                    "id_corrida": id_corrida,
                    "usuario_id": usuario_id,
                    "nome": nome,
                    "avatar": gerar_avatar(nome),
                    "hora": hora_formatada,
                    "dt_corrida": dt_corrida,
                    "grupo": rec[4] if len(rec) > 4 else None,  # Telefone do passageiro (antes era rec[9])
                    "local": rec[5] if len(rec) > 5 else None,  # Origem  
                    "destino": rec[6] if len(rec) > 6 else None,  # Destino
                    "telefone": telefone,
                    "cidade": cidade_detectada,
                    "tempo": None
                }
                # Verificar filtro de cidade
                cidade_item = item.get("cidade")
                if cidade and cidade_item != cidade:
                    continue  # Pular se não corresponde ao filtro de cidade
                    
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim:
                    concluidas.append(item)
                    ids_concluidas.add(id_corrida)
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant:
                    concluidas_ant.append(item)
                    ids_concluidas.add(id_corrida)
        # Missed Rides (aceita nomes em português e inglês)
        elif table_name in ["Missed Rides", "corridas_perdidas"]:
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                
                # DEDUPLICAÇÃO: Pular se ID já foi processado
                if id_corrida in ids_perdidas:
                    continue
                    
                # Forçar índice fixo: Missed -> nome em rec[1]
                nome = rec[1] if len(rec) > 1 else None  # passageiro correto
                usuario_id = None
                for idx in (1,2,3):
                    if len(rec) > idx and rec[idx] and str(rec[idx]).isdigit():
                        usuario_id = rec[idx]
                        break
                hora = rec[6] if len(rec) > 6 else None
                motivo = rec[5] if len(rec) > 5 else None  # índice correto para motivo
                dt_corrida = None
                hora_formatada = None
                if hora:
                    # Usar função unificada para extrair datetime
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = str(hora)
                    else:
                        hora_formatada = str(hora)
                item = {
                    "id_corrida": id_corrida,
                    "nome": nome,
                    "avatar": gerar_avatar(nome),
                    "hora": hora_formatada,
                    "dt_corrida": dt_corrida,
                    "grupo": rec[2] if len(rec) > 2 else None,
                    "local": rec[3] if len(rec) > 3 else None,
                    "destino": None,
                    "cidade": rec[8] if len(rec) > 8 else None,  # Cidade no índice 8 para corridas perdidas
                    "tempo": None,
                    "motivo": motivo
                }
                # Verificar filtro de cidade
                cidade_item = item.get("cidade")
                if cidade and cidade_item != cidade:
                    continue  # Pular se não corresponde ao filtro de cidade
                    
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim:
                    perdidas.append(item)
                    ids_perdidas.add(id_corrida)
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant:
                    perdidas_ant.append(item)
                    ids_perdidas.add(id_corrida)
        # Cancelled Rides (aceita nomes em português e inglês)
        elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None

                # DEDUPLICAÇÃO: Pular se ID já foi processado
                if id_corrida in ids_canceladas:
                    continue

                # Forçar índice fixo: Cancelled -> nome em rec[6] (fallback rec[3])
                usuario_id = None
                nome = None
                if len(rec) > 6 and rec[6] and not str(rec[6]).isdigit():
                    nome = rec[6]
                elif len(rec) > 3 and rec[3] and not str(rec[3]).isdigit():
                    nome = rec[3]
                # usuario_id fallback nas posições 1 e 3 (remover uso de índice 2)
                for idx in (1,3):
                    if len(rec) > idx and rec[idx] and str(rec[idx]).isdigit():
                        usuario_id = rec[idx]
                        break

                # Data/hora: preferir índice 12, depois 11, depois 7/8
                hora = None
                for idx in (12, 11, 8, 7):
                    if len(rec) > idx and rec[idx]:
                        hora = rec[idx]
                        break

                # Motivo: 13 (pt) ou 14 (en) ou fallback 12
                motivo = None
                for idx in (13, 14, 12):
                    if len(rec) > idx and rec[idx]:
                        motivo = rec[idx]
                        break

                # Cidade: preferir 8, depois 17, depois 15
                cidade_val = None
                for idx in (8, 17, 15):
                    if len(rec) > idx and rec[idx]:
                        cidade_val = rec[idx]
                        break

                # Detectar se rec[5] é telefone (formatos como +5566...) e mapear corretamente
                telefone = None
                local_val = None
                destino_val = None
                try:
                    maybe_5 = str(rec[5]).strip() if len(rec) > 5 and rec[5] is not None else ""
                except Exception:
                    maybe_5 = ""
                if maybe_5 and re.match(r"^\+?\d{7,}$", maybe_5.replace(' ', '').replace('-', '')):
                    telefone = maybe_5
                    # se rec[5] é telefone, buscar endereço em 8/9/6
                    if len(rec) > 8 and rec[8]:
                        local_val = rec[8]
                        destino_val = rec[9] if len(rec) > 9 and rec[9] else (rec[6] if len(rec) > 6 else None)
                    elif len(rec) > 6 and rec[6]:
                        local_val = rec[6]
                        destino_val = rec[9] if len(rec) > 9 and rec[9] else None
                    else:
                        local_val = None
                        destino_val = None
                else:
                    # padrão: rec[5] é local, rec[6] destino
                    local_val = rec[5] if len(rec) > 5 else None
                    destino_val = rec[6] if len(rec) > 6 else None

                dt_corrida = None
                hora_formatada = None
                if hora:
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = str(hora)
                    else:
                        hora_formatada = str(hora)

                item = {
                    "id_corrida": id_corrida,
                    "usuario_id": usuario_id,
                    "nome": nome,
                    "avatar": gerar_avatar(nome),
                    "hora": hora_formatada,
                    "dt_corrida": dt_corrida,
                    "grupo": rec[5] if len(rec) > 5 else (rec[4] if len(rec) > 4 else None),
                    "local": local_val,
                    "destino": destino_val,
                    "telefone": telefone,
                    "cidade": cidade_val,
                    "tempo": None,
                    "motivo": motivo
                }
                # Verificar filtro de cidade
                cidade_item = item.get("cidade")
                if cidade and cidade_item != cidade:
                    continue  # Pular se não corresponde ao filtro de cidade

                if dt_corrida and dt_ini <= dt_corrida <= dt_fim:
                    canceladas.append(item)
                    ids_canceladas.add(id_corrida)
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant:
                    canceladas_ant.append(item)
                    ids_canceladas.add(id_corrida)
        # Scheduled Rides (aceita nomes em português e inglês)
        elif table_name in ["Scheduled Rides", "corridas_agendadas"]:
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[1] if len(rec) > 1 else None  # passageiro correto
                hora = rec[10] if len(rec) > 10 else None
                dt_corrida = None
                hora_formatada = None
                if hora:
                    # Usar função unificada para extrair datetime
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = str(hora)
                    else:
                        hora_formatada = str(hora)
                item = {
                    "id_corrida": id_corrida,
                    "nome": nome,
                    "avatar": gerar_avatar(nome),
                    "hora": hora_formatada,
                    "dt_corrida": dt_corrida,
                    "grupo": rec[6] if len(rec) > 6 else None,
                    "local": rec[8] if len(rec) > 8 else None,
                    "destino": rec[9] if len(rec) > 9 else None,
                    "cidade": rec[17] if len(rec) > 17 else None,  # Cidade no índice 17 para corridas canceladas
                    "tempo": None
                }
                # Verificar filtro de cidade
                cidade_item = item.get("cidade")
                if cidade and cidade_item != cidade:
                    continue  # Pular se não corresponde ao filtro de cidade
                    
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas_ant.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))

    concluidas = ordenar_por_data(concluidas)
    canceladas = ordenar_por_data(canceladas)
    perdidas = ordenar_por_data(perdidas)

    def calc_variacao(atual, anterior):
        if anterior == 0:
            return 100.0 if atual > 0 else 0.0
        return round(((atual - anterior) / anterior) * 100, 2)

    atividade_recente = {
        "concluidas": concluidas[:3],
        "canceladas": canceladas[:3],
        "perdidas": perdidas[:3]
    }

    metricas_principais = {
        "corridas_concluidas": len(concluidas),
        "corridas_canceladas": len(canceladas),
        "corridas_perdidas": len(perdidas),
        "variacao_concluidas": calc_variacao(len(concluidas), len(concluidas_ant)),
        "variacao_canceladas": calc_variacao(len(canceladas), len(canceladas_ant)),
        "variacao_perdidas": calc_variacao(len(perdidas), len(perdidas_ant)),
    }

    # --- NOVAS AGREGAÇÕES PARA DASHBOARD ---
    from collections import Counter, defaultdict
    # Evolução temporal (por dia)
    evolucao = defaultdict(lambda: {"concluidas":0, "canceladas":0, "perdidas":0})
    for item in concluidas:
        if item["dt_corrida"]:
            dia = item["dt_corrida"].date().isoformat()
            evolucao[dia]["concluidas"] += 1
    for item in canceladas:
        if item["dt_corrida"]:
            dia = item["dt_corrida"].date().isoformat()
            evolucao[dia]["canceladas"] += 1
    for item in perdidas:
        if item["dt_corrida"]:
            dia = item["dt_corrida"].date().isoformat()
            evolucao[dia]["perdidas"] += 1
    evolucao_list = []
    for dia in sorted(evolucao.keys()):
        total = evolucao[dia]["concluidas"] + evolucao[dia]["canceladas"] + evolucao[dia]["perdidas"]
        evolucao_list.append({
            "data": dia,
            "concluidas": evolucao[dia]["concluidas"],
            "canceladas": evolucao[dia]["canceladas"],
            "perdidas": evolucao[dia]["perdidas"],
            "taxa_conclusao": (evolucao[dia]["concluidas"] / total * 100) if total else 0,
            "taxa_cancelamento": (evolucao[dia]["canceladas"] / total * 100) if total else 0,
            "taxa_perda": (evolucao[dia]["perdidas"] / total * 100) if total else 0
        })

    # Distribuição de status
    distribuicao_status = [
        {"status": "concluida", "quantidade": len(concluidas)},
        {"status": "cancelada", "quantidade": len(canceladas)},
        {"status": "perdida", "quantidade": len(perdidas)}
    ]

    # Motivos de cancelamento/perda
    motivos_cancelamento = Counter([c.get("motivo") for c in canceladas if c.get("motivo")])
    motivos_perda = Counter([p.get("motivo") for p in perdidas if p.get("motivo")])
    motivos_cancelamento_list = [{"motivo": k, "quantidade": v} for k, v in motivos_cancelamento.items()]
    motivos_perda_list = [{"motivo": k, "quantidade": v} for k, v in motivos_perda.items()]

    # Comparativo por cidade
    cidades = set()
    for c in concluidas+canceladas+perdidas:
        if c.get("cidade"): cidades.add(c["cidade"])
    comparativo_cidades = []
    for cidade in cidades:
        concl = [c for c in concluidas if c.get("cidade") == cidade]
        canc = [c for c in canceladas if c.get("cidade") == cidade]
        perd = [c for c in perdidas if c.get("cidade") == cidade]
        total = len(concl) + len(canc) + len(perd)
        comparativo_cidades.append({
            "cidade": cidade,
            "concluidas": len(concl),
            "canceladas": len(canc),
            "perdidas": len(perd),
            "taxa_conclusao": (len(concl)/total*100) if total else 0,
            "taxa_cancelamento": (len(canc)/total*100) if total else 0,
            "taxa_perda": (len(perd)/total*100) if total else 0
        })

    # Comparativo por categoria (grupo)
    categorias = set()
    for c in concluidas+canceladas+perdidas:
        if c.get("grupo"): categorias.add(c["grupo"])
    comparativo_categorias = []
    for cat in categorias:
        concl = [c for c in concluidas if c.get("grupo") == cat]
        canc = [c for c in canceladas if c.get("grupo") == cat]
        perd = [c for c in perdidas if c.get("grupo") == cat]
        total = len(concl) + len(canc) + len(perd)
        comparativo_categorias.append({
            "categoria": cat,
            "concluidas": len(concl),
            "canceladas": len(canc),
            "perdidas": len(perd),
            "taxa_conclusao": (len(concl)/total*100) if total else 0,
            "taxa_cancelamento": (len(canc)/total*100) if total else 0,
            "taxa_perda": (len(perd)/total*100) if total else 0
        })

    # Comparativo por horário (hora do dia)
    horarios = defaultdict(lambda: {"concluidas":0, "canceladas":0, "perdidas":0})
    for c in concluidas:
        if c["dt_corrida"]:
            h = c["dt_corrida"].strftime("%H")
            horarios[h]["concluidas"] += 1
    for c in canceladas:
        if c["dt_corrida"]:
            h = c["dt_corrida"].strftime("%H")
            horarios[h]["canceladas"] += 1
    for c in perdidas:
        if c["dt_corrida"]:
            h = c["dt_corrida"].strftime("%H")
            horarios[h]["perdidas"] += 1
    comparativo_horarios = []
    for h in sorted(horarios.keys()):
        total = horarios[h]["concluidas"] + horarios[h]["canceladas"] + horarios[h]["perdidas"]
        comparativo_horarios.append({
            "hora": h,
            "concluidas": horarios[h]["concluidas"],
            "canceladas": horarios[h]["canceladas"],
            "perdidas": horarios[h]["perdidas"],
            "taxa_conclusao": (horarios[h]["concluidas"]/total*100) if total else 0,
            "taxa_cancelamento": (horarios[h]["canceladas"]/total*100) if total else 0,
            "taxa_perda": (horarios[h]["perdidas"]/total*100) if total else 0
        })

    # Tempos operacionais (placeholders, pois não há campo tempo)
    tempos_operacionais = {
        "tempo_medio_espera": None,
        "tempo_medio_chegada": None
    }

    # Filtros disponíveis
    filtros_disponiveis = {
        "cidades": sorted(list(cidades)),
        "categorias": sorted([str(cat) for cat in categorias])  # Converter para string antes de ordenar
    }

    return {
        "metricas_principais": metricas_principais,
        "evolucao": evolucao_list,
        "distribuicao_status": distribuicao_status,
        "motivos_cancelamento": motivos_cancelamento_list,
        "motivos_perda": motivos_perda_list,
        "comparativo_cidades": comparativo_cidades,
        "comparativo_categorias": comparativo_categorias,
        "comparativo_horarios": comparativo_horarios,
        "tempos_operacionais": tempos_operacionais,
        "filtros_disponiveis": filtros_disponiveis,
        "atividade_recente": atividade_recente
    }
