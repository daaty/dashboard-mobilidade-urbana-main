#!/usr/bin/env python3
"""
Script para debugar o filtro de cidade no endpoint /api/metrics/overview
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

async def debug_city_filter():
    """Debug do filtro de cidade"""
    print("🔍 DEBUG DO FILTRO DE CIDADE")
    print("=" * 80)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        # Filtrar apenas corridas concluídas para teste
        target_city = "GUARANTA DO NORTE"
        found_records = []

        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        for rec in new_records:
                            # Extrair cidade
                            cidade_detectada = extract_city_from_record(rec)

                            if cidade_detectada == target_city:
                                found_records.append({
                                    'id': r.id,
                                    'record': rec,
                                    'cidade': cidade_detectada,
                                    'table_name': table_name
                                })

                except Exception as e:
                    continue

        print(f"\n🏙️ Registros encontrados para {target_city}: {len(found_records)}")
        print("-" * 50)

        if found_records:
            for i, record in enumerate(found_records[:5]):  # Mostrar apenas os primeiros 5
                print(f"\n📋 Registro {i+1} (ID: {record['id']}):")
                print(f"   Cidade detectada: {record['cidade']}")
                print(f"   Table: {record['table_name']}")
                print(f"   Record completo: {record['record'][:10]}...")  # Mostrar apenas primeiros 10 campos
        else:
            print("❌ Nenhum registro encontrado para esta cidade!")

        # Testar também sem filtro para ver se há dados
        print("\n🔄 Testando SEM filtro de cidade:")
        total_records = 0
        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name == "Completed Rides":
                        total_records += len(new_records)
                except Exception:
                    continue

        # Testar comparação de cidades
        print("\n🔍 TESTANDO COMPARAÇÃO DE CIDADES:")
        test_city_filter = "GUARANTA DO NORTE"

        for record in found_records[:3]:  # Testar apenas os primeiros 3
            cidade_item = record['cidade']
            print(f"   Filtro: '{test_city_filter}' (len={len(test_city_filter)})")
            print(f"   Item:   '{cidade_item}' (len={len(cidade_item)})")
            print(f"   Igual?  {cidade_item == test_city_filter}")
            print(f"   Upper:  '{cidade_item.upper()}' == '{test_city_filter.upper()}' = {cidade_item.upper() == test_city_filter.upper()}")
            print(f"   Strip:  '{cidade_item.strip()}' == '{test_city_filter.strip()}' = {cidade_item.strip() == test_city_filter.strip()}")
            print(f"   Repr:   {repr(cidade_item)} vs {repr(test_city_filter)}")
            print()