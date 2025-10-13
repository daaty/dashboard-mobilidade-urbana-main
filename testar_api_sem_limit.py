"""
🔍 BUSCAR TODOS OS PASSAGEIROS DA API (SEM LIMIT)
"""

import requests

BASE_URL = "http://localhost:8000"

print("="*100)
print("🔍 BUSCANDO TODOS OS PASSAGEIROS DA API")
print("="*100)
print()

# Testar com limit=1000 para pegar todos
print("📍 Endpoint: /api/passengers/list?limit=1000")
print()

resp = requests.get(f"{BASE_URL}/api/passengers/list?limit=1000", timeout=30)

if resp.status_code == 200:
    passengers = resp.json()
    
    print(f"✅ Total de passageiros retornados: {len(passengers)}")
    print()
    
    # Contar por status
    ativos = sum(1 for p in passengers if p.get('status') == 'Ativo')
    bloqueados = sum(1 for p in passengers if p.get('status') == 'Bloqueado')
    
    # Contar por cidade
    cities = {}
    for p in passengers:
        city = p.get('city', 'N/A')
        cities[city] = cities.get(city, 0) + 1
    
    # Contar com/sem corridas
    with_rides = sum(1 for p in passengers if p.get('total_rides', 0) > 0)
    without_rides = sum(1 for p in passengers if p.get('total_rides', 0) == 0)
    
    print("="*100)
    print("📊 ESTATÍSTICAS")
    print("="*100)
    print()
    print(f"✅ Passageiros ATIVOS: {ativos}")
    print(f"❌ Passageiros BLOQUEADOS: {bloqueados}")
    print()
    print(f"✅ Com corridas: {with_rides}")
    print(f"❌ Sem corridas: {without_rides}")
    print()
    
    print("🏙️  DISTRIBUIÇÃO POR CIDADE:")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
        print(f"   {city}: {count}")
    print()
    print(f"📊 Total de cidades: {len(cities)}")
    print()
    
    print("="*100)
    print("🎯 COMPARAÇÃO")
    print("="*100)
    print()
    print(f"Banco de dados: 304 passageiros")
    print(f"API retorna: {len(passengers)} passageiros")
    print()
    
    if len(passengers) < 304:
        diff = 304 - len(passengers)
        print(f"⚠️  FALTAM {diff} passageiros!")
    elif len(passengers) == 304:
        print("✅ PERFEITO! Todos os passageiros estão sendo retornados!")
    else:
        print(f"⚠️  API retorna MAIS passageiros ({len(passengers)}) do que o banco (304)!")
    print()

else:
    print(f"❌ Erro HTTP {resp.status_code}")
    print(resp.text)
