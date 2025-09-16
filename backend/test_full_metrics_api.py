#!/usr/bin/env python3
"""
Teste completo da API de métricas com filtro de cidade
Simula exatamente como a API funciona para verificar o problema
"""

import sys
import os
import json
import asyncio
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from app.api.metrics import extract_city_from_record, matches_city_filter
from sqlalchemy.future import select

async def test_full_metrics_api():
    """Testa a API completa de métricas com filtro de cidade"""
    print("🧪 TESTANDO API COMPLETA DE MÉTRICAS")
    print("=" * 45)

    async with SessionLocal() as session:
        # Buscar registros de corridas
        result = await session.execute(
            select(RidesData).where(RidesData.table_name == "Completed Rides")
        )
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        # Simular a lógica da API de métricas
        test_cities = ["MATUPA", "NOVA MONTE VERDE", "PEIXOTO DE AZEVEDO"]
        results = {}

        for filter_city in test_cities:
            print(f"\n🏙️ Testando filtro: {filter_city}")
            filtered_records = []
            detected_cities = []

            for ride in rides:
                if ride.ride_data:
                    try:
                        ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                        table_name = ride_data.get("tableName", "")
                        new_records = ride_data.get("newRecords", [])

                        if table_name == "Completed Rides":
                            for rec in new_records:
                                # Extrair cidade usando a função corrigida
                                detected_city = extract_city_from_record(rec)
                                detected_cities.append(detected_city)

                                # Aplicar filtro de cidade
                                if matches_city_filter(detected_city, filter_city):
                                    filtered_records.append(rec)

                    except Exception as e:
                        continue

            results[filter_city] = {
                'filtered_count': len(filtered_records),
                'unique_cities_detected': len(set(detected_cities)),
                'sample_cities': list(set(detected_cities))[:5]  # Primeiras 5 cidades detectadas
            }

            print(f"   ✅ Registros filtrados: {len(filtered_records)}")
            print(f"   📍 Cidades únicas detectadas: {len(set(detected_cities))}")
            print(f"   🔍 Amostra de cidades: {list(set(detected_cities))[:5]}")

        # Resumo final
        print("\n📈 RESUMO FINAL:")
        print("-" * 30)
        for city, data in results.items():
            status = "✅" if data['filtered_count'] > 0 else "❌"
            print(f"{status} {city}: {data['filtered_count']} registros")

        return results

if __name__ == "__main__":
    asyncio.run(test_full_metrics_api())