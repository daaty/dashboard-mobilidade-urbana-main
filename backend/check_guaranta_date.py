#!/usr/bin/env python3
"""
Verificar data da corrida de GUARANTA DO NORTE
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from app.api.metrics import extract_city_from_record, extract_datetime_from_record
from sqlalchemy.future import select

async def check_guaranta_date():
    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print("🔍 Procurando corrida de GUARANTA DO NORTE:")
        found = False

        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        for rec in new_records:
                            cidade = extract_city_from_record(rec)
                            if cidade and "GUARANTA" in cidade.upper():
                                # Extrair data
                                if r.source == "monitoring-service-adapted":
                                    hora = rec[7] if len(rec) > 7 else None
                                else:
                                    hora = rec[6] if len(rec) > 6 else None

                                dt_str = extract_datetime_from_record([hora], 0) if hora else None
                                print(f"✅ Encontrada: ID {rec[0]}, Cidade: {cidade}")
                                print(f"   Data: {dt_str}")
                                print(f"   Source: {r.source}")
                                found = True
                except Exception as e:
                    continue

        if not found:
            print("❌ Nenhuma corrida de GUARANTA DO NORTE encontrada")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_guaranta_date())