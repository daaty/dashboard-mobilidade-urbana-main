"""
🔍 TESTAR OS 5 PASSAGEIROS QUE VOCÊ ENCONTROU
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Os 5 passageiros que você encontrou no banco
PASSENGER_IDS = [
    "18765654",
    "18811933", 
    "18950699",
    "19197368",
    "19255623"
]

print("="*100)
print("🔍 TESTANDO OS 5 PASSAGEIROS COM CORRIDAS DE HOJE")
print("="*100)
print()

total_rides_found = 0
passengers_with_data = 0
passengers_without_data = 0

for pid in PASSENGER_IDS:
    print(f"📍 Passageiro: {pid}")
    
    try:
        resp = requests.get(f"{BASE_URL}/api/passengers/{pid}", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            rides = data.get('rides_details', [])
            
            # Filtrar corridas de hoje
            today = datetime.now().strftime("%d/%m/%Y")
            rides_today = [r for r in rides if r.get('date', '').startswith(today)]
            
            if rides_today:
                print(f"  ✅ {len(rides_today)} corrida(s) de HOJE encontrada(s)!")
                passengers_with_data += 1
                total_rides_found += len(rides_today)
                
                for ride in rides_today:
                    print(f"     - {ride.get('date')} | R$ {ride.get('user_fare')} | {ride.get('driver_name')}")
            else:
                if rides:
                    print(f"  ⚠️  {len(rides)} corrida(s) encontrada(s), mas NENHUMA de hoje")
                    print(f"     Última corrida: {rides[0].get('date')}")
                else:
                    print(f"  ❌ Nenhuma corrida encontrada")
                passengers_without_data += 1
        else:
            print(f"  ❌ Erro HTTP {resp.status_code}")
            passengers_without_data += 1
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        passengers_without_data += 1
    
    print()

print("="*100)
print("📊 RESUMO FINAL")
print("="*100)
print()
print(f"✅ Passageiros com corridas de HOJE: {passengers_with_data}/{len(PASSENGER_IDS)}")
print(f"❌ Passageiros sem corridas de hoje: {passengers_without_data}/{len(PASSENGER_IDS)}")
print(f"📊 Total de corridas de HOJE encontradas: {total_rides_found}")
print()
print("="*100)
print("🎯 CONCLUSÃO")
print("="*100)
print()
print(f"Se encontramos {total_rides_found} corridas nesses 5 passageiros,")
print("mas o dashboard mostra 15 corridas no total,")
print(f"significa que faltam {15 - total_rides_found} corridas em OUTROS passageiros!")
print()
