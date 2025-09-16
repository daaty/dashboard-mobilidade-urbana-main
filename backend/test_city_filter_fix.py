#!/usr/bin/env python3
"""
Teste da correção do filtro de cidades
Verifica se as cidades agora são detectadas corretamente após a atualização
"""

import sys
import os
import json
import asyncio
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from app.api.metrics import extract_city_from_record
from services.city_service import normalize_city_name
from sqlalchemy.future import select

async def test_city_filter_fix():
    """Testa se a correção do filtro de cidades funcionou"""
    print("🧪 TESTANDO CORREÇÃO DO FILTRO DE CIDADES")
    print("=" * 50)

    async with SessionLocal() as session:
        # Buscar registros de corridas
        result = await session.execute(
            select(RidesData).where(RidesData.table_name == "Completed Rides")
        )
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        # Testar cidades específicas que estavam falhando
        test_cities = ["NOVA MONTE VERDE", "PEIXOTO DE AZEVEDO", "GUARANTA DO NORTE", "NOVA BANDEIRANTES", "MATUPA"]
        city_counts = {city: 0 for city in test_cities}

        # Processar cada registro
        for ride in rides:
            if ride.ride_data:
                try:
                    ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        for rec in new_records:
                            # Usar a função corrigida
                            detected_city = extract_city_from_record(rec)

                            # Verificar se corresponde a alguma cidade de teste
                            for test_city in test_cities:
                                if detected_city and test_city in detected_city.upper():
                                    city_counts[test_city] += 1
                                    break

                except Exception as e:
                    print(f"❌ Erro processando registro: {e}")
                    continue

        # Resultados
        print("\n📈 RESULTADOS DA CORREÇÃO:")
        print("-" * 30)
        total_found = 0
        for city, count in city_counts.items():
            status = "✅" if count > 0 else "❌"
            print(f"{status} {city}: {count} registros")
            total_found += count

        print(f"\n🎯 Total de registros encontrados: {total_found}")

        # Verificar se a correção funcionou
        success = all(count > 0 for count in city_counts.values())
        if success:
            print("\n🎉 CORREÇÃO BEM-SUCEDIDA! Todas as cidades foram detectadas.")
        else:
            print("\n⚠️  CORREÇÃO PARCIAL! Algumas cidades ainda não foram detectadas.")
            failed_cities = [city for city, count in city_counts.items() if count == 0]
            print(f"Cidades que ainda falham: {failed_cities}")

        return success

if __name__ == "__main__":
    asyncio.run(test_city_filter_fix())