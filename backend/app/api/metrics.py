from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from typing import Optional

import json
from datetime import datetime, timedelta
from collections import defaultdict
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.city_service import get_cities_from_rides_data, normalize_city_name, extract_city_from_address

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

def matches_city_filter(cidade_item, cidade_filter):
    """Compara cidade de forma robusta, lidando com None e diferenças de formatação"""
    if not cidade_filter:
        return True  # Sem filtro, aceitar tudo

    if not cidade_item:
        return False  # Item sem cidade não corresponde a filtro

    # Aplicar normalização completa a ambas as strings
    item_norm = normalize_city_name(str(cidade_item).strip())
    filter_norm = normalize_city_name(str(cidade_filter).strip())

    # Se a normalização falhar, usar o valor original em maiúsculo
    if not item_norm:
        item_norm = str(cidade_item).strip().upper()
    if not filter_norm:
        filter_norm = str(cidade_filter).strip().upper()

    return item_norm == filter_norm

def extract_city_from_record(rec):
    """Extrai cidade de um registro de forma robusta"""
    try:
        # Tentar diferentes índices onde a cidade pode estar
        for idx in (17, 16, 15, 14, 13):
            if len(rec) > idx and rec[idx]:
                cidade = str(rec[idx]).strip()
                if cidade and cidade not in ["", "null", "None"]:
                    return extract_city_from_address(cidade)
        return None
    except Exception:
        return None
        item_norm = str(cidade_item).strip().upper()
    if not filter_norm:
        filter_norm = str(cidade_filter).strip().upper()

    return item_norm == filter_norm

def extract_city_from_record(rec):
    """Detecta cidade baseada nos dados do registro usando normalização completa"""
    if not rec or len(rec) == 0:
        return "Unnamed"

    # Detectar tipo de corrida baseado na estrutura dos dados
    rec_length = len(rec)

    # Cancelled Rides: geralmente têm 18 campos, cidade no índice 17 (último) ou 7 (endereço)
    if rec_length >= 18:
        # Tentar primeiro o último campo (índice 17 para 18 campos)
        if rec_length > 17 and rec[17]:
            city_str = str(rec[17]).strip()
            normalized_city = normalize_city_name(city_str)
            if normalized_city:
                return normalized_city
            extracted_city = extract_city_from_address(city_str)
            if extracted_city:
                return extracted_city

        # Tentar endereço no índice 7
        if len(rec) > 7 and rec[7]:
            city_str = str(rec[7]).strip()
            normalized_city = normalize_city_name(city_str)
            if normalized_city:
                return normalized_city
            extracted_city = extract_city_from_address(city_str)
            if extracted_city:
                return extracted_city

    # Missed Rides: geralmente têm 8-9 campos, cidade no índice 8 (último) ou 3 (endereço)
    elif rec_length >= 8 and rec_length <= 10:
        # Tentar primeiro o último campo
        last_idx = len(rec) - 1
        if rec[last_idx]:
            city_str = str(rec[last_idx]).strip()
            normalized_city = normalize_city_name(city_str)
            if normalized_city:
                return normalized_city
            extracted_city = extract_city_from_address(city_str)
            if extracted_city:
                return extracted_city

        # Tentar endereço no índice 3
        if len(rec) > 3 and rec[3]:
            city_str = str(rec[3]).strip()
            normalized_city = normalize_city_name(city_str)
            if normalized_city:
                return normalized_city
            extracted_city = extract_city_from_address(city_str)
            if extracted_city:
                return extracted_city

    # Completed Rides e outros: usar índices tradicionais
    else:
        # Priorizar índices onde as cidades realmente aparecem nos dados atuais
        possible_city_indices = [5, 6, 15, 17, 8, 9, 10]  # Reordenado por prioridade baseada nos dados

        for idx in possible_city_indices:
            if idx < len(rec) and rec[idx]:
                city_str = str(rec[idx]).strip()

                # Primeiro tentar normalização direta
                normalized_city = normalize_city_name(city_str)
                if normalized_city:
                    return normalized_city

                # Se não conseguiu normalizar diretamente, tentar extrair de endereço
                extracted_city = extract_city_from_address(city_str)
                if extracted_city:
                    return extracted_city

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

