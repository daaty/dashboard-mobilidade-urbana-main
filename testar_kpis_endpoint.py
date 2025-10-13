"""
🔍 TESTAR O ENDPOINT /api/passengers/kpis
Esse é o endpoint que o frontend usa para mostrar "Total de Passageiros"
"""

import requests

BASE_URL = "http://localhost:8000"

print("="*100)
print("🔍 TESTANDO ENDPOINT /api/passengers/kpis")
print("="*100)
print()

# Testar com diferentes períodos
periods = ['today', '7_days', '30_days', '3_months', '6_months', '12_months']

for period in periods:
    print(f"📍 Período: {period}")
    print()
    
    resp = requests.get(f"{BASE_URL}/api/passengers/kpis?period={period}", timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        
        print(f"  ✅ Total de Passageiros: {data.get('total_passengers')}")
        print(f"  ✅ Passageiros Ativos: {data.get('active_passengers')}")
        print(f"  📊 Total de Corridas: {data.get('total_rides')}")
        print(f"  💵 Receita Total: R$ {data.get('total_revenue', 0):.2f}")
        print(f"  ⭐ Média de Avaliação: {data.get('avg_rating', 0):.2f}")
        print(f"  🏙️  Total de Cidades: {data.get('cities_count')}")
        print(f"  📅 Registrados este mês: {data.get('registered_this_month')}")
        print(f"  🚫 Bloqueados: {data.get('blocked_passengers')}")
        print()
    else:
        print(f"  ❌ Erro HTTP {resp.status_code}")
        print()
    
    print("-"*100)
    print()

print("="*100)
print("🎯 COMPARAÇÃO")
print("="*100)
print()
print("Banco de dados: 304 passageiros únicos")
print("API /api/passengers/list (limit=1000): 304 passageiros")
print()
print("Vamos ver o que o /api/passengers/kpis retorna em cada período...")
print()
