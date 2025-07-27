from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
    # Função para ordenar por data
    def ordenar_por_data(lista):
        return sorted(lista, key=lambda x: x.get("dt_corrida", datetime.min), reverse=True)

import json
from datetime import datetime, timedelta

router = APIRouter()

def ordenar_por_data(lista):
    return sorted(lista, key=lambda x: x.get("dt_corrida", datetime.min), reverse=True)

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/overview")
async def get_metrics_overview(
    db: AsyncSession = Depends(get_db),
    periodo: str = Query("hoje", enum=["hoje", "7d", "30d"], description="Período do filtro: hoje, 7d, 30d")
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
    else:  # "30d"
        dt_ini = now - timedelta(days=30)
        dt_fim = now
        dt_ini_ant = dt_ini - timedelta(days=30)
        dt_fim_ant = dt_ini

    # Função para gerar avatar fictício baseado no nome
    def gerar_avatar(nome):
        if not nome:
            return "https://ui-avatars.com/api/?name=User&background=random"
        nome_url = nome.replace(" ", "+")
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
        # Completed Rides
        if table_name == "Completed Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
                hora = rec[7] if len(rec) > 7 else None
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
                    "local": rec[5] if len(rec) > 5 else None,
                    "destino": rec[6] if len(rec) > 6 else None,
                    "cidade": None,
                    "tempo": None
                }
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_concluidas:
                    concluidas.append(item)
                    ids_concluidas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_concluidas:
                    concluidas_ant.append(item)
                    ids_concluidas.add((id_corrida, hora_formatada))
        # Missed Rides
        elif table_name == "Missed Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
                hora = rec[6] if len(rec) > 6 else None
                motivo = rec[7] if len(rec) > 7 else None
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
                    "cidade": None,
                    "tempo": None,
                    "motivo": motivo
                }
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_perdidas:
                    perdidas.append(item)
                    ids_perdidas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_perdidas:
                    perdidas_ant.append(item)
                    ids_perdidas.add((id_corrida, hora_formatada))
        # Cancelled Rides (prioritário para canceladas)
        elif table_name == "Cancelled Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
                hora = rec[9] if len(rec) > 9 else None
                motivo = rec[10] if len(rec) > 10 else None
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
                    "cidade": None,
                    "tempo": None,
                    "motivo": motivo
                }
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas_ant.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))
        # Scheduled Rides (fallback para canceladas)
        elif table_name == "Scheduled Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
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
                    "cidade": None,
                    "tempo": None
                }
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas_ant.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))
    # Utilizar set para evitar duplicidade pelo id da corrida e data
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
        # Completed Rides
        if table_name == "Completed Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
                hora = rec[7] if len(rec) > 7 else None
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
                    "local": rec[5] if len(rec) > 5 else None,
                    "destino": rec[6] if len(rec) > 6 else None,
                    "cidade": None,
                    "tempo": None
                }
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_concluidas:
                    concluidas.append(item)
                    ids_concluidas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_concluidas:
                    concluidas_ant.append(item)
                    ids_concluidas.add((id_corrida, hora_formatada))
        # Missed Rides
        elif table_name == "Missed Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
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
                    "cidade": None,
                    "tempo": None
                }
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_perdidas:
                    perdidas.append(item)
                    ids_perdidas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_perdidas:
                    perdidas_ant.append(item)
                    ids_perdidas.add((id_corrida, hora_formatada))
        # Cancelled Rides (prioritário para canceladas)
        elif table_name == "Cancelled Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
                hora = rec[9] if len(rec) > 9 else None
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
                    "cidade": None,
                    "tempo": None
                }
                if dt_corrida and dt_ini <= dt_corrida <= dt_fim and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))
                elif dt_corrida and dt_ini_ant <= dt_corrida < dt_fim_ant and (id_corrida, hora_formatada) not in ids_canceladas:
                    canceladas_ant.append(item)
                    ids_canceladas.add((id_corrida, hora_formatada))
        # Scheduled Rides (fallback para canceladas)
        elif table_name == "Scheduled Rides":
            for rec in new_records:
                id_corrida = rec[0] if len(rec) > 0 else None
                nome = rec[3] if len(rec) > 3 else None  # passageiro
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
                    "cidade": None,
                    "tempo": None
                }
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

    return {
        "metricas_principais": metricas_principais,
        "atividade_recente": atividade_recente
    }
