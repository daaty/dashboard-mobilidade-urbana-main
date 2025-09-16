#!/usr/bin/env python3
"""
Análise específica de onde NOVA MONTE VERDE aparece nos registros
"""

import sys
import os
import json
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select

async def find_nova_monte_verde():
    """Encontrar especificamente onde NOVA MONTE VERDE aparece nos registros"""
    print("🔍 PROCURANDO NOVA MONTE VERDE NOS REGISTROS")
    print("=" * 60)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        found_records = []

        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        for i, rec in enumerate(new_records):
                            # Procurar NOVA MONTE VERDE em todos os campos
                            found_in_fields = []
                            for j, field in enumerate(rec):
                                if field and "NOVA MONTE VERDE" in str(field).upper():
                                    found_in_fields.append((j, str(field)))

                            if found_in_fields:
                                found_records.append({
                                    'record_index': i,
                                    'record_length': len(rec),
                                    'found_in_fields': found_in_fields,
                                    'full_record': rec
                                })

                except Exception as e:
                    continue

        print(f"\n🏙️ Registros contendo 'NOVA MONTE VERDE': {len(found_records)}")
        print("-" * 50)

        if found_records:
            for i, record in enumerate(found_records[:3]):  # Mostrar primeiros 3
                print(f"\n📋 Registro {i+1}:")
                print(f"   Tamanho: {record['record_length']} campos")
                print(f"   Campos com NOVA MONTE VERDE:")
                for field_idx, field_value in record['found_in_fields']:
                    print(f"     Índice {field_idx}: '{field_value}'")

                # Mostrar alguns campos ao redor para contexto
                print(f"   Contexto (campos 0-20):")
                for j in range(min(21, record['record_length'])):
                    value = record['full_record'][j] if j < record['record_length'] else "N/A"
                    marker = " <-- NOVA MONTE VERDE" if any(j == idx for idx, _ in record['found_in_fields']) else ""
                    print(f"     [{j}]: '{value}'{marker}")
        else:
            print("❌ NENHUM registro encontrado contendo 'NOVA MONTE VERDE'")

        # Também procurar por variações
        print("\n🔄 Procurando variações...")
        variations = ["NOVA MONTE VERDE", "NOVA MONTEVERDE", "MONTE VERDE", "NOVA MV"]
        for variation in variations:
            count = 0
            for r in rides:
                if r.ride_data:
                    try:
                        ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
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
    asyncio.run(find_nova_monte_verde())