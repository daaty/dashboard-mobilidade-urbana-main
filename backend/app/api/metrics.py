
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
import json

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/overview")
async def get_metrics_overview(db: AsyncSession = Depends(get_db)):
    # Buscar todos os registros da tabela rides_data
    result = await db.execute(select(RidesData))
    rides = result.scalars().all()

    concluidas, canceladas, perdidas = [], [], []

    # Extrair e processar os dados do campo ride_data (JSON)
    for r in rides:
        ride_data = r.ride_data
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
                concluidas.append({
                    "nome": rec[2] if len(rec) > 2 else None,
                    "avatar": None,
                    "hora": rec[7] if len(rec) > 7 else None,
                    "grupo": rec[9] if len(rec) > 9 else None,
                    "local": rec[5] if len(rec) > 5 else None,
                    "destino": rec[6] if len(rec) > 6 else None,
                    "cidade": None,
                    "tempo": None
                })
        # Missed Rides
        elif table_name == "Missed Rides":
            for rec in new_records:
                perdidas.append({
                    "nome": rec[1] if len(rec) > 1 else None,
                    "avatar": None,
                    "hora": rec[6] if len(rec) > 6 else None,
                    "grupo": rec[4] if len(rec) > 4 else None,
                    "local": rec[3] if len(rec) > 3 else None,
                    "destino": None,
                    "cidade": None,
                    "tempo": None
                })
        # Scheduled Rides (considerar como canceladas ou agendadas)
        elif table_name == "Scheduled Rides":
            for rec in new_records:
                canceladas.append({
                    "nome": rec[1] if len(rec) > 1 else None,
                    "avatar": None,
                    "hora": rec[10] if len(rec) > 10 else None,
                    "grupo": rec[6] if len(rec) > 6 else None,
                    "local": rec[8] if len(rec) > 8 else None,
                    "destino": rec[9] if len(rec) > 9 else None,
                    "cidade": None,
                    "tempo": None
                })
        # Ongoing Rides (não contabiliza para métricas principais)
        # elif table_name == "Ongoing Rides":
        #     ...

    metricas_principais = {
        "corridas_concluidas": len(concluidas),
        "corridas_canceladas": len(canceladas),
        "corridas_perdidas": len(perdidas),
        "variacao_concluidas": 0.0,
        "variacao_canceladas": 0.0,
        "variacao_perdidas": 0.0
    }

    atividade_recente = {
        "concluidas": concluidas[:10],
        "canceladas": canceladas[:10],
        "perdidas": perdidas[:10]
    }

    return {
        "metricas_principais": metricas_principais,
        "atividade_recente": atividade_recente
    }
