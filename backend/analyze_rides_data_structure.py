#!/usr/bin/env python3
"""
Análise completa da estrutura de dados na tabela rides_data
Verificar diferenças entre dados do XLS e do scraper
"""

import sys
import os
import json
from datetime import datetime
from collections import defaultdict, Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy.future import select

async def analyze_rides_data_structure():
    """Análise completa da estrutura de dados na tabela rides_data"""
    print("🔍 ANÁLISE COMPLETA DA TABELA RIDES_DATA")
    print("=" * 60)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Total de registros na tabela: {len(rides)}")

        # Separar por fonte
        sources = defaultdict(list)
        for ride in rides:
            source = ride.source or "unknown"
            sources[source].append(ride)

        print("\n📋 Distribuição por fonte:")
        for source, rides_list in sources.items():
            print(f"   {source}: {len(rides_list)} registros")

        # Analisar estrutura por fonte
        for source_name, rides_list in sources.items():
            print(f"\n🏷️  ANÁLISE DA FONTE: {source_name}")
            print("-" * 40)

            # Analisar tipos de tabelas
            table_types = Counter()
            sample_records = []

            for ride in rides_list[:10]:  # Analisar primeiras 10
                if ride.ride_data:
                    try:
                        ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                        table_name = ride_data.get("tableName", "Unknown")
                        table_types[table_name] += 1

                        # Coletar amostra de registros
                        new_records = ride_data.get("newRecords", [])
                        if new_records and len(sample_records) < 3:
                            sample_records.append({
                                "table_name": table_name,
                                "source": source_name,
                                "records": new_records[:2],  # Primeiros 2 registros
                                "total_records": len(new_records)
                            })
                    except Exception as e:
                        print(f"   ❌ Erro ao processar registro: {e}")
                        continue

            print(f"   📊 Tipos de tabelas encontradas:")
            for table_name, count in table_types.items():
                print(f"      {table_name}: {count} registros")

            # Mostrar estrutura dos registros
            print(f"\n   📋 Estrutura dos registros ({source_name}):")
            for i, sample in enumerate(sample_records):
                print(f"\n      🔸 Amostra {i+1} - Tabela: {sample['table_name']}")
                print(f"         Total de registros: {sample['total_records']}")
                for j, record in enumerate(sample['records'][:1]):  # Mostrar apenas 1 registro detalhado
                    print(f"         📝 Registro {j+1} (tamanho: {len(record)} campos):")
                    for idx, field in enumerate(record):
                        if field is not None and str(field).strip():
                            field_preview = str(field)[:80] + "..." if len(str(field)) > 80 else str(field)
                            print(f"            [{idx}]: {field_preview}")

        # Análise específica de Completed Rides
        print("\n🎯 ANÁLISE ESPECÍFICA DE COMPLETED RIDES")
        print("-" * 50)

        completed_by_source = defaultdict(list)

        for ride in rides:
            if ride.ride_data:
                try:
                    ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                    table_name = ride_data.get("tableName", "")

                    if table_name == "Completed Rides":
                        source = ride.source or "unknown"
                        new_records = ride_data.get("newRecords", [])
                        completed_by_source[source].extend(new_records)
                except:
                    continue

        for source_name, records in completed_by_source.items():
            print(f"\n🏷️  Completed Rides - Fonte: {source_name}")
            print(f"   📊 Total de registros: {len(records)}")

            if records:
                # Analisar estrutura dos primeiros registros
                print(f"   📋 Estrutura dos primeiros registros:")

                for i, record in enumerate(records[:3]):
                    print(f"\n      🔸 Registro {i+1} (tamanho: {len(record)} campos):")
                    for idx in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 17]:  # Campos importantes
                        if idx < len(record):
                            field = record[idx]
                            if field is not None:
                                field_preview = str(field)[:60] + "..." if len(str(field)) > 60 else str(field)
                                print(f"         [{idx}]: {field_preview}")

        # Análise de cidades encontradas
        print("\n🏙️  ANÁLISE DE CIDADES ENCONTRADAS")
        print("-" * 40)

        from app.api.metrics import extract_city_from_record

        cities_by_source = defaultdict(Counter)

        for ride in rides:
            if ride.ride_data:
                try:
                    ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                    table_name = ride_data.get("tableName", "")

                    if table_name == "Completed Rides":
                        source = ride.source or "unknown"
                        new_records = ride_data.get("newRecords", [])

                        for record in new_records:
                            city = extract_city_from_record(record)
                            if city:
                                cities_by_source[source][city] += 1
                except:
                    continue

        for source_name, cities in cities_by_source.items():
            print(f"\n🏷️  Cidades encontradas - Fonte: {source_name}")
            print(f"   📊 Total de cidades únicas: {len(cities)}")
            print(f"   📋 Top 10 cidades:")
            for city, count in cities.most_common(10):
                print(f"      {city}: {count} registros")

if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_rides_data_structure())