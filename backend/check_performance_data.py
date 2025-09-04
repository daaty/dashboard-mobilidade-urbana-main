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

print("🔍 VERIFICANDO DADOS DE PERFORMANCE:")

# Verificar quantos motoristas têm dados na aba "Driver Performance"
cursor.execute("""
    SELECT 
        page_source,
        COUNT(*) as total,
        COUNT(CASE WHEN additional_data->>'City' = 'Matupá' THEN 1 END) as matupa_count
    FROM drivers_data 
    GROUP BY page_source
    ORDER BY total DESC
""")

page_sources = cursor.fetchall()
print("Dados por aba (page_source):")
for source in page_sources:
    print(f"   - {source[0]}: {source[1]} total, {source[2]} em Matupá")

# Verificar especificamente motoristas de Matupá com dados de performance
cursor.execute("""
    SELECT 
        driver_id,
        name,
        additional_data
    FROM drivers_data 
    WHERE page_source = 'Driver Performance' 
      AND additional_data->>'City' = 'Matupá'
    LIMIT 3
""")

performance_drivers = cursor.fetchall()
print(f"\nMotoristas de Matupá com dados de performance: {len(performance_drivers)}")
for driver in performance_drivers:
    additional_data = driver[2]
    cancelled = additional_data.get('driver_cancelled_rides', 0) + additional_data.get('user_cancelled_rides', 0)
    success = additional_data.get('success_rides', 0)
    print(f"   - {driver[1]} (ID: {driver[0]}): {success} sucessos, {cancelled} canceladas")

cursor.close()
conn.close()
