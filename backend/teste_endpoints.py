#!/usr/bin/env python3
"""
Teste para identificar qual endpoint está sendo usado
"""
import requests

print("=== TESTANDO ENDPOINTS ===")
print()

# Testar Flask endpoint
print("1. Flask endpoint (/api/metrics/overview):")
try:
    response = requests.get('http://localhost:5000/api/metrics/overview?periodo=6m', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Total corridas: {data.get('total_corridas', 'N/A')}")
        print(f"   Concluidas: {data.get('corridas_concluidas', {}).get('total', 'N/A')}")
        print(f"   Canceladas: {data.get('corridas_canceladas', {}).get('total', 'N/A')}")
        print(f"   Perdidas: {data.get('corridas_perdidas', {}).get('total', 'N/A')}")
    else:
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   Erro: {e}")

print()

# Testar FastAPI endpoint
print("2. FastAPI endpoint (/api/metrics/overview):")
try:
    response = requests.get('http://localhost:8000/api/metrics/overview?periodo=6m', timeout=5)
    if response.status_code == 200:
        data = response.json()
        metricas = data.get('metricas_principais', {})
        print(f"   Status: {response.status_code}")
        total = metricas.get('corridas_concluidas', 0) + metricas.get('corridas_canceladas', 0) + metricas.get('corridas_perdidas', 0)
        print(f"   Total corridas: {total}")
        print(f"   Concluidas: {metricas.get('corridas_concluidas', 'N/A')}")
        print(f"   Canceladas: {metricas.get('corridas_canceladas', 'N/A')}")
        print(f"   Perdidas: {metricas.get('corridas_perdidas', 'N/A')}")
    else:
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   Erro: {e}")

print()
print("=== COMPARAÇÃO ===")
print("Se o frontend mostra 251 corridas totais, está usando o Flask endpoint")
print("Se o frontend mostra mais corridas, está usando o FastAPI endpoint")