def ordenar_por_data(lista):
    return sorted(lista, key=lambda x: x.get("dt_corrida", datetime.min), reverse=True)

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
                if not matches_city_filter(cidade_item, cidade):
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
                    "cidade": (extract_city_from_address(rec[3]) if len(rec) > 3 and rec[3] else None) if len(rec) > 3 and rec[3] else (normalize_city_name(str(rec[8]).strip()) if len(rec) > 8 and rec[8] else None),  # Extrair do endereço ou índice 8
                    "tempo": None,
                    "motivo": motivo
                }
                # Verificar filtro de cidade
                cidade_item = item.get("cidade")
                if not matches_city_filter(cidade_item, cidade):
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

                # Cidade: primeiro tentar extrair dos endereços, depois índices específicos
                cidade_val = None

                # Tentar extrair cidade do endereço de origem
                if local_val:
                    try:
                        extracted = extract_city_from_address(local_val)
                        if extracted:
                            cidade_val = normalize_city_name(extracted)
                    except Exception:
                        pass  # Silenciar erros na extração

                # Se não conseguiu do endereço, tentar índices específicos
                if not cidade_val:
                    for idx in (8, 17, 15):
                        if len(rec) > idx and rec[idx]:
                            cidade_val = rec[idx]
                            break

                    # Aplicar normalização à cidade detectada dos índices
                    if cidade_val:
                        cidade_val = normalize_city_name(str(cidade_val).strip())

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
                if not matches_city_filter(cidade_item, cidade):
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
                if not matches_city_filter(cidade_item, cidade):
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
        "concluidas": concluidas,
        "canceladas": canceladas,
        "perdidas": perdidas,
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

def get_periodo_key(dt_corrida, periodo):
    """Retorna a chave de agrupamento baseada no período selecionado"""
    if not dt_corrida:
        return None

    if periodo == "hoje":
        # Agrupar por hora: "08:00", "09:00", etc.
        return dt_corrida.strftime("%H:00")
    elif periodo in ["7d", "30d"]:
        # Agrupar por data: "2024-01-15"
        return dt_corrida.date().isoformat()
    elif periodo in ["3m", "6m", "12m"]:
        # Agrupar por semana: "2024-01-15" (segunda-feira da semana)
        # Calcular o início da semana (segunda-feira)
        days_since_monday = dt_corrida.weekday()  # 0=segunda, 6=domingo
        monday = dt_corrida - timedelta(days=days_since_monday)
        return monday.date().isoformat()
    return None

