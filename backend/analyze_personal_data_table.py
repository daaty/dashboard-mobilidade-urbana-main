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

print("🔍 ANÁLISE DETALHADA DA TABELA driver_personal_details:")

# Verificar registros únicos por driver_id
cursor.execute("""
    SELECT driver_id, COUNT(*) as count
    FROM driver_personal_details 
    GROUP BY driver_id 
    HAVING COUNT(*) > 1
    ORDER BY count DESC
""")

duplicates = cursor.fetchall()
print(f"Drivers com registros duplicados na driver_personal_details: {len(duplicates)}")
for dup in duplicates[:10]:
    print(f"   - Driver ID {dup[0]}: {dup[1]} registros")

# Total de registros únicos por driver_id
cursor.execute("""
    SELECT COUNT(DISTINCT driver_id) 
    FROM driver_personal_details
""")
unique_drivers = cursor.fetchone()[0]
print(f"\nTotal de drivers únicos em driver_personal_details: {unique_drivers}")

# Total de registros na tabela
cursor.execute("SELECT COUNT(*) FROM driver_personal_details")
total_records = cursor.fetchone()[0]
print(f"Total de registros na driver_personal_details: {total_records}")

# Verificar se todos têm vehicle_type no personal_data
print("\n🚗 ANÁLISE DE VEHICLE_TYPE:")
cursor.execute("""
    SELECT 
        driver_id,
        city,
        personal_data->>'vehicle_type' as vehicle_type
    FROM driver_personal_details 
    WHERE personal_data->>'vehicle_type' IS NOT NULL
    ORDER BY city, driver_id
""")

vehicles = cursor.fetchall()
print(f"Drivers com vehicle_type definido: {len(vehicles)}")

# Agrupar por vehicle_type
vehicle_counts = {}
city_counts = {}
for vehicle in vehicles:
    vtype = vehicle[2]
    city = vehicle[1]
    
    if vtype not in vehicle_counts:
        vehicle_counts[vtype] = 0
    vehicle_counts[vtype] += 1
    
    if city not in city_counts:
        city_counts[city] = 0
    city_counts[city] += 1

print("\nTipos de veículos encontrados:")
for vtype, count in sorted(vehicle_counts.items()):
    print(f"   - {vtype}: {count} motoristas")

print("\nCidades encontradas:")
for city, count in sorted(city_counts.items()):
    print(f"   - {city}: {count} motoristas")

# Verificar drivers sem vehicle_type
cursor.execute("""
    SELECT driver_id, city
    FROM driver_personal_details 
    WHERE personal_data->>'vehicle_type' IS NULL 
       OR personal_data->>'vehicle_type' = ''
""")

no_vehicle_type = cursor.fetchall()
print(f"\nDrivers SEM vehicle_type: {len(no_vehicle_type)}")
for driver in no_vehicle_type[:5]:
    print(f"   - {driver[0]} (Cidade: {driver[1]})")

cursor.close()
conn.close()
