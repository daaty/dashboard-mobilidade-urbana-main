#!/usr/bin/env python3
"""
Investigar onde MATUPA aparece nos registros
"""

import sys
import os
import json
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy.future import select

async def find_matupa():
    """Encontrar onde MATUPA aparece nos registros"""
    print("🔍 PROCURANDO MATUPA NOS REGISTROS")
    print("=" * 40)

    async with SessionLocal() as session:
        result = await session.execute(
            select(RidesData).where(RidesData.table_name == "Completed Rides")
        )
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        matupa_count = 0
        matupa_records = []

        for ride in rides:
            if ride.ride_data:
                try:
                    ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        for rec in new_records:
                            # Procurar MATUPA em todos os campos
                            found_matupa = False
                            for idx, field in enumerate(rec):
                                if field and "MATUPA" in str(field).upper():
                                    matupa_count += 1
                                    found_matupa = True
                                    if len(matupa_records) < 3:  # Mostrar apenas primeiros 3
                                        matupa_records.append((idx, field))

                            if found_matupa:
                                break  # Já contou este registro

                except Exception as e:
                    continue

        print(f"\n🏙️ Registros contendo 'MATUPA': {matupa_count}")

        if matupa_records:
            print("\n📋 Exemplos encontrados:")
            for idx, (field_idx, field_value) in enumerate(matupa_records):
                print(f"   Registro {idx+1}: Índice {field_idx} = '{field_value}'")

        # Verificar variações
        print("\n🔄 Procurando variações de MATUPA...")
        variations = ["MATUPA", "MT MATUPA", "MATUPÁ"]
        for variation in variations:
            count = 0
            for ride in rides:
                if ride.ride_data:
                    try:
                        ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                        table_name = ride_data.get("tableName", "")
                        new_records = ride_data.get("newRecords", [])

                        if table_name == "Completed Rides":
                            for rec in new_records:
                                for field in rec:
                                    if field and variation in str(field).upper():
                                        count += 1
                                        break
                    except:
                        continue

            print(f"   '{variation}': {count} registros")

if __name__ == "__main__":
    asyncio.run(find_matupa())