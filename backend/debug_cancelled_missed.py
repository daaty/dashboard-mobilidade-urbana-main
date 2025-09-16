#!/usr/bin/env python3
import requests
import json

def debug_cancelled_missed_rides():
    """Debug dos registros de corridas canceladas e perdidas"""
    response = requests.get('http://localhost:8000/api/metrics/overview?periodo=30d')
    data = response.json()

    print("=== DEBUG CORRIDAS CANCELADAS ===")
    cancelled_rides = data.get('canceladas', [])
    print(f"Total de corridas canceladas: {len(cancelled_rides)}")

    for i, ride in enumerate(cancelled_rides[:5]):  # Mostrar apenas as primeiras 5
        print(f"\nCancelada {i+1}:")
        print(f"  ID: {ride.get('id_corrida')}")
        print(f"  Cidade: {ride.get('cidade')}")
        print(f"  Local: {ride.get('local')}")
        print(f"  Destino: {ride.get('destino')}")
        print(f"  Grupo: {ride.get('grupo')}")

    print("\n=== DEBUG CORRIDAS PERDIDAS ===")
    missed_rides = data.get('perdidas', [])
    print(f"Total de corridas perdidas: {len(missed_rides)}")

    for i, ride in enumerate(missed_rides[:5]):  # Mostrar apenas as primeiras 5
        print(f"\nPerdida {i+1}:")
        print(f"  ID: {ride.get('id_corrida')}")
        print(f"  Cidade: {ride.get('cidade')}")
        print(f"  Local: {ride.get('local')}")
        print(f"  Grupo: {ride.get('grupo')}")

if __name__ == "__main__":
    debug_cancelled_missed_rides()