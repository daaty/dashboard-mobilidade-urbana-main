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

print("🔍 INVESTIGANDO PROBLEMA DE VEHICLE_TYPE:")

# Motoristas em drivers_data que NÃO estão em driver_personal_details
print("\n📊 MOTORISTAS SEM PERSONAL_DATA:")
cursor.execute("""
    SELECT dd.driver_id, dd.name, 
           CASE WHEN dd.additional_data IS NOT NULL THEN 
               dd.additional_data->>'City' 
           ELSE 'N/A' 
           END as cidade
    FROM drivers_data dd
    LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
    WHERE dpd.driver_id IS NULL
    ORDER BY dd.name
""")

missing_drivers = cursor.fetchall()
print(f"Total de motoristas sem personal_data: {len(missing_drivers)}")

# Mostrar exemplos dos motoristas que estão missing
print("\nPrimeiros 10 motoristas sem personal_data:")
for i, driver in enumerate(missing_drivers[:10]):
    print(f"   {i+1}. {driver[1]} (ID: {driver[0]}, Cidade: {driver[2]})")

# Motoristas que TÊM personal_data (para comparação)
print("\n✅ MOTORISTAS COM PERSONAL_DATA:")
cursor.execute("""
    SELECT dd.driver_id, dd.name, dpd.city
    FROM drivers_data dd
    INNER JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
    ORDER BY dd.name
""")

with_personal_data = cursor.fetchall()
print(f"Total de motoristas COM personal_data: {len(with_personal_data)}")

print("\nPrimeiros 10 motoristas com personal_data:")
for i, driver in enumerate(with_personal_data[:10]):
    print(f"   {i+1}. {driver[1]} (ID: {driver[0]}, Cidade: {driver[2]})")

# Verificar se algum dos motoristas sem personal_data tem dados de cidade no additional_data
print("\n🏙️ CIDADES DOS MOTORISTAS SEM PERSONAL_DATA:")
cidades_sem_personal = {}
for driver in missing_drivers:
    cidade = driver[2]
    if cidade != 'N/A':
        if cidade not in cidades_sem_personal:
            cidades_sem_personal[cidade] = 0
        cidades_sem_personal[cidade] += 1

for cidade, count in sorted(cidades_sem_personal.items()):
    print(f"   - {cidade}: {count} motoristas")

cursor.close()
conn.close()
