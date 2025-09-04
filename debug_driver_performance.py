import sqlite3
import json

conn = sqlite3.connect('drivers_data.db')
cursor = conn.cursor()

# Verificar quantos registros há na aba Driver Performance
cursor.execute("SELECT COUNT(*) FROM drivers_data WHERE page_source = 'Driver Performance'")
count = cursor.fetchone()[0]
print(f"Registros na aba Driver Performance: {count}")

# Buscar um motorista específico na aba Driver Performance
cursor.execute("""
SELECT driver_id, additional_data 
FROM drivers_data 
WHERE page_source = 'Driver Performance' 
AND additional_data LIKE '%online_hours%' 
LIMIT 3
""")

records = cursor.fetchall()
for record in records:
    driver_id, additional_data = record
    print(f"\nDriver ID: {driver_id}")
    
    try:
        data = json.loads(additional_data)
        print(f"Online Hours: {data.get('online_hours', 'N/A')}")
        print(f"Active Days: {data.get('active_days', 'N/A')}")
        print(f"Success Rides: {data.get('success_rides', 'N/A')}")
        print(f"Vehicle: {data.get('vehicle', 'N/A')}")
    except:
        print("Erro ao fazer parse do JSON")

conn.close()
