from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from typing import Optional
import json
from collections import defaultdict

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session


@router.get("/mapa-calor-problemas")
async def get_mapa_calor_problemas(
    db: AsyncSession = Depends(get_db),
    periodo: str = Query("30d", enum=["hoje", "7d", "30d", "3m", "6m", "12m"]),
    cidade: Optional[str] = Query(None)
):
    result = await db.execute(select(RidesData))
    rides = result.scalars().all()
    pontos = []
    for r in rides:
        ride_data = r.ride_data
        if isinstance(ride_data, str):
            try:
                ride_data = json.loads(ride_data)
            except Exception:
                continue
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        # Canceladas
        if table_name in ["Cancelled Rides", "corridas_canceladas"]:
            for rec in new_records:
                endereco = rec[4] if len(rec) > 4 else None
                bairro = rec[5] if len(rec) > 5 else None
                motivo = rec[6] if len(rec) > 6 else None
                cidade = rec[7] if len(rec) > 7 else None
                estado = rec[8] if len(rec) > 8 else None
                pontos.append({
                    "endereco": endereco,
                    "bairro": bairro,
                    "cidade": cidade,
                    "estado": estado,
                    "motivo": motivo,
                    "status": "cancelada"
                })
        # Perdidas
        elif table_name in ["Missed Rides", "corridas_perdidas"]:
            for rec in new_records:
                bairro = rec[3] if len(rec) > 3 else None
                motivo = rec[5] if len(rec) > 5 else None
                pontos.append({
                    "bairro": bairro,
                    "motivo": motivo,
                    "status": "perdida"
                })
        # Concluídas
        elif table_name in ["Completed Rides", "corridas_concluidas"]:
            for rec in new_records:
                bairro = rec[4] if len(rec) > 4 else None
                pontos.append({
                    "bairro": bairro,
                    "motivo": None,
                    "status": "concluida"
                })
    # Remove pontos sem bairro
    pontos = [p for p in pontos if p["bairro"]]
    return {"pontos": pontos}