@router.get("/overview-by-period")
async def get_metrics_overview_by_period(
    db: AsyncSession = Depends(get_db),
    periodo: str = Query("30d", enum=["hoje", "7d", "30d", "3m", "6m", "12m"], description="Período do filtro: hoje, 7d, 30d, 3m, 6m, 12m"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade específica")
):
    """Endpoint para dados agrupados por período (hora/dia/semana) para gráficos por período"""

    # Buscar todos os registros da tabela rides_data
    result = await db.execute(select(RidesData))
    rides = result.scalars().all()

    # Inicializar contadores por período
    periodos_data = {}

    # Definir datas de filtro
    now = datetime.now()
    if periodo == "hoje":
        dt_ini = now.replace(hour=0, minute=0, second=0, microsecond=0)
        dt_fim = now
    elif periodo == "7d":
        dt_ini = now - timedelta(days=7)
        dt_fim = now
    elif periodo == "30d":
        dt_ini = now - timedelta(days=30)
        dt_fim = now
    elif periodo == "3m":
        dt_ini = now - timedelta(days=90)
        dt_fim = now
    elif periodo == "6m":
        dt_ini = now - timedelta(days=180)
        dt_fim = now
    else:  # "12m"
        dt_ini = now - timedelta(days=365)
        dt_fim = now

    # Processar os dados
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
                # Extrair data/hora
                dt_corrida = None
                if r.source == "monitoring-service-adapted":
                    # Dados do scraper
                    hora = rec[8] if len(rec) > 8 else rec[7] if len(rec) > 7 else None
                else:
                    # Dados do Excel
                    hora = rec[7] if len(rec) > 7 else rec[6] if len(rec) > 6 else None

                if hora:
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            continue

                if not dt_corrida or not (dt_ini <= dt_corrida <= dt_fim):
                    continue

                # Verificar filtro de cidade
                cidade_detectada = extract_city_from_record(rec)
                if not matches_city_filter(cidade_detectada, cidade):
                    continue

                # Agrupar por período
                periodo_key = get_periodo_key(dt_corrida, periodo)
                if periodo_key:
                    if periodo_key not in periodos_data:
                        periodos_data[periodo_key] = {"concluidas": 0, "canceladas": 0, "perdidas": 0}
                    periodos_data[periodo_key]["concluidas"] += 1

        # Processar corridas canceladas
        elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
            for rec in new_records:
                dt_corrida = None  # Inicializar variável
                
                # Extrair data/hora
                hora = None
                for idx in (12, 11, 8, 7):
                    if len(rec) > idx and rec[idx]:
                        hora = rec[idx]
                        break

                if hora:
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            continue

                if not dt_corrida or not (dt_ini <= dt_corrida <= dt_fim):
                    continue

                # Verificar filtro de cidade
                cidade_detectada = extract_city_from_record(rec)
                if not matches_city_filter(cidade_detectada, cidade):
                    continue

                # Agrupar por período
                periodo_key = get_periodo_key(dt_corrida, periodo)
                if periodo_key:
                    if periodo_key not in periodos_data:
                        periodos_data[periodo_key] = {"concluidas": 0, "canceladas": 0, "perdidas": 0}
                    periodos_data[periodo_key]["canceladas"] += 1

        # Processar corridas perdidas
        elif table_name in ["Missed Rides", "corridas_perdidas"]:
            for rec in new_records:
                dt_corrida = None  # Inicializar variável
                
                # Extrair data/hora
                hora = rec[6] if len(rec) > 6 else None

                if hora:
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            continue

                if not dt_corrida or not (dt_ini <= dt_corrida <= dt_fim):
                    continue

                # Verificar filtro de cidade
                cidade_detectada = extract_city_from_record(rec)
                if not matches_city_filter(cidade_detectada, cidade):
                    continue

                # Agrupar por período
                periodo_key = get_periodo_key(dt_corrida, periodo)
                if periodo_key:
                    if periodo_key not in periodos_data:
                        periodos_data[periodo_key] = {"concluidas": 0, "canceladas": 0, "perdidas": 0}
                    periodos_data[periodo_key]["perdidas"] += 1

    # Converter para lista ordenada
    comparativo_periodos = []
    for periodo_key in sorted(periodos_data.keys()):
        data = periodos_data[periodo_key]
        total = data["concluidas"] + data["canceladas"] + data["perdidas"]

        comparativo_periodos.append({
            "periodo": periodo_key,
            "concluidas": data["concluidas"],
            "canceladas": data["canceladas"],
            "perdidas": data["perdidas"],
            "taxa_conclusao": (data["concluidas"] / total * 100) if total > 0 else 0,
            "taxa_cancelamento": (data["canceladas"] / total * 100) if total > 0 else 0,
            "taxa_perda": (data["perdidas"] / total * 100) if total > 0 else 0
        })

    # Calcular totais
    total_concluidas = sum(p["concluidas"] for p in comparativo_periodos)
    total_canceladas = sum(p["canceladas"] for p in comparativo_periodos)
    total_perdidas = sum(p["perdidas"] for p in comparativo_periodos)

    return {
        "comparativo_periodos": comparativo_periodos,
        "total_concluidas": total_concluidas,
        "total_canceladas": total_canceladas,
        "total_perdidas": total_perdidas,
        "periodo_filtro": periodo,
        "cidade_filtro": cidade
    }

@router.get("/debug-missed-sample")
async def debug_missed_sample(db: AsyncSession = Depends(get_db)):
    """Debug endpoint para ver exemplos de corridas perdidas"""
    try:
        result = await db.execute(select(RidesData))
        rides = result.scalars().all()
        
        missed_samples = []
        
        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            if table_name == "Missed Rides":
                new_records = ride_data.get("newRecords", [])
                for idx, rec in enumerate(new_records[:3]):  # primeiros 3
                    sample = {
                        "source": r.source,
                        "record_index": idx,
                        "record_length": len(rec),
                        "campos": {}
                    }
                    
                    for i, campo in enumerate(rec):
                        sample["campos"][f"campo_{i}"] = str(campo)[:100]  # limitar tamanho
                        # Tentar extrair data de cada campo
                        try:
                            dt_str = extract_datetime_from_record([campo], 0)
                            if dt_str:
                                sample["campos"][f"campo_{i}_parsed"] = dt_str
                        except:
                            pass
                    
                    missed_samples.append(sample)
                    
                if len(missed_samples) >= 5:  # limitar a 5 exemplos
                    break
        
        return {"missed_samples": missed_samples}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro interno: {str(e)}"}
        )

