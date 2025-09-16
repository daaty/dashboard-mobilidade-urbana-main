#!/usr/bin/env python3
"""
Debug detalhado da API /api/metrics/overview
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from app.api.metrics import extract_city_from_record, matches_city_filter
from sqlalchemy.future import select

async def debug_api_processing():
    """Debug detalhado do processamento da API"""
    print("🔧 DEBUG DETALHADO DA API /api/metrics/overview")
    print("=" * 55)

    async with SessionLocal() as session:
        # Buscar registros como a API faz
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Total de registros encontrados: {len(rides)}")

        # Simular processamento da API
        periodo = "30d"
        cidade = "GUARANTA DO NORTE"

        # Definir datas como na API
        now = datetime.now()
        if periodo == "30d":
            dt_ini = now - timedelta(days=30)
            dt_fim = now

        print(f"📅 Período: {dt_ini.date()} até {dt_fim.date()}")
        print(f"🏙️ Filtro cidade: {cidade}")

        # Processar como a API faz
        concluidas = []
        total_processed = 0
        city_matches = 0
        date_matches = 0

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

            if table_name == "Completed Rides":
                for rec in new_records:
                    total_processed += 1

                    # Detectar cidade
                    cidade_detectada = extract_city_from_record(rec)
                    if cidade_detectada:
                        city_matches += 1

                    # Verificar filtro de cidade
                    if not matches_city_filter(cidade_detectada, cidade):
                        continue

                    # Verificar data (simplificado)
                    # Aqui seria a lógica completa de extração de data
                    date_matches += 1

                    # Adicionar à lista
                    item = {
                        "cidade": cidade_detectada,
                        "id_corrida": rec[0] if len(rec) > 0 else None
                    }
                    concluidas.append(item)

        print("\n📈 RESULTADOS DO PROCESSAMENTO:")
        print(f"   🔢 Total de corridas processadas: {total_processed}")
        print(f"   🏙️ Cidades detectadas: {city_matches}")
        print(f"   📅 Corridas no período: {date_matches}")
        print(f"   ✅ Corridas após filtro: {len(concluidas)}")

        if concluidas:
            print("\n🔍 Amostra de corridas filtradas:")
            for i, corrida in enumerate(concluidas[:5]):
                print(f"   {i+1}. ID: {corrida['id_corrida']}, Cidade: {corrida['cidade']}")

        # Verificar por que GUARANTA DO NORTE não está sendo encontrada
        print("\n🔎 Verificando especificamente GUARANTA DO NORTE:")
        guarantas_found = []
        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        for rec in new_records:
                            cidade_detectada = extract_city_from_record(rec)
                            if cidade_detectada and "GUARANTA" in cidade_detectada.upper():
                                guarantas_found.append({
                                    "cidade": cidade_detectada,
                                    "id": rec[0] if len(rec) > 0 else None,
                                    "endereco": rec[5] if len(rec) > 5 else None
                                })
                except:
                    continue

        print(f"   🏙️ Registros com GUARANTA encontrados: {len(guarantas_found)}")
        if guarantas_found:
            for i, item in enumerate(guarantas_found[:3]):
                print(f"      {i+1}. {item['cidade']} - ID: {item['id']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_api_processing())