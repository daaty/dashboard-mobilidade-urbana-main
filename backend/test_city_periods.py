#!/usr/bin/env python3
"""
Script para testar o filtro de cidade com diferentes períodos
"""

import requests
import json

def test_city_filter_periods():
    print("🔍 TESTANDO FILTRO DE CIDADE COM DIFERENTES PERÍODOS")
    print("=" * 60)

    periods = ["hoje", "7d", "30d", "3m", "6m", "12m"]
    target_city = "GUARANTA DO NORTE"

    for period in periods:
        print(f"\n📅 Testando período: {period}")

        # Sem filtro
        response = requests.get(f"http://localhost:8000/api/metrics/overview?periodo={period}")
        if response.status_code == 200:
            data = response.json()
            metrics = data.get("metricas_principais", {})
            total_concluidas = metrics.get('corridas_concluidas', 0)
            print(f"   Sem filtro - Concluídas: {total_concluidas}")

        # Com filtro de cidade
        response = requests.get(f"http://localhost:8000/api/metrics/overview?cidade={target_city}&periodo={period}")
        if response.status_code == 200:
            data = response.json()
            metrics = data.get("metricas_principais", {})
            filtered_concluidas = metrics.get('corridas_concluidas', 0)
            print(f"   Com filtro - Concluídas: {filtered_concluidas}")

            if filtered_concluidas > 0:
                print("   ✅ ENCONTROU RESULTADOS!")
                concluidas = data.get("concluidas", [])
                if concluidas:
                    print(f"   📋 Primeira corrida: ID {concluidas[0].get('id_corrida')} - {concluidas[0].get('cidade')}")
            else:
                print("   ❌ Nenhum resultado encontrado")

if __name__ == "__main__":
    test_city_filter_periods()