"""
🔍 INVESTIGAÇÃO VIA API - Corridas de Passageiros
Usando os endpoints existentes para investigar a discrepância
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("="*100)
print("🔍 INVESTIGAÇÃO: CORRIDAS DE PASSAGEIROS - Análise via API")
print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d')}")
print("="*100)
print()

# =========================================================================
# 1. OBTER DADOS DO METRICS OVERVIEW (FONTE DA VERDADE)
# =========================================================================
print("1️⃣  DADOS DO METRICS OVERVIEW (Fonte da Verdade)")
print("-"*100)

resp_metrics = requests.get(f"{BASE_URL}/api/metrics/overview", params={"periodo": "hoje"})
metrics_data = resp_metrics.json()

concluidas = metrics_data.get('concluidas', [])
canceladas = metrics_data.get('canceladas', [])
perdidas = metrics_data.get('perdidas', [])

total_corridas = len(concluidas) + len(canceladas) + len(perdidas)

print(f"📊 Total de corridas HOJE: {total_corridas}")
print(f"   ✅ Concluídas: {len(concluidas)}")
print(f"   ❌ Canceladas: {len(canceladas)}")
print(f"   ⏱️  Perdidas: {len(perdidas)}")
print()

# Extrair passenger_ids das corridas
passenger_ids_from_metrics = set()

print("📋 Passageiros das corridas de HOJE:")
print()

for corrida in concluidas + canceladas + perdidas:
    passenger_id = corrida.get('passenger_id')
    passenger_name = corrida.get('passenger_name', 'N/A')
    if passenger_id:
        passenger_ids_from_metrics.add(passenger_id)

print(f"👥 Total de passageiros únicos nas {total_corridas} corridas: {len(passenger_ids_from_metrics)}")
print()

# Amostra dos passageiros
if passenger_ids_from_metrics:
    print("Amostra de passenger_ids:")
    for i, pid in enumerate(list(passenger_ids_from_metrics)[:5], 1):
        print(f"   {i}. {pid}")
    if len(passenger_ids_from_metrics) > 5:
        print(f"   ... e mais {len(passenger_ids_from_metrics) - 5}")
print()

# =========================================================================
# 2. OBTER DADOS DO PASSENGERS KPIs
# =========================================================================
print("\n2️⃣  DADOS DO PASSENGERS KPIs")
print("-"*100)

resp_passengers = requests.get(f"{BASE_URL}/api/passengers/kpis", params={"period": "today", "city": "all"})
passengers_data = resp_passengers.json()

print(f"📊 Total Passengers: {passengers_data.get('total_passengers')}")
print(f"📊 Total Rides: {passengers_data.get('total_rides')}")
print(f"💰 Total Revenue: R$ {passengers_data.get('total_revenue', 0):.2f}")
print()

# =========================================================================
# 3. OBTER LISTA DE PASSAGEIROS
# =========================================================================
print("\n3️⃣  LISTA DE PASSAGEIROS")
print("-"*100)

resp_list = requests.get(f"{BASE_URL}/api/passengers/list", params={"period": "today", "city": "all", "limit": 1000})
passengers_list = resp_list.json()

print(f"📊 Total de passageiros na lista: {len(passengers_list)}")
print()

if len(passengers_list) > 0:
    print("📋 Amostra dos primeiros 5 passageiros:")
    print(f"{'Passenger ID':<15} | {'Nome':<25} | {'Total Rides':<12} | {'Status':<10}")
    print("-"*80)
    
    for p in passengers_list[:5]:
        print(f"{p.get('passenger_id', 'N/A'):<15} | {p.get('user_name', 'N/A')[:25]:<25} | {p.get('total_rides', 0):<12} | {p.get('status', 'N/A'):<10}")
    
    print()

# =========================================================================
# 4. ANÁLISE CRUZADA - Verificar se passageiros das corridas estão na lista
# =========================================================================
print("\n4️⃣  ANÁLISE CRUZADA")
print("-"*100)

passenger_ids_from_list = {p.get('passenger_id') for p in passengers_list if p.get('passenger_id')}

print(f"Passageiros únicos nas corridas de HOJE (metrics): {len(passenger_ids_from_metrics)}")
print(f"Passageiros na lista (passengers/list): {len(passenger_ids_from_list)}")
print()

# Verificar interseção
in_both = passenger_ids_from_metrics & passenger_ids_from_list
only_in_metrics = passenger_ids_from_metrics - passenger_ids_from_list
only_in_list = passenger_ids_from_list - passenger_ids_from_metrics

print(f"✅ Passageiros que estão em AMBOS: {len(in_both)}")
print(f"⚠️  Passageiros apenas em CORRIDAS: {len(only_in_metrics)}")
print(f"⚠️  Passageiros apenas na LISTA: {len(only_in_list)}")
print()

if only_in_metrics:
    print("❌ Passageiros das corridas de HOJE que NÃO estão na lista de passageiros:")
    for pid in list(only_in_metrics)[:10]:
        print(f"   • {pid}")
    if len(only_in_metrics) > 10:
        print(f"   ... e mais {len(only_in_metrics) - 10}")
    print()

# =========================================================================
# 5. ANÁLISE DO PROBLEMA
# =========================================================================
print("\n" + "="*100)
print("🎯 ANÁLISE DO PROBLEMA")
print("="*100)
print()

print("📊 COMPARAÇÃO NUMÉRICA:")
print(f"   • Corridas no metrics/overview: {total_corridas}")
print(f"   • Corridas no passengers/kpis: {passengers_data.get('total_rides')}")
print(f"   • Diferença: {abs(total_corridas - passengers_data.get('total_rides', 0))}")
print()

print("🔍 POSSÍVEIS CAUSAS DA DISCREPÂNCIA:")
print()

# Verificar se passengers/kpis está filtrando por cadastro
if passengers_data.get('total_rides', 0) < total_corridas:
    print("1️⃣  FILTRO DE DATA INCORRETO")
    print("   ❌ O endpoint passengers/kpis provavelmente filtra por 'created_at' do PASSAGEIRO")
    print("   ❌ Deveria filtrar por 'created_at' da CORRIDA")
    print(f"   ℹ️  Está retornando apenas {passengers_data.get('total_rides')} corridas de {passengers_data.get('total_passengers')} passageiros cadastrados HOJE")
    print()
    
if len(only_in_metrics) > 0:
    print("2️⃣  PASSAGEIROS NÃO CADASTRADOS NA TABELA passenger_personal_details")
    print(f"   ❌ {len(only_in_metrics)} passageiros das corridas de hoje não estão cadastrados")
    print("   💡 Possível causa: Sincronização entre rides_data e passenger_personal_details")
    print()

# =========================================================================
# 6. VERIFICAR ENDPOINT DO BACKEND PASSENGERS.PY
# =========================================================================
print("\n" + "="*100)
print("💡 SOLUÇÃO SUGERIDA")
print("="*100)
print()

print("📝 O endpoint /api/passengers/kpis precisa ser corrigido:")
print()
print("❌ LÓGICA ATUAL (INCORRETA):")
print("   SELECT ... FROM passenger_personal_details")
print("   WHERE created_at::date = CURRENT_DATE  ← Filtra CADASTRO do passageiro")
print()
print("✅ LÓGICA CORRETA:")
print("   SELECT ... FROM passenger_personal_details ppd,")
print("   LATERAL jsonb_array_elements(ppd.rides_history) as ride")
print("   WHERE (ride->>'created_at')::date = CURRENT_DATE  ← Filtra DATA DA CORRIDA")
print()

# Salvar relatório
relatorio = {
    "timestamp": datetime.now().isoformat(),
    "total_corridas_metrics": total_corridas,
    "total_corridas_passengers_kpis": passengers_data.get('total_rides'),
    "discrepancia": total_corridas - passengers_data.get('total_rides', 0),
    "passenger_ids_metrics": list(passenger_ids_from_metrics),
    "passenger_ids_list": list(passenger_ids_from_list),
    "passageiros_ausentes": list(only_in_metrics),
    "conclusao": "Endpoint passengers/kpis filtra por data de cadastro, não data da corrida"
}

with open("investigacao_passageiros_api.json", 'w', encoding='utf-8') as f:
    json.dump(relatorio, f, indent=2, ensure_ascii=False)

print("💾 Relatório detalhado salvo em: investigacao_passageiros_api.json")
print()
print("="*100)
print("✨ Investigação concluída!")
print("="*100)
