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

print("🔍 ANALISANDO ESTRUTURA DAS CORRIDAS:")

# Verificar alguns exemplos de rides_history para entender como detectar cancelamentos
cursor.execute("""
    SELECT 
        driver_id,
        personal_data->>'driver_name' as nome,
        rides_history
    FROM driver_personal_details 
    WHERE rides_history IS NOT NULL 
      AND rides_history != '[]'
    LIMIT 3
""")

drivers = cursor.fetchall()
for driver in drivers:
    print(f"\nDriver: {driver[1]} (ID: {driver[0]})")
    rides_history = driver[2]
    if rides_history and len(rides_history) > 0:
        print("Exemplo de corrida:")
        first_ride = rides_history[0]
        print(f"   Campos disponíveis: {list(first_ride.keys())}")
        print(f"   Corrida completa: {json.dumps(first_ride, indent=2)}")
        break

cursor.close()
conn.close()
