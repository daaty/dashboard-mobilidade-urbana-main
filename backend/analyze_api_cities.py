#!/usr/bin/env python3
import requests
import json
from collections import defaultdict

def analyze_api_cities():
    """Analisar cidades retornadas pela API sem filtro"""
    response = requests.get('http://localhost:8000/api/metrics/overview?periodo=30d')
    data = response.json()

    cities_by_type = {
        "concluidas": defaultdict(int),
        "canceladas": defaultdict(int),
        "perdidas": defaultdict(int)
    }

    # Analisar corridas concluídas
    for ride in data.get('concluidas', []):
        city = ride.get('cidade', 'N/A')
        cities_by_type["concluidas"][city] += 1

    # Analisar corridas canceladas
    for ride in data.get('canceladas', []):
        city = ride.get('cidade', 'N/A')
        cities_by_type["canceladas"][city] += 1

    # Analisar corridas perdidas
    for ride in data.get('perdidas', []):
        city = ride.get('cidade', 'N/A')
        cities_by_type["perdidas"][city] += 1

    print("=== CIDADES ENCONTRADAS NA API (SEM FILTRO) ===")
    print(f"Corridas Concluídas ({len(data.get('concluidas', []))}):")
    for city, count in sorted(cities_by_type["concluidas"].items()):
        print(f"  {city}: {count}")

    print(f"\nCorridas Canceladas ({len(data.get('canceladas', []))}):")
    for city, count in sorted(cities_by_type["canceladas"].items(), key=lambda x: (x[0] is None, x[0] or "")):
        city_name = city if city is not None else "N/A"
        print(f"  {city_name}: {count}")

    print(f"\nCorridas Perdidas ({len(data.get('perdidas', []))}):")
    for city, count in sorted(cities_by_type["perdidas"].items(), key=lambda x: (x[0] is None, x[0] or "")):
        city_name = city if city is not None else "N/A"
        print(f"  {city_name}: {count}")

    # Verificar cidades alvo
    target_cities = ["MATUPA", "PEIXOTO DE AZEVEDO", "NOVA MONTE VERDE", "GUARANTA DO NORTE", "NOVA BANDEIRANTES"]

    print("\n=== VERIFICAÇÃO DAS CIDADES ALVO ===")
    for target in target_cities:
        found_completed = target in cities_by_type["concluidas"]
        found_cancelled = target in cities_by_type["canceladas"]
        found_missed = target in cities_by_type["perdidas"]

        print(f"\n{target}:")
        print(f"  Concluídas: {found_completed} ({cities_by_type['concluidas'].get(target, 0)})")
        print(f"  Canceladas: {found_cancelled} ({cities_by_type['canceladas'].get(target, 0)})")
        print(f"  Perdidas: {found_missed} ({cities_by_type['perdidas'].get(target, 0)})")

if __name__ == "__main__":
    analyze_api_cities()