@router.get("/debug-cancelled-sample")
async def debug_cancelled_sample(db: AsyncSession = Depends(get_db)):
    """Debug endpoint para ver exemplos de corridas canceladas"""
    try:
        result = await db.execute(select(RidesData))
        rides = result.scalars().all()
        
        cancelled_samples = []
        
        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            if table_name == "Cancelled Rides":
                new_records = ride_data.get("newRecords", [])
                for idx, rec in enumerate(new_records[:3]):  # primeiros 3
                    # Verificar todos os campos que podem conter data/hora
                    sample = {
                        "source": r.source,
                        "record_index": idx,
                        "record_length": len(rec),
                        "campos": {}
                    }
                    
                    for i, campo in enumerate(rec):
                        sample["campos"][f"campo_{i}"] = str(campo)[:100]  # limitar tamanho
                        # Tentar extrair data de cada campo
                        try:
                            dt_str = extract_datetime_from_record([campo], 0)
                            if dt_str:
                                sample["campos"][f"campo_{i}_parsed"] = dt_str
                        except:
                            pass
                    
                    cancelled_samples.append(sample)
                    
                if len(cancelled_samples) >= 5:  # limitar a 5 exemplos
                    break
        
        return {"cancelled_samples": cancelled_samples}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro interno: {str(e)}"}
        )

@router.get("/debug-date")
async def debug_date(
    db: AsyncSession = Depends(get_db),
    data_especifica: str = Query(..., description="Data específica no formato YYYY-MM-DD")
):
    """Debug endpoint para ver dados de uma data específica"""
    try:
        result = await db.execute(select(RidesData))
        rides = result.scalars().all()
        
        # Converter string de data para datetime range
        data_obj = datetime.strptime(data_especifica, "%Y-%m-%d")
        dt_ini = data_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        dt_fim = data_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        debug_info = {
            "data_procurada": data_especifica,
            "range_inicio": dt_ini.isoformat(),
            "range_fim": dt_fim.isoformat(),
            "tables_encontradas": {},
            "registros_processados": 0,
            "registros_na_data": 0
        }
        
        for r in rides:
            debug_info["registros_processados"] += 1
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            
            if table_name not in debug_info["tables_encontradas"]:
                debug_info["tables_encontradas"][table_name] = {
                    "total_records": 0,
                    "records_na_data": 0,
                    "exemplo_record": None
                }
            
            debug_info["tables_encontradas"][table_name]["total_records"] += len(new_records)
            
            for rec in new_records:
                # Para corridas concluídas
                if table_name == "Completed Rides":
                    hora_solicitacao = None
                    hora_conclusao = None
                    
                    if r.source == "monitoring-service-adapted":
                        hora_solicitacao = rec[7] if len(rec) > 7 else None
                        hora_conclusao = rec[8] if len(rec) > 8 else None
                    else:
                        hora_solicitacao = rec[6] if len(rec) > 6 else None
                        hora_conclusao = rec[7] if len(rec) > 7 else None
                    
                    hora = hora_conclusao or hora_solicitacao
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                if dt_ini <= dt_corrida <= dt_fim:
                                    debug_info["tables_encontradas"][table_name]["records_na_data"] += 1
                                    debug_info["registros_na_data"] += 1
                                    if not debug_info["tables_encontradas"][table_name]["exemplo_record"]:
                                        debug_info["tables_encontradas"][table_name]["exemplo_record"] = {
                                            "record": rec[:5],  # primeiros 5 campos
                                            "hora_extraida": dt_str,
                                            "source": r.source
                                        }
                            except Exception:
                                pass
                                
                # Para corridas canceladas
                elif table_name == "Cancelled Rides":
                    hora = rec[6] if len(rec) > 6 else None
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                if dt_ini <= dt_corrida <= dt_fim:
                                    debug_info["tables_encontradas"][table_name]["records_na_data"] += 1
                                    debug_info["registros_na_data"] += 1
                                    if not debug_info["tables_encontradas"][table_name]["exemplo_record"]:
                                        debug_info["tables_encontradas"][table_name]["exemplo_record"] = {
                                            "record": rec[:7],  # primeiros 7 campos
                                            "hora_extraida": dt_str,
                                            "source": r.source
                                        }
                            except Exception:
                                pass
                                
                # Para corridas perdidas
                elif table_name == "Missed Rides":
                    hora = rec[4] if len(rec) > 4 else None
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                if dt_ini <= dt_corrida <= dt_fim:
                                    debug_info["tables_encontradas"][table_name]["records_na_data"] += 1
                                    debug_info["registros_na_data"] += 1
                                    if not debug_info["tables_encontradas"][table_name]["exemplo_record"]:
                                        debug_info["tables_encontradas"][table_name]["exemplo_record"] = {
                                            "record": rec[:5],  # primeiros 5 campos
                                            "hora_extraida": dt_str,
                                            "source": r.source
                                        }
                            except Exception:
                                pass
        
        return debug_info
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro interno: {str(e)}"}
        )

