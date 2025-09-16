#!/usr/bin/env python3
"""
Análise crítica detalhada do filtro de cidade
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

def matches_city_filter(cidade_item, cidade_filter):
    """Compara cidade de forma robusta, lidando com None e diferenças de formatação"""
    if not cidade_filter:
        return True  # Sem filtro, aceitar tudo

    if not cidade_item:
        return False  # Item sem cidade não corresponde a filtro

    # Normalizar ambas as strings para comparação
    item_norm = str(cidade_item).strip().upper()
    filter_norm = str(cidade_filter).strip().upper()

    return item_norm == filter_norm

async def analyze_city_filter():
    """Análise crítica detalhada do filtro de cidade"""
    print("🔍 ANÁLISE CRÍTICA DO FILTRO DE CIDADE")
    print("=" * 80)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        # Cidades para testar
        test_cities = [
            "MATUPA",
            "PEIXOTO DE AZEVEDO",
            "GUARANTA DO NORTE",
            "NOVA MONTE VERDE",
            "NOVA BANDEIRANTES"
        ]

        city_analysis = {}

        for target_city in test_cities:
            print(f"\n🏙️ ANALISANDO: {target_city}")
            print("-" * 50)

            found_records = []
            detection_details = []

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

                                # Testar se corresponde ao filtro
                                matches = matches_city_filter(cidade_detectada, target_city)

                                if cidade_detectada != "Unnamed":
                                    detection_details.append({
                                        'cidade_detectada': cidade_detectada,
                                        'matches_filter': matches,
                                        'record_length': len(rec),
                                        'indices_checked': [15, 17, 8, 9, 10],
                                        'values_at_indices': {
                                            15: rec[15] if 15 < len(rec) else None,
                                            17: rec[17] if 17 < len(rec) else None,
                                            8: rec[8] if 8 < len(rec) else None,
                                            9: rec[9] if 9 < len(rec) else None,
                                            10: rec[10] if 10 < len(rec) else None
                                        }
                                    })

                                if matches:
                                    found_records.append({
                                        'id': r.id,
                                        'record': rec,
                                        'cidade': cidade_detectada,
                                        'table_name': table_name
                                    })

                    except Exception as e:
                        continue

            print(f"   Registros encontrados: {len(found_records)}")
            print(f"   Detecções de cidade analisadas: {len(detection_details)}")

            # Análise das detecções
            unique_detections = set()
            for detail in detection_details:
                unique_detections.add(detail['cidade_detectada'])

            print(f"   Cidades únicas detectadas: {sorted(unique_detections)}")

            # Mostrar primeiras detecções para debug
            if detection_details:
                print("\n   📋 PRIMEIRAS 5 DETECÇÕES:")
                for i, detail in enumerate(detection_details[:5]):
                    print(f"     {i+1}. Detectada: '{detail['cidade_detectada']}' | Match: {detail['matches_filter']}")
                    print(f"        Valores nos índices: {detail['values_at_indices']}")

            city_analysis[target_city] = {
                'found_records': len(found_records),
                'detection_details': len(detection_details),
                'unique_detections': list(unique_detections)
            }

        print("\n📊 RESUMO DA ANÁLISE:")
        print("=" * 80)
        for city, analysis in city_analysis.items():
            status = "✅ FUNCIONANDO" if analysis['found_records'] > 0 else "❌ FALHANDO"
            print(f"   {city}: {analysis['found_records']} registros | {status}")

        # Análise específica dos problemas
        print("\n🔍 ANÁLISE DE PROBLEMAS:")
        print("-" * 80)

        # Verificar se há problemas de normalização
        print("1. VERIFICAÇÃO DE NORMALIZAÇÃO:")
        test_cases = [
            ("MATUPA", "MATUPA"),
            ("MATUPÁ", "MATUPA"),
            ("PEIXOTO", "PEIXOTO DE AZEVEDO"),
            ("PEIXOTO DE AZEVEDO", "PEIXOTO DE AZEVEDO"),
            ("GUARANTA DO NORTE", "GUARANTA DO NORTE"),
            ("GUARANTA", "GUARANTA DO NORTE"),
            ("NOVA MONTE VERDE", "NOVA MONTE VERDE"),
            ("NOVA BANDEIRANTES", "NOVA BANDEIRANTES")
        ]

        for item, filter_city in test_cases:
            matches = matches_city_filter(item, filter_city)
            print(f"   '{item}' vs '{filter_city}' = {matches}")

if __name__ == "__main__":
    asyncio.run(analyze_city_filter())