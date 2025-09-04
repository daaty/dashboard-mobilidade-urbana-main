import psycopg2
import json

conn = psycopg2.connect(
    host='148.230.73.27',
    database='n8n_db', 
    user='n8n_user',
    password='n8n_pw',
    port=5432
)

cursor = conn.cursor()

print("🔍 CONTANDO CANCELAMENTOS DOS DADOS REAIS:")

# Buscar todos os motoristas com cancelamentos
cursor.execute("""
    SELECT 
        driver_id,
        name,
        additional_data
    FROM drivers_data 
    WHERE additional_data IS NOT NULL
""")

drivers = cursor.fetchall()
total_cancelled = 0
drivers_with_cancellations = 0

for driver in drivers:
    driver_id = driver[0]
    name = driver[1]
    additional_data = driver[2]
    
    if additional_data:
        # Contar cancelamentos
        driver_cancelled = int(additional_data.get('driver_cancelled_rides', 0))
        user_cancelled = int(additional_data.get('user_cancelled_rides', 0))
        
        # Formato alternativo
        if driver_cancelled == 0:
            driver_cancelled = int(additional_data.get('Driver Cancelled Rides', 0))
        if user_cancelled == 0:
            user_cancelled = int(additional_data.get('User Cancelled Rides', 0))
        
        total_driver_cancelled = driver_cancelled + user_cancelled
        
        if total_driver_cancelled > 0:
            drivers_with_cancellations += 1
            total_cancelled += total_driver_cancelled
            print(f"   - {name} (ID: {driver_id}): {total_driver_cancelled} cancelamentos")

print(f"\n📊 RESUMO:")
print(f"Total de motoristas analisados: {len(drivers)}")
print(f"Motoristas com cancelamentos: {drivers_with_cancellations}")
print(f"Total de cancelamentos: {total_cancelled}")

cursor.close()
conn.close()
