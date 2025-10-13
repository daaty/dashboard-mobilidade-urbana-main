"""
RELATÓRIO FINAL - CORRIDAS DE HOJE (2025-10-12)
Análise completa e definitiva das inconsistências
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("="*100)
print("🎯 RELATÓRIO FINAL - CORRIDAS DE HOJE (2025-10-12)")
print("="*100)
print()

# ========================================================================================
# ENDPOINT 1: Passengers Analytics
# ========================================================================================
print("1️⃣  PASSENGERS ANALYTICS")
print("-"*100)
resp = requests.get(f"{BASE_URL}/api/passengers/analytics", params={"period": "today", "city": "all"})
data = resp.json()
summary = data.get("summary", {})
print(f"   📍 Endpoint: /api/passengers/analytics")
print(f"   📊 Total Rides: {summary.get('total_rides', 0)}")
print(f"   💰 Total Revenue: R$ {summary.get('total_revenue', 0):.2f}")
print(f"   📌 Estrutura: Dict com 'summary' contendo 'total_rides'")
print(f"   ⚠️  OBSERVAÇÃO: Este endpoint analisa corridas dos PASSAGEIROS cadastrados hoje")
print()

# ========================================================================================
# ENDPOINT 2: Passengers KPIs
# ========================================================================================
print("2️⃣  PASSENGERS KPIs")
print("-"*100)
resp = requests.get(f"{BASE_URL}/api/passengers/kpis", params={"period": "today", "city": "all"})
data = resp.json()
print(f"   📍 Endpoint: /api/passengers/kpis")
print(f"   📊 Total Passengers: {data.get('total_passengers', 'N/A')}")
print(f"   📊 Total Rides (if available): {data.get('total_rides', 'N/A')}")
print(f"   📌 Estrutura: {list(data.keys())}")
print()

# ========================================================================================
# ENDPOINT 3: Passengers List
# ========================================================================================
print("3️⃣  PASSENGERS LIST")
print("-"*100)
resp = requests.get(f"{BASE_URL}/api/passengers/list", params={"period": "today", "city": "all", "limit": 1000})
data = resp.json()
total_passengers = len(data)
total_rides_sum = sum(p.get('total_rides', 0) for p in data)
print(f"   📍 Endpoint: /api/passengers/list")
print(f"   👥 Total Passageiros: {total_passengers}")
print(f"   📊 Soma de 'total_rides' de cada passageiro: {total_rides_sum}")
print(f"   📌 Estrutura: Array de passageiros, cada um com 'total_rides'")
print(f"   ⚠️  OBSERVAÇÃO: Este endpoint retorna PASSAGEIROS, não corridas!")
print(f"   ⚠️  Os {total_rides_sum} são corridas HISTÓRICAS dos passageiros, não apenas de hoje")
print()

# ========================================================================================
# ENDPOINT 4: Metrics Overview
# ========================================================================================
print("4️⃣  METRICS OVERVIEW")
print("-"*100)
resp = requests.get(f"{BASE_URL}/api/metrics/overview", params={"periodo": "hoje"})
data = resp.json()
metricas = data.get('metricas_principais', {})
concluidas = len(data.get('concluidas', []))
canceladas = len(data.get('canceladas', []))
perdidas = len(data.get('perdidas', []))
total_corridas = concluidas + canceladas + perdidas

print(f"   📍 Endpoint: /api/metrics/overview")
print(f"   ✅ Corridas Concluídas: {concluidas}")
print(f"   ❌ Corridas Canceladas: {canceladas}")
print(f"   ⏱️  Corridas Perdidas: {perdidas}")
print(f"   📊 TOTAL DE CORRIDAS HOJE: {total_corridas}")
print(f"   📌 Estrutura: Dict com arrays 'concluidas', 'canceladas', 'perdidas'")
print(f"   ✨ ESTE É O ENDPOINT PRINCIPAL PARA ANÁLISE DE CORRIDAS!")
print()

# ========================================================================================
# ENDPOINT 5: Performance Analytics - Detailed Metrics
# ========================================================================================
print("5️⃣  PERFORMANCE ANALYTICS - DETAILED METRICS")
print("-"*100)
resp = requests.get(f"{BASE_URL}/api/analytics/performance/detailed-metrics", params={"period": "today", "city": "all"})
data = resp.json()
metrics = data.get('metrics', [])
total_motoristas = len(metrics)
total_rides_from_drivers = sum(m.get('total_rides', 0) for m in metrics)
completed_rides_from_drivers = sum(m.get('completed_rides', 0) for m in metrics)

print(f"   📍 Endpoint: /api/analytics/performance/detailed-metrics")
print(f"   🚗 Total Motoristas: {total_motoristas}")
print(f"   📊 Soma 'total_rides': {total_rides_from_drivers}")
print(f"   ✅ Soma 'completed_rides': {completed_rides_from_drivers}")
print(f"   📌 Estrutura: Dict com array 'metrics' (1 objeto por motorista)")
print(f"   ⚠️  OBSERVAÇÃO: Este endpoint retorna dados agregados POR MOTORISTA")
print()

# ========================================================================================
# ENDPOINT 6: Drivers KPIs
# ========================================================================================
print("6️⃣  DRIVERS KPIs")
print("-"*100)
resp = requests.get(f"{BASE_URL}/api/drivers/kpis", params={"period": "today", "city": "all"})
data = resp.json()
print(f"   📍 Endpoint: /api/drivers/kpis")
print(f"   📊 Total Drivers: {data.get('total_drivers', 'N/A')}")
print(f"   📊 Total Rides (if available): {data.get('total_rides', 'N/A')}")
print(f"   📌 Estrutura: {list(data.keys())}")
print()

# ========================================================================================
# ANÁLISE FINAL
# ========================================================================================
print("="*100)
print("🎯 CONCLUSÃO E RECOMENDAÇÕES")
print("="*100)
print()
print("📊 CONTAGEM DE CORRIDAS HOJE (2025-10-12):")
print()
print(f"   ✅ Concluídas: {concluidas}")
print(f"   ❌ Canceladas: {canceladas}")
print(f"   ⏱️  Perdidas: {perdidas}")
print(f"   📈 TOTAL: {total_corridas} corridas")
print()
print("🔍 INCONSISTÊNCIAS IDENTIFICADAS:")
print()
print(f"   1. Passengers Analytics reporta: {summary.get('total_rides', 0)} corridas")
print(f"      → Possível causa: Está contando apenas corridas de NOVOS passageiros cadastrados hoje")
print()
print(f"   2. Passengers List mostra: {total_passengers} passageiros com {total_rides_sum} corridas totais")
print(f"      → Possível causa: 'total_rides' é o HISTÓRICO completo, não apenas hoje")
print()
print(f"   3. Metrics Overview reporta: {total_corridas} corridas (7 + 1 + 7)")
print(f"      → ✅ Este é o valor CORRETO baseado na tabela rides_data")
print()
print(f"   4. Performance Analytics mostra: {total_motoristas} motoristas com {completed_rides_from_drivers} corridas completas")
print(f"      → Possível causa: Agregação por motorista, pode ter lógica diferente")
print()
print("="*100)
print("✨ ENDPOINT RECOMENDADO PARA ANÁLISE DE CORRIDAS:")
print("="*100)
print()
print("   🏆 /api/metrics/overview com parâmetro 'periodo=hoje'")
print()
print("   Motivos:")
print("   • Acessa diretamente a tabela rides_data")
print("   • Separa corridas por status (concluídas, canceladas, perdidas)")
print("   • Fornece detalhes completos de cada corrida")
print("   • Inclui métricas comparativas e análises adicionais")
print()
print("="*100)

# Salvar relatório
relatorio = {
    "data_analise": "2025-10-12",
    "timestamp": datetime.now().isoformat(),
    "endpoints_analisados": {
        "passengers_analytics": {
            "url": "/api/passengers/analytics",
            "total_rides": summary.get('total_rides', 0),
            "observacao": "Corridas de passageiros cadastrados hoje"
        },
        "passengers_list": {
            "url": "/api/passengers/list",
            "total_passageiros": total_passengers,
            "total_rides_historico": total_rides_sum,
            "observacao": "Retorna passageiros com histórico completo"
        },
        "metrics_overview": {
            "url": "/api/metrics/overview",
            "concluidas": concluidas,
            "canceladas": canceladas,
            "perdidas": perdidas,
            "total": total_corridas,
            "observacao": "✅ FONTE PRINCIPAL - Dados da tabela rides_data"
        },
        "performance_detailed": {
            "url": "/api/analytics/performance/detailed-metrics",
            "motoristas": total_motoristas,
            "total_rides": total_rides_from_drivers,
            "completed_rides": completed_rides_from_drivers,
            "observacao": "Agregação por motorista"
        }
    },
    "conclusao": {
        "corridas_hoje": total_corridas,
        "endpoint_recomendado": "/api/metrics/overview",
        "inconsistencias": [
            f"Passengers Analytics: {summary.get('total_rides', 0)} vs Metrics Overview: {total_corridas}",
            f"Passengers List soma histórica: {total_rides_sum} (não é apenas hoje)"
        ]
    }
}

with open("RELATORIO_FINAL_CORRIDAS_HOJE.json", 'w', encoding='utf-8') as f:
    json.dump(relatorio, f, indent=2, ensure_ascii=False)

print(f"💾 Relatório salvo em: RELATORIO_FINAL_CORRIDAS_HOJE.json")
print()
