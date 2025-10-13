"""
🔍 ANÁLISE DETALHADA - Passageiros Específicos
Verificar rides_history dos 5 passageiros encontrados
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# IDs dos passageiros encontrados
PASSENGER_IDS = [
    "18756583",
    "18756825",
    "18762196",
    "18765654",
    "18766423"
]

print("="*100)
print("🔍 ANÁLISE DETALHADA - PASSAGEIROS ESPECÍFICOS")
print(f"📅 Data de HOJE: {datetime.now().strftime('%d/%m/%Y')}")
print("="*100)
print()

print(f"👥 Analisando {len(PASSENGER_IDS)} passageiros:")
for pid in PASSENGER_IDS:
    print(f"   • {pid}")
print()

# Obter todos os passageiros para filtrar os específicos
print("1️⃣  Obtendo dados dos passageiros...")
print("-"*100)

resp = requests.get(f"{BASE_URL}/api/passengers/list", params={"period": "all_time", "city": "all", "limit": 10000})
all_passengers = resp.json()

# Filtrar apenas os IDs específicos
passengers_found = [p for p in all_passengers if p.get('passenger_id') in PASSENGER_IDS]

print(f"📊 Passageiros encontrados: {len(passengers_found)}/{len(PASSENGER_IDS)}")
print()

if len(passengers_found) < len(PASSENGER_IDS):
    missing = set(PASSENGER_IDS) - {p.get('passenger_id') for p in passengers_found}
    print(f"⚠️  Passageiros NÃO encontrados: {missing}")
    print()

# Analisar cada passageiro
for passenger in passengers_found:
    pid = passenger.get('passenger_id')
    name = passenger.get('user_name', 'N/A')
    total_rides = passenger.get('total_rides', 0)
    
    print("="*100)
    print(f"👤 PASSAGEIRO: {name} (ID: {pid})")
    print("="*100)
    print()
    
    print(f"📊 Total de corridas (histórico): {total_rides}")
    print(f"💰 Total gasto: R$ {passenger.get('total_spent', 0):.2f}")
    print(f"⭐ Avaliação média: {passenger.get('avg_rating', 0)}")
    print(f"🏙️  Cidade: {passenger.get('city', 'N/A')}")
    print(f"📅 Data registro: {passenger.get('date_registered', 'N/A')}")
    print(f"📱 Dispositivo: {passenger.get('device_type', 'N/A')}")
    print()
    
    # Tentar obter dados detalhados via endpoint individual
    try:
        resp_detail = requests.get(f"{BASE_URL}/api/passengers/{pid}", timeout=10)
        if resp_detail.status_code == 200:
            detail = resp_detail.json()
            
            print("📋 DADOS DETALHADOS:")
            print()
            
            # Verificar se tem rides_history
            rides_history = detail.get('rides_history', [])
            
            if rides_history:
                print(f"   📊 Total de corridas no rides_history: {len(rides_history)}")
                print()
                
                # Filtrar corridas de HOJE
                hoje = datetime.now().strftime('%d/%m/%Y')
                corridas_hoje = []
                
                for ride in rides_history:
                    ride_date = ride.get('date', '')
                    # Extrair apenas a data (sem hora)
                    if ' ' in ride_date:
                        ride_date = ride_date.split(' ')[0]
                    
                    if ride_date == hoje:
                        corridas_hoje.append(ride)
                
                print(f"   ✅ Corridas de HOJE ({hoje}): {len(corridas_hoje)}")
                print()
                
                if corridas_hoje:
                    print("   📋 DETALHES DAS CORRIDAS DE HOJE:")
                    print()
                    
                    for i, ride in enumerate(corridas_hoje, 1):
                        print(f"   Corrida {i}:")
                        print(f"      • Data/Hora: {ride.get('date', 'N/A')}")
                        print(f"      • Driver ID: {ride.get('driver_id', 'N/A')}")
                        print(f"      • Driver Nome: {ride.get('driver_name', 'N/A')}")
                        print(f"      • Valor: R$ {ride.get('user_fare', '0')}")
                        print(f"      • Distância: {ride.get('ride_distance', 'N/A')} km")
                        print(f"      • Avaliação: {ride.get('user_rating', 'N/A')}")
                        print(f"      • Tempo: {ride.get('ride_time', 'N/A')} min")
                        print(f"      • Engagement ID: {ride.get('engagement_id', 'N/A')}")
                        print()
                else:
                    print("   ❌ Nenhuma corrida de HOJE encontrada no rides_history")
                    print()
                
                # Mostrar as 3 últimas corridas do histórico
                print("   📋 ÚLTIMAS 3 CORRIDAS DO HISTÓRICO:")
                print()
                
                for i, ride in enumerate(rides_history[-3:], 1):
                    print(f"   Corrida {i}:")
                    print(f"      • Data: {ride.get('date', 'N/A')}")
                    print(f"      • Valor: R$ {ride.get('user_fare', '0')}")
                    print(f"      • Motorista: {ride.get('driver_name', 'N/A')}")
                    print()
            else:
                print("   ❌ rides_history está VAZIO!")
                print()
        else:
            print(f"   ⚠️  Não foi possível obter dados detalhados (HTTP {resp_detail.status_code})")
            print()
            
    except Exception as e:
        print(f"   ❌ Erro ao obter detalhes: {e}")
        print()

# RESUMO FINAL
print("\n" + "="*100)
print("📊 RESUMO FINAL")
print("="*100)
print()

# Contar total de corridas de hoje encontradas
resp_today = requests.get(f"{BASE_URL}/api/passengers/analytics", params={"period": "today", "city": "all"})
today_data = resp_today.json()
total_corridas_hoje = today_data.get('summary', {}).get('total_rides', 0)

print(f"📊 Total de corridas de HOJE no sistema (passengers/analytics): {total_corridas_hoje}")
print()

print("💡 CONCLUSÃO:")
print()
print("   Se esses 5 passageiros têm corridas registradas mas não aparecem nas corridas")
print("   de HOJE, então:")
print()
print("   1️⃣  As corridas existem no banco")
print("   2️⃣  MAS a data no rides_history NÃO é 12/10/2025")
print("   3️⃣  Ou o processo de sincronização ainda não aconteceu")
print()

print("="*100)
