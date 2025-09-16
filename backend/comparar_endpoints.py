#!/usr/bin/env python3
"""
Comparação detalhada entre os dois endpoints FastAPI
"""
import requests

print("=== COMPARAÇÃO DETALHADA DOS ENDPOINTS ===")
print()

# KPIs (FastAPI)
print("📊 KPIs - FastAPI /api/metrics/overview:")
try:
    response = requests.get('http://localhost:8000/api/metrics/overview?periodo=6m', timeout=10)
    if response.status_code == 200:
        data = response.json()
        metricas = data.get('metricas_principais', {})
        total_kpis = metricas.get('corridas_concluidas', 0) + metricas.get('corridas_canceladas', 0) + metricas.get('corridas_perdidas', 0)
        print(f"   Total: {total_kpis}")
        print(f"   Concluidas: {metricas.get('corridas_concluidas', 0)}")
        print(f"   Canceladas: {metricas.get('corridas_canceladas', 0)}")
        print(f"   Perdidas: {metricas.get('corridas_perdidas', 0)}")
except Exception as e:
    print(f"   Erro: {e}")

print()

# Mapa de Calor
print("🗺️ Mapa - FastAPI /api/mapa-calor-problemas:")
try:
    response = requests.get('http://localhost:8000/api/mapa-calor-problemas?periodo=6m', timeout=10)
    if response.status_code == 200:
        data = response.json()
        pontos = data.get('pontos', [])

        # Contar por status
        status_count = {}
        for ponto in pontos:
            status = ponto.get('status', 'desconhecido')
            status_count[status] = status_count.get(status, 0) + 1

        print(f"   Total pontos: {len(pontos)}")
        for status, count in status_count.items():
            print(f"   {status.title()}: {count}")

        print(f"   Concluidas: {status_count.get('concluida', 0)}")
        print(f"   Canceladas: {status_count.get('cancelada', 0)}")
        print(f"   Perdidas: {status_count.get('perdida', 0)}")

except Exception as e:
    print(f"   Erro: {e}")

print()
print("🎯 AMBOS OS ENDPOINTS USAM POSTGRESQL!")
print("🔍 O problema está na LÓGICA DE PROCESSAMENTO dos dados")
print()
print("📋 POSSÍVEIS CAUSAS:")
print("1. Filtros de período diferentes")
print("2. Lógica de deduplicação diferente")
print("3. Critérios de validação diferentes")
print("4. Processamento de datas diferente")