@router.get("/debug-tables")
async def debug_tables(db: AsyncSession = Depends(get_db)):
    """Debug endpoint para verificar tableNames"""
    try:
        result = await db.execute(select(RidesData))
        rides = result.scalars().all()
        
        table_names = set()
        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            if table_name:
                table_names.add(table_name)
        
        return {"table_names": list(table_names)}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro interno: {str(e)}"}
        )

@router.get("/daily-detail")
async def get_daily_detail(
    db: AsyncSession = Depends(get_db),
    data_especifica: str = Query(..., description="Data específica no formato YYYY-MM-DD"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade específica")
):
    """
    Retorna dados de uma data específica detalhados por hora
    
    Args:
        data_especifica: Data no formato YYYY-MM-DD (ex: 2025-09-15)
        cidade: Cidade para filtrar (opcional)
        
    Returns:
        {
            "data": "2025-09-15",
            "total_dia": {"concluidas": 13, "canceladas": 7, "perdidas": 18},
            "horarios": [
                {"hora": "15", "concluidas": 6, "canceladas": 1, "perdidas": 3},
                ...
            ]
        }
    """
    try:
        # Buscar todos os registros
        result = await db.execute(select(RidesData))
        rides = result.scalars().all()

        # Converter string de data para datetime range
        try:
            data_obj = datetime.strptime(data_especifica, "%Y-%m-%d")
            dt_ini = data_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            dt_fim = data_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "Data inválida. Use formato YYYY-MM-DD"}
            )

        concluidas, canceladas, perdidas = [], [], []
        
        # Processar dados (mesma lógica do endpoint overview, mas filtrado por data)
        ids_concluidas = set()
        ids_canceladas = set()
        ids_perdidas = set()
        
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
                    id_corrida = rec[0] if len(rec) > 0 else None
                    if id_corrida in ids_concluidas:
                        continue
                        
                    # Extrair data/hora
                    hora_solicitacao = None
                    hora_conclusao = None
                    
                    if r.source == "monitoring-service-adapted":
                        hora_solicitacao = rec[7] if len(rec) > 7 else None
                        hora_conclusao = rec[8] if len(rec) > 8 else None
                    else:
                        hora_solicitacao = rec[6] if len(rec) > 6 else None
                        hora_conclusao = rec[7] if len(rec) > 7 else None
                    
                    hora = hora_conclusao or hora_solicitacao
                    dt_corrida = None
                    
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                continue
                                
                    if not dt_corrida:
                        continue
                        
                    # Detectar cidade
                    cidade_detectada = extract_city_from_record(rec)
                    if not matches_city_filter(cidade_detectada, cidade):
                        continue
                        
                    # Verificar se a corrida está na data específica
                    if dt_ini <= dt_corrida <= dt_fim:
                        concluidas.append({"dt_corrida": dt_corrida})
                        ids_concluidas.add(id_corrida)
                        
            # Processar corridas canceladas
            elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                for rec in new_records:
                    id_corrida = rec[0] if len(rec) > 0 else None
                    if id_corrida in ids_canceladas:
                        continue
                        
                    # Extrair data/hora - índices corretos para canceladas
                    hora = None
                    if r.source == "import_excel":
                        # Para import_excel, data está no campo 11
                        hora = rec[11] if len(rec) > 11 else None
                    elif r.source == "monitoring-service-adapted":
                        # Para monitoring-service-adapted, data está no campo 12
                        hora = rec[12] if len(rec) > 12 else None
                    
                    dt_corrida = None
                    
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                continue
                                
                    if not dt_corrida:
                        continue
                        
                    # Detectar cidade
                    cidade_detectada = extract_city_from_record(rec)
                    if not matches_city_filter(cidade_detectada, cidade):
                        continue
                        
                    if dt_ini <= dt_corrida <= dt_fim:
                        canceladas.append({"dt_corrida": dt_corrida})
                        ids_canceladas.add(id_corrida)
                        
            # Processar corridas perdidas
            elif table_name in ["Missed Rides", "corridas_perdidas"]:
                for rec in new_records:
                    id_corrida = rec[0] if len(rec) > 0 else None
                    if id_corrida in ids_perdidas:
                        continue
                        
                    # Extrair data/hora - campo 6 para perdidas (tanto import_excel quanto monitoring-service-adapted)
                    hora = rec[6] if len(rec) > 6 else None
                    dt_corrida = None
                    
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                continue
                                
                    if not dt_corrida:
                        continue
                        
                    # Detectar cidade
                    cidade_detectada = extract_city_from_record(rec)
                    if not matches_city_filter(cidade_detectada, cidade):
                        continue
                        
                    if dt_ini <= dt_corrida <= dt_fim:
                        perdidas.append({"dt_corrida": dt_corrida})
                        ids_perdidas.add(id_corrida)

        # Agrupar por hora
        horarios = defaultdict(lambda: {"concluidas": 0, "canceladas": 0, "perdidas": 0})
        
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

        # Construir resposta
        horarios_list = []
        total_concluidas = len(concluidas)
        total_canceladas = len(canceladas)
        total_perdidas = len(perdidas)
        
        # Incluir todas as horas de 00-23 (mesmo que sejam 0)
        for h in range(24):
            h_str = f"{h:02d}"
            concluidas_h = horarios[h_str]["concluidas"]
            canceladas_h = horarios[h_str]["canceladas"] 
            perdidas_h = horarios[h_str]["perdidas"]
            total_h = concluidas_h + canceladas_h + perdidas_h
            
            if total_h > 0:  # Só incluir horas com dados
                horarios_list.append({
                    "hora": h_str,
                    "concluidas": concluidas_h,
                    "canceladas": canceladas_h,
                    "perdidas": perdidas_h,
                    "total": total_h,
                    "taxa_conclusao": (concluidas_h / total_h * 100) if total_h > 0 else 0,
                    "taxa_cancelamento": (canceladas_h / total_h * 100) if total_h > 0 else 0,
                    "taxa_perda": (perdidas_h / total_h * 100) if total_h > 0 else 0
                })

        return {
            "data": data_especifica,
            "total_dia": {
                "concluidas": total_concluidas,
                "canceladas": total_canceladas,
                "perdidas": total_perdidas,
                "total": total_concluidas + total_canceladas + total_perdidas
            },
            "horarios": horarios_list,
            "cidade_filtro": cidade
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro interno: {str(e)}"}
        )

