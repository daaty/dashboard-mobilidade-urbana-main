"""
🔍 BUSCAR TODOS OS PASSENGER_IDS DAS CORRIDAS DE HOJE
Direto na tabela rides_data
"""

import psycopg2
from datetime import datetime
import json

# Conectar ao banco
conn = psycopg2.connect(
    host="localhost",
    database="dashboard_mobilidade",
    user="postgres",
    password="mb123"
)

cur = conn.cursor()

# Data de hoje
today = datetime.now().date()

print("="*100)
print(f"🔍 BUSCANDO PASSENGER_IDS DAS CORRIDAS DE HOJE ({today})")
print("="*100)
print()

# Buscar todas as corridas de hoje
query = """
SELECT 
    passenger_id,
    driver_id,
    TO_CHAR(ride_timestamp, 'DD/MM/YYYY HH24:MI') as data_hora,
    user_fare,
    status,
    engagement_id
FROM rides_data
WHERE DATE(ride_timestamp) = %s
ORDER BY ride_timestamp DESC
"""

cur.execute(query, (today,))
rides = cur.fetchall()

print(f"✅ Total de corridas de HOJE: {len(rides)}")
print()

# Agrupar por passenger_id
passengers_rides = {}
for ride in rides:
    p_id = ride[0]
    if p_id not in passengers_rides:
        passengers_rides[p_id] = []
    passengers_rides[p_id].append({
        'driver_id': ride[1],
        'data_hora': ride[2],
        'valor': float(ride[3]) if ride[3] else 0,
        'status': ride[4],
        'engagement_id': ride[5]
    })

print(f"📊 Total de PASSAGEIROS distintos: {len(passengers_rides)}")
print()

# Agora verificar quais existem em passenger_personal_details
print("="*100)
print("🔍 VERIFICANDO QUAIS PASSAGEIROS EXISTEM NA TABELA passenger_personal_details")
print("="*100)
print()

passenger_ids = list(passengers_rides.keys())

query_check = """
SELECT passenger_id, 
       CASE WHEN rides_history IS NOT NULL THEN 'SIM' ELSE 'NAO' END as tem_rides_history
FROM passenger_personal_details
WHERE passenger_id = ANY(%s)
"""

cur.execute(query_check, (passenger_ids,))
existing_passengers = {row[0]: row[1] for row in cur.fetchall()}

# Mostrar resultados
passengers_found = 0
passengers_missing = 0

for p_id, rides_list in passengers_rides.items():
    num_rides = len(rides_list)
    total_valor = sum(r['valor'] for r in rides_list)
    
    if p_id in existing_passengers:
        has_rides_history = existing_passengers[p_id]
        print(f"✅ Passageiro {p_id}:")
        print(f"   - Existe na tabela: SIM")
        print(f"   - rides_history preenchido: {has_rides_history}")
        print(f"   - Corridas hoje: {num_rides}")
        print(f"   - Valor total: R$ {total_valor:.2f}")
        passengers_found += 1
    else:
        print(f"❌ Passageiro {p_id}:")
        print(f"   - Existe na tabela: NÃO")
        print(f"   - Corridas hoje: {num_rides}")
        print(f"   - Valor total: R$ {total_valor:.2f}")
        passengers_missing += 1
        
        # Mostrar detalhes das corridas
        for i, ride in enumerate(rides_list, 1):
            print(f"      {i}. {ride['data_hora']} | R$ {ride['valor']:.2f} | Status: {ride['status']}")
    
    print()

print("="*100)
print("📊 RESUMO")
print("="*100)
print()
print(f"✅ Passageiros que EXISTEM na tabela: {passengers_found}")
print(f"❌ Passageiros que NÃO EXISTEM na tabela: {passengers_missing}")
print(f"📊 Total de corridas: {len(rides)}")
print()

if passengers_missing > 0:
    print("="*100)
    print("⚠️  PROBLEMA IDENTIFICADO!")
    print("="*100)
    print()
    print(f"{passengers_missing} passageiros têm corridas registradas em rides_data,")
    print("mas NÃO existem na tabela passenger_personal_details!")
    print()
    print("Isso explica por que o endpoint /api/passengers/kpis mostra menos corridas.")
    print("O endpoint só conta passageiros que existem na tabela passenger_personal_details!")
    print()

cur.close()
conn.close()
