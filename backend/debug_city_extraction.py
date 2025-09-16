#!/usr/bin/env python3
"""
Script detalhado para debugar a extração de cidades
"""

import sys
import os
import json
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select
from datetime import datetime, timedelta

def extract_city_from_record(rec):
    """Detecta cidade baseada nos dados do registro"""
    # Diferentes índices dependendo do tipo de corrida
    possible_city_indices = [15, 17, 8, 9, 10]  # Diferentes posições onde a cidade pode estar

    for idx in possible_city_indices:
        if idx < len(rec) and rec[idx]:
            city_str = str(rec[idx]).strip().upper()
            # Limpar dados de cidade
            if city_str in ["MATUPA", "MATUPÁ"]:
                return "MATUPA"
            elif city_str == "PEIXOTO":
                return "PEIXOTO"
            elif "GUARANTA" in city_str:
                return "GUARANTA DO NORTE"

    # Fallback: detectar pela localização (índices 5 e 6)
    if len(rec) > 6:
        local_str = str(rec[5]) if len(rec) > 5 else ""
        destino_str = str(rec[6]) if len(rec) > 6 else ""
        local_destino = (local_str + " " + destino_str).upper()

        if "MATUPA" in local_destino or "MATUPÁ" in local_destino:
            return "MATUPA"
        elif "PEIXOTO" in local_destino:
            return "PEIXOTO"
        elif "GUARANTA" in local_destino:
            return "GUARANTA DO NORTE"

    return "Unnamed"  # Default se não conseguir detectar

async def debug_city_extraction():
    """Debug detalhado da extração de cidades"""
    print("🔍 DEBUG DETALHADO DA EXTRAÇÃO DE CIDADES")
    print("=" * 80)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        city_counts = {}
        total_records = 0
        records_with_cities = 0

        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        for rec in new_records:
                            total_records += 1
                            cidade_detectada = extract_city_from_record(rec)

                            if cidade_detectada != "Unnamed":
                                records_with_cities += 1
                                if cidade_detectada not in city_counts:
                                    city_counts[cidade_detectada] = 0
                                city_counts[cidade_detectada] += 1

                            # Mostrar detalhes dos primeiros registros de GUARANTA
                            if cidade_detectada == "GUARANTA DO NORTE" and city_counts.get("GUARANTA DO NORTE", 0) <= 3:
                                print(f"\n🏙️ Registro GUARANTA DO NORTE #{city_counts['GUARANTA DO NORTE']}:")
                                print(f"   Tamanho do registro: {len(rec)}")
                                print(f"   Índices testados: [15, 17, 8, 9, 10]")
                                for idx in [15, 17, 8, 9, 10]:
                                    if idx < len(rec):
                                        print(f"   rec[{idx}]: '{rec[idx]}'")
                                    else:
                                        print(f"   rec[{idx}]: (índice fora do range)")

                except Exception as e:
                    continue

        print("\n📈 RESULTADOS DA ANÁLISE:")
        print(f"   Total de registros analisados: {total_records}")
        print(f"   Registros com cidades detectadas: {records_with_cities}")
        print(f"   Taxa de detecção: {(records_with_cities/total_records*100):.1f}%" if total_records > 0 else "0%")

        print("\n🏙️ CONTAGEM POR CIDADE:")
        for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {city}: {count} registros")

        if "GUARANTA DO NORTE" not in city_counts:
            print("\n❌ NENHUM registro de GUARANTA DO NORTE encontrado!")
        else:
            print(f"\n✅ GUARANTA DO NORTE encontrado: {city_counts['GUARANTA DO NORTE']} registros")

if __name__ == "__main__":
    asyncio.run(debug_city_extraction())