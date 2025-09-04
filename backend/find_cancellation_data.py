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

print("🔍 PROCURANDO DADOS DE CANCELAMENTOS EM OUTRAS ABAS:")

# Verificar se outras abas têm dados de cancelamentos para Matupá
cursor.execute("""
    SELECT 
        page_source,
        driver_id,
        name,
        additional_data
    FROM drivers_data 
    WHERE additional_data->>'City' = 'Matupá'
      AND (
        additional_data ? 'driver_cancelled_rides' OR
        additional_data ? 'user_cancelled_rides' OR  
        additional_data ? 'cancelled_rides' OR
        additional_data ? 'success_rides'
      )
    LIMIT 5
""")

drivers_with_cancellation_data = cursor.fetchall()
print(f"Motoristas de Matupá com dados de cancelamentos: {len(drivers_with_cancellation_data)}")

for driver in drivers_with_cancellation_data:
    additional_data = driver[3]
    print(f"\nDriver: {driver[2]} (ID: {driver[1]}, Aba: {driver[0]})")
    print(f"   Campos disponíveis: {list(additional_data.keys())}")
    
    # Verificar dados de cancelamentos
    driver_cancelled = additional_data.get('driver_cancelled_rides', 'N/A')
    user_cancelled = additional_data.get('user_cancelled_rides', 'N/A')
    success_rides = additional_data.get('success_rides', 'N/A')
    
    print(f"   Driver cancelled: {driver_cancelled}")
    print(f"   User cancelled: {user_cancelled}")
    print(f"   Success rides: {success_rides}")

cursor.close()
conn.close()
