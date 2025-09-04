import psycopg2
import json
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host='148.230.73.27',
    database='n8n_db', 
    user='n8n_user',
    password='n8n_pw',
    port=5432
)

cursor = conn.cursor()

print("🔍 ANALISANDO DADOS REAIS DE CORRIDAS PARA KPIs:")

# Verificar dados de corridas dos motoristas com personal_data
cursor.execute("""
    SELECT 
        dpd.driver_id,
        dpd.city,
        dpd.rides_history,
        dpd.personal_data
    FROM driver_personal_details dpd
    WHERE dpd.city IN ('Guarantã do Norte', 'Matupá', 'Nova Monte Verde', 'Nova Bandeirantes')
    AND dpd.rides_history IS NOT NULL
    LIMIT 5
""")

rides_data = cursor.fetchall()
print(f"Motoristas com dados de corridas: {len(rides_data)}")

total_rides = 0
total_distance = 0
total_duration = 0
cancelled_rides = 0
completed_rides = 0

print("\n📊 ANÁLISE DETALHADA DAS CORRIDAS:")

for driver in rides_data:
    driver_id = driver[0]
    city = driver[1]
    rides_history = driver[2]
    
    if rides_history and len(rides_history) > 0:
        print(f"\nMotorista {driver_id} ({city}): {len(rides_history)} corridas")
        
        for ride in rides_history[:3]:  # Mostrar apenas 3 primeiras corridas
            fare = ride.get('fare', 0)
            duration = ride.get('duration', 0)
            distance = ride.get('distance_travelled', 0)
            rating = ride.get('driver_rating', '--')
            
            print(f"  - Fare: R${fare}, Duração: {duration}min, Distância: {distance}km, Rating: {rating}")
            
            # Acumular estatísticas
            try:
                if fare and fare != '0':
                    completed_rides += 1
                    total_distance += float(distance) if distance else 0
                    total_duration += int(duration) if duration else 0
                else:
                    cancelled_rides += 1
            except:
                pass
        
        total_rides += len(rides_history)

print(f"\n📈 ESTATÍSTICAS GERAIS:")
print(f"Total de corridas: {total_rides}")
print(f"Corridas completadas: {completed_rides}")
print(f"Corridas canceladas: {cancelled_rides}")
print(f"Taxa de conclusão: {(completed_rides / total_rides * 100):.1f}%" if total_rides > 0 else "0%")
print(f"Taxa de cancelamento: {(cancelled_rides / total_rides * 100):.1f}%" if total_rides > 0 else "0%")
print(f"Distância total: {total_distance:.2f}km")
print(f"Duração total: {total_duration} minutos")
print(f"Km por corrida: {(total_distance / completed_rides):.1f}km" if completed_rides > 0 else "0km")
print(f"Tempo médio por corrida: {(total_duration / completed_rides):.1f}min" if completed_rides > 0 else "0min")

cursor.close()
conn.close()
