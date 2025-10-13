"""
🔍 TESTE DIRETO - Buscar passageiro específico que TEM dados
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# ID do passageiro que VOCÊ VIU que tem rides_history no banco
# Substitua pelo ID correto
PASSENGER_ID = "18765654"  # Este é um dos 5 que você mencionou

print("="*100)
print(f"🔍 TESTANDO PASSAGEIRO: {PASSENGER_ID}")
print("="*100)
print()

# Testar endpoint direto
print(f"📍 Endpoint: /api/passengers/{PASSENGER_ID}")
print()

try:
    resp = requests.get(f"{BASE_URL}/api/passengers/{PASSENGER_ID}", timeout=30)
    
    print(f"Status: {resp.status_code}")
    print()
    
    if resp.status_code == 200:
        data = resp.json()
        
        print("✅ RESPOSTA RECEBIDA!")
        print()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
        
        # Verificar rides
        rides_details = data.get('rides_details', [])
        rides_summary = data.get('rides_summary', {})
        
        print("="*100)
        print("📊 ANÁLISE")
        print("="*100)
        print()
        print(f"Total de corridas (summary): {rides_summary.get('total_rides', 0)}")
        print(f"Total de corridas (details): {len(rides_details)}")
        print()
        
        if rides_details:
            print("✅ RIDES_DETAILS TEM DADOS!")
            print()
            for i, ride in enumerate(rides_details, 1):
                print(f"Corrida {i}:")
                print(f"  Data: {ride.get('date')}")
                print(f"  Valor: R$ {ride.get('user_fare')}")
                print(f"  Motorista: {ride.get('driver_name')}")
                print()
        else:
            print("❌ RIDES_DETAILS ESTÁ VAZIO!")
            print()
            print("Mas você viu no banco que TEM dados...")
            print("Isso significa que a query SQL não está retornando o rides_history!")
    else:
        print(f"❌ Erro HTTP {resp.status_code}")
        print(resp.text)
        
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("="*100)
print("💡 PRÓXIMO PASSO")
print("="*100)
print()
print("Se rides_details está vazio mas você VIU no banco que tem dados,")
print("então confirme qual é o passenger_id EXATO que tem a corrida:")
print()
print('rides_history = [{"date":"12/10/2025 12:21 pm",...}]')
print()
print("E me passe o passenger_id correto para testarmos!")
print()
