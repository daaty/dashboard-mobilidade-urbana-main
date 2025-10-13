"""
🔍 BUSCAR PASSENGER_IDS DAS CORRIDAS DE HOJE VIA API
Comparar com quais passageiros existem
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("="*100)
print("🔍 BUSCANDO TODAS AS CORRIDAS DE HOJE")
print("="*100)
print()

# 1. Buscar todas as corridas de hoje via /api/metrics/overview
try:
    resp = requests.get(f"{BASE_URL}/api/metrics/overview", timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        
        # Extrair dados das corridas de hoje
        today_data = data.get('today', {})
        total_rides = today_data.get('total_rides', 0)
        
        print(f"✅ Total de corridas de HOJE: {total_rides}")
        print()
        
        # Pegar detalhes das corridas
        rides_details = data.get('rides_details', [])
        
        if not rides_details:
            print("⚠️  Endpoint não retorna rides_details")
            print("Vou tentar buscar via endpoint de listagem de passageiros...")
            print()
            
            # Buscar lista de passageiros
            resp2 = requests.get(f"{BASE_URL}/api/passengers/list", timeout=30)
            
            if resp2.status_code == 200:
                passengers_list = resp2.json()
                print(f"✅ Total de passageiros na tabela: {len(passengers_list)}")
                print()
                
                # Testar cada passageiro para ver quem tem corridas de hoje
                today_str = datetime.now().strftime("%d/%m/%Y")
                passengers_with_rides_today = []
                total_rides_found = 0
                
                print("🔍 Testando cada passageiro para encontrar corridas de hoje...")
                print()
                
                for i, passenger in enumerate(passengers_list, 1):
                    p_id = passenger.get('passenger_id')
                    
                    if i % 10 == 0:
                        print(f"   Testados: {i}/{len(passengers_list)}...", end='\r')
                    
                    try:
                        resp3 = requests.get(f"{BASE_URL}/api/passengers/{p_id}", timeout=5)
                        
                        if resp3.status_code == 200:
                            p_data = resp3.json()
                            rides = p_data.get('rides_details', [])
                            
                            # Filtrar corridas de hoje
                            rides_today = [r for r in rides if r.get('date', '').startswith(today_str)]
                            
                            if rides_today:
                                passengers_with_rides_today.append({
                                    'passenger_id': p_id,
                                    'name': p_data.get('personal_info', {}).get('user_name', 'N/A'),
                                    'city': p_data.get('city', 'N/A'),
                                    'rides_today': rides_today
                                })
                                total_rides_found += len(rides_today)
                    except:
                        pass
                
                print(" " * 50, end='\r')  # Limpar linha
                print()
                print("="*100)
                print("📊 RESULTADOS")
                print("="*100)
                print()
                print(f"✅ Passageiros com corridas de HOJE: {len(passengers_with_rides_today)}")
                print(f"📊 Total de corridas de HOJE encontradas: {total_rides_found}")
                print()
                
                if passengers_with_rides_today:
                    print("="*100)
                    print("📋 DETALHES DOS PASSAGEIROS COM CORRIDAS DE HOJE")
                    print("="*100)
                    print()
                    
                    for p_data in passengers_with_rides_today:
                        p_id = p_data['passenger_id']
                        name = p_data['name']
                        city = p_data['city']
                        rides = p_data['rides_today']
                        
                        total_valor = sum(float(r.get('user_fare', 0)) for r in rides)
                        
                        print(f"✅ Passageiro: {p_id} - {name} ({city})")
                        print(f"   Corridas hoje: {len(rides)}")
                        print(f"   Valor total: R$ {total_valor:.2f}")
                        
                        for i, ride in enumerate(rides, 1):
                            print(f"      {i}. {ride.get('date')} | R$ {ride.get('user_fare')} | {ride.get('driver_name')}")
                        print()
                    
                    print("="*100)
                    print("🎯 CONCLUSÃO")
                    print("="*100)
                    print()
                    print(f"Encontramos {total_rides_found} corridas em {len(passengers_with_rides_today)} passageiros")
                    print(f"O endpoint /api/metrics/overview mostra {total_rides} corridas")
                    print()
                    
                    if total_rides_found < total_rides:
                        missing = total_rides - total_rides_found
                        print(f"⚠️  FALTAM {missing} corridas!")
                        print(f"Isso significa que {missing} corridas estão em passageiros que NÃO existem na tabela!")
                    elif total_rides_found == total_rides:
                        print("✅ Todas as corridas foram encontradas!")
                    else:
                        print(f"⚠️  Encontramos MAIS corridas ({total_rides_found}) do que o esperado ({total_rides})!")
                    print()
                
    else:
        print(f"❌ Erro HTTP {resp.status_code}")
        print(resp.text)
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print()
