from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from typing import Optional

import json
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.city_service import get_cities_from_rides_data

router = APIRouter()

def ordenar_por_data(lista):
    return sorted(lista, key=lambda x: x.get("dt_corrida", datetime.min), reverse=True)

async def get_db():
    async with SessionLocal() as session:
        yield session

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
        dt_ini = now - timedelta(days=150)  # Ampliado para pegar dados de abril
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
                    
                nome_motorista = rec[1] if len(rec) > 1 else None  # Driver Name
                nome_passageiro = rec[2] if len(rec) > 2 else None  # User Name
                telefone = rec[3] if len(rec) > 3 else None  # User Phone No
                
                # Usar nome do passageiro como principal, motorista como fallback
                nome = nome_passageiro or nome_motorista or "Usuário"
                
                hora = rec[6] if len(rec) > 6 else None
                dt_corrida = None
                hora_formatada = None
                if hora:
                    import re
                    match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", hora)
                    if match:
                        dt_str = match.group(1)
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = None
                    else:
                        hora_formatada = hora  # fallback
                item = {
                    "id_corrida": id_corrida,
                    "nome": nome,
                    "avatar": gerar_avatar(nome),
                    "hora": hora_formatada,
                    "dt_corrida": dt_corrida,
                    "grupo": rec[9] if len(rec) > 9 else None,
                    "local": rec[4] if len(rec) > 4 else None,
                    "destino": rec[5] if len(rec) > 5 else None,
                    "cidade": rec[15] if len(rec) > 15 else None,  # Cidade no índice 15 para corridas concluídas
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
                    
                nome = rec[1] if len(rec) > 1 else None  # passageiro correto
                hora = rec[6] if len(rec) > 6 else None
                motivo = rec[5] if len(rec) > 5 else None  # índice correto para motivo
                dt_corrida = None
                hora_formatada = None
                if hora:
                    import re
                    match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", hora)
                    if match:
                        dt_str = match.group(1)
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = None
                    else:
                        hora_formatada = hora
                item = {
                    "id_corrida": id_corrida,
                    "nome": nome,
                    "avatar": gerar_avatar(nome),
                    "hora": hora_formatada,
                    "dt_corrida": dt_corrida,
                    "grupo": rec[4] if len(rec) > 4 else None,
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
                    
                nome = rec[2] if len(rec) > 2 else None  # passageiro correto (índice 2)
                hora = rec[11] if len(rec) > 11 else None  # CORRIGIDO: data está no índice 11
                motivo = rec[12] if len(rec) > 12 else None  # CORRIGIDO: motivo está no índice 12
                dt_corrida = None
                hora_formatada = None
                if hora:
                    import re
                    match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", hora)
                    if match:
                        dt_str = match.group(1)
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = None
                    else:
                        hora_formatada = hora
                item = {
                    "id_corrida": id_corrida,
                    "nome": nome,
                    "avatar": gerar_avatar(nome),
                    "hora": hora_formatada,
                    "dt_corrida": dt_corrida,
                    "grupo": rec[4] if len(rec) > 4 else None,
                    "local": rec[5] if len(rec) > 5 else None,
                    "destino": rec[6] if len(rec) > 6 else None,
                    "cidade": rec[17] if len(rec) > 17 else None,  # Cidade no índice 17 para corridas canceladas
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
                    import re
                    match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", hora)
                    if match:
                        dt_str = match.group(1)
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            hora_formatada = dt_str
                        except Exception:
                            dt_corrida = None
                            hora_formatada = None
                    else:
                        hora_formatada = hora
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
