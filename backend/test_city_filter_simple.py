#!/usr/bin/env python3
"""
Script simples para testar o filtro de cidade diretamente
"""

import requests
import json

def test_city_filter():
    print("🔍 TESTANDO FILTRO DE CIDADE")
    print("=" * 50)

    # Testar sem filtro
    print("1. Testando SEM filtro de cidade:")
    response = requests.get("http://localhost:8000/api/metrics/overview?periodo=30d")
    if response.status_code == 200:
        data = response.json()
        metrics = data.get("metricas_principais", {})
        print(f"   Concluídas: {metrics.get('corridas_concluidas', 0)}")
        print(f"   Canceladas: {metrics.get('corridas_canceladas', 0)}")
        print(f"   Perdidas: {metrics.get('corridas_perdidas', 0)}")
    else:
        print(f"   Erro: {response.status_code}")

    # Testar com filtro
    print("\n2. Testando COM filtro de cidade (GUARANTA DO NORTE):")
    response = requests.get("http://localhost:8000/api/metrics/overview?cidade=GUARANTA%20DO%20NORTE&periodo=30d")
    if response.status_code == 200:
        data = response.json()
        metrics = data.get("metricas_principais", {})
        print(f"   Concluídas: {metrics.get('corridas_concluidas', 0)}")
        print(f"   Canceladas: {metrics.get('corridas_canceladas', 0)}")
        print(f"   Perdidas: {metrics.get('corridas_perdidas', 0)}")

        # Mostrar algumas corridas se houver
        concluidas = data.get("concluidas", [])
        if concluidas:
            print(f"\n   Primeiras 2 corridas encontradas:")
            for i, ride in enumerate(concluidas[:2]):
                print(f"     {i+1}. ID: {ride.get('id_corrida')} - Cidade: {ride.get('cidade')}")
        else:
            print("   Nenhuma corrida encontrada!")
    else:
        print(f"   Erro: {response.status_code}")

    # Testar cidades disponíveis
    print("\n3. Cidades disponíveis:")
    response = requests.get("http://localhost:8000/api/metrics/cities")
    if response.status_code == 200:
        data = response.json()
        cities = data.get("cities", [])
        print(f"   Cidades: {cities}")
    else:
        print(f"   Erro ao buscar cidades: {response.status_code}")

if __name__ == "__main__":
    test_city_filter()