@router.get("/comparative")
async def get_comparative_data(
    db: AsyncSession = Depends(get_db),
    periodo: str = Query("6", description="Período em meses (ex: 6 para últimos 6 meses)"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade específica")
):
    """
    � ENDPOINT PARA GRÁFICO COMPARATIVO DIA POR DIA POR MÊS
    Retorna dados estruturados: 
    - X-axis: Dias do mês (1-31)
    - Y-axis: Quantidade de corridas
    - Múltiplas linhas: Uma linha para cada mês com cor diferente
    """
    try:
        # Buscar todos os registros
        result = await db.execute(select(RidesData))
        rides = result.scalars().all()
        
        # Definir período de análise (últimos N meses)
        now = datetime.now()
        periodo_meses = int(periodo)
        
        # Calcular meses para análise
        meses_analise = []
        for i in range(periodo_meses):
            mes_data = now.replace(day=1) - timedelta(days=i*30)
            mes_str = mes_data.strftime("%Y-%m")
            meses_analise.insert(0, mes_str)  # Inserir no início para ordem cronológica
        
        # Estrutura de dados: [mês][dia] = {concluidas, canceladas, perdidas}
        # Dias 1-31 para cada mês
        data_por_mes = {}
        for mes in meses_analise:
            data_por_mes[mes] = {}
            for dia in range(1, 32):  # Dias 1 a 31
                data_por_mes[mes][dia] = {
                    "concluidas": 0,
                    "canceladas": 0, 
                    "perdidas": 0,
                    "total": 0
                }
        
        # Controle de duplicatas - usar apenas o ID único da corrida
        corridas_processadas = set()
        
        # Processar todos os registros de corridas
        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            source = r.source
            
            # Processar corridas concluídas
            if table_name in ["Completed Rides", "corridas_concluidas", "rides_data"]:
                for rec in new_records:
                    # ID da corrida sempre está no índice [0] em ambas as fontes
                    ride_id = rec[0] if len(rec) > 0 else None
                    if not ride_id:
                        continue
                    
                    # Normalizar ID para string para comparação
                    ride_id_str = str(ride_id)
                    
                    # Verificar se já processamos esta corrida
                    if ride_id_str in corridas_processadas:
                        continue  # Pular duplicata
                    
                    # Extrair data e status baseado na fonte
                    if source == "import_excel":
                        hora = rec[6] if len(rec) > 6 else None
                        status = rec[9] if len(rec) > 9 else None
                    else:  # monitoring-service-adapted
                        hora = rec[7] if len(rec) > 7 else None
                        status = rec[10] if len(rec) > 10 else None
                        
                    # Verificar se é realmente concluída
                    if status and "Concluído" not in str(status) and "Completed" not in str(status):
                        continue
                    
                    # Marcar como processada
                    corridas_processadas.add(ride_id_str)
                        
                    # Extrair e validar data
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                mes_corrida = dt_corrida.strftime("%Y-%m")
                                dia_corrida = dt_corrida.day
                                
                                # Verificar se está no período de análise
                                if mes_corrida in data_por_mes:
                                    data_por_mes[mes_corrida][dia_corrida]["concluidas"] += 1
                                        
                            except Exception:
                                continue
            
            # Processar corridas canceladas
            elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                for rec in new_records:
                    # ID da corrida sempre está no índice [0] em ambas as fontes
                    ride_id = rec[0] if len(rec) > 0 else None
                    if not ride_id:
                        continue
                    
                    # Normalizar ID para string para comparação
                    ride_id_str = str(ride_id)
                    
                    # Verificar se já processamos esta corrida
                    if ride_id_str in corridas_processadas:
                        continue  # Pular duplicata
                    
                    # Extrair data e status baseado na fonte
                    if source == "import_excel":
                        hora = rec[11] if len(rec) > 11 else None
                        status = rec[13] if len(rec) > 13 else None
                    else:  # monitoring-service-adapted
                        hora = rec[12] if len(rec) > 12 else None
                        status = rec[14] if len(rec) > 14 else None
                    
                    # Verificar se é realmente cancelada
                    if status and "Cancel" not in str(status) and "cancel" not in str(status):
                        continue
                    
                    # Marcar como processada
                    corridas_processadas.add(ride_id_str)
                            
                    # Extrair e validar data
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                mes_corrida = dt_corrida.strftime("%Y-%m")
                                dia_corrida = dt_corrida.day
                                
                                # Verificar se está no período de análise
                                if mes_corrida in data_por_mes:
                                    data_por_mes[mes_corrida][dia_corrida]["canceladas"] += 1
                                        
                            except Exception:
                                continue
            
            # Processar corridas perdidas/missed
            elif table_name in ["Missed Rides", "corridas_perdidas", "Scheduled Rides", "corridas_agendadas"]:
                for rec in new_records:
                    # ID da corrida sempre está no índice [0] em ambas as fontes
                    ride_id = rec[0] if len(rec) > 0 else None
                    if not ride_id:
                        continue
                    
                    # Normalizar ID para string para comparação
                    ride_id_str = str(ride_id)
                    
                    # Verificar se já processamos esta corrida
                    if ride_id_str in corridas_processadas:
                        continue  # Pular duplicata
                    
                    # Extrair data e status baseado na fonte
                    if source == "import_excel":
                        hora = rec[6] if len(rec) > 6 else None
                        status = rec[5] if len(rec) > 5 else None
                    else:  # monitoring-service-adapted
                        if table_name in ["Scheduled Rides", "corridas_agendadas"]:
                            hora = rec[10] if len(rec) > 10 else None
                            status = rec[14] if len(rec) > 14 else None
                        else:
                            hora = rec[6] if len(rec) > 6 else None
                            status = rec[5] if len(rec) > 5 else None
                    
                    # Verificar se é realmente perdida/missed/timeout
                    if status and not any(word in str(status) for word in ["Timeout", "Missed", "Process", "perdida"]):
                        continue
                    
                    # Marcar como processada
                    corridas_processadas.add(ride_id_str)
                        
                    # Extrair e validar data
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                mes_corrida = dt_corrida.strftime("%Y-%m")
                                dia_corrida = dt_corrida.day
                                
                                # Verificar se está no período de análise
                                if mes_corrida in data_por_mes:
                                    data_por_mes[mes_corrida][dia_corrida]["perdidas"] += 1
                                        
                            except Exception:
                                continue
        
        # CALCULAR TOTAL CORRETAMENTE (apenas uma vez por dia/mês)
        for mes in data_por_mes:
            for dia in data_por_mes[mes]:
                # Total = concluídas + canceladas + perdidas (cada corrida conta só uma vez)
                data_por_mes[mes][dia]["total"] = (
                    data_por_mes[mes][dia]["concluidas"] + 
                    data_por_mes[mes][dia]["canceladas"] + 
                    data_por_mes[mes][dia]["perdidas"]
                )
        
        # Estruturar resposta para o gráfico comparativo
        # X-axis: Dias 1-31
        # Multiple lines: Uma linha para cada mês
        
        daily_data = []
        for dia in range(1, 32):  # Dias 1 a 31
            dia_entry = {
                "day": dia,  # Para X-axis do gráfico
            }
            
            # Adicionar dados de cada mês como linhas separadas
            for mes in meses_analise:
                mes_nome = datetime.strptime(f"{mes}-01", "%Y-%m-%d").strftime("%b %Y")
                mes_key = mes.replace("-", "_")  # 2025-04 -> 2025_04
                
                dia_entry[f"{mes_key}_concluidas"] = data_por_mes[mes][dia]["concluidas"]
                dia_entry[f"{mes_key}_canceladas"] = data_por_mes[mes][dia]["canceladas"] 
                dia_entry[f"{mes_key}_perdidas"] = data_por_mes[mes][dia]["perdidas"]
                dia_entry[f"{mes_key}_total"] = data_por_mes[mes][dia]["total"]
                dia_entry[f"{mes_key}_nome"] = mes_nome
                
            daily_data.append(dia_entry)
        
        # Preparar metadados dos meses para o frontend
        months_metadata = []
        for mes in meses_analise:
            try:
                mes_obj = datetime.strptime(f"{mes}-01", "%Y-%m-%d")
                months_metadata.append({
                    "key": mes.replace("-", "_"),  # 2025_04
                    "label": mes_obj.strftime("%b %Y"),  # Abr 2025
                    "value": mes,  # 2025-04
                    "total_concluidas": sum(data_por_mes[mes][dia]["concluidas"] for dia in range(1, 32)),
                    "total_canceladas": sum(data_por_mes[mes][dia]["canceladas"] for dia in range(1, 32)),
                    "total_perdidas": sum(data_por_mes[mes][dia]["perdidas"] for dia in range(1, 32)),
                    "total_geral": sum(data_por_mes[mes][dia]["total"] for dia in range(1, 32))
                })
            except:
                continue
        
        return {
            "success": True,
            "periodo_meses": periodo_meses,
            "cidade": cidade,
            "daily_data": daily_data,  # Dados dia por dia (1-31) com todas as linhas dos meses
            "months_metadata": months_metadata,  # Metadados dos meses para legendas e cores
            "total_records": len(daily_data),
            "meses_analisados": meses_analise
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro interno: {str(e)}"}
        )
