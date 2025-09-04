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

print("🔍 ESTRATÉGIA DE SOLUÇÃO:")

# Verificar quais cidades têm motoristas na drivers_data mas não na driver_personal_details
cursor.execute("""
    SELECT 
        dd.additional_data->>'City' as cidade,
        COUNT(*) as total_drivers_data,
        COUNT(dpd.driver_id) as total_personal_details,
        COUNT(*) - COUNT(dpd.driver_id) as motoristas_faltando
    FROM drivers_data dd
    LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
    WHERE dd.additional_data->>'City' IS NOT NULL
    GROUP BY dd.additional_data->>'City'
    ORDER BY motoristas_faltando DESC
""")

city_stats = cursor.fetchall()
print("📊 ESTATÍSTICAS POR CIDADE:")
print("Cidade                 | Total | Com Personal | Faltando")
print("-" * 55)
for stat in city_stats:
    cidade = stat[0] or "N/A"
    total = stat[1]
    com_personal = stat[2]
    faltando = stat[3]
    print(f"{cidade:<20} | {total:5} | {com_personal:11} | {faltando:8}")

# Verificar se algum dos motoristas "faltando" tem dados de vehicle_type no additional_data
print("\n🚗 VERIFICANDO SE HÁ VEHICLE_TYPE NO ADDITIONAL_DATA:")
cursor.execute("""
    SELECT 
        dd.driver_id,
        dd.name,
        dd.additional_data->>'City' as cidade,
        dd.additional_data->>'Vehicle Number' as veiculo
    FROM drivers_data dd
    LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
    WHERE dpd.driver_id IS NULL 
      AND dd.additional_data->>'Vehicle Number' IS NOT NULL
      AND dd.additional_data->>'City' IN ('Guarantã do Norte', 'Matupá', 'Nova Monte Verde', 'Nova Bandeirantes')
    LIMIT 10
""")

missing_with_vehicle = cursor.fetchall()
print(f"Motoristas sem personal_data MAS com Vehicle Number: {len(missing_with_vehicle)}")
for driver in missing_with_vehicle:
    print(f"   - {driver[1]} (ID: {driver[0]}, Cidade: {driver[2]}, Veículo: {driver[3]})")

cursor.close()
conn.close()

print("\n🎯 OPÇÕES DE SOLUÇÃO:")
print("1. FILTRAR NO FRONTEND: Mostrar apenas motoristas com personal_data válido")
print("2. MIGRAR DADOS: Criar registros na driver_personal_details para motoristas faltantes") 
print("3. USAR DADOS DO ADDITIONAL_DATA: Extrair vehicle_type do campo additional_data quando personal_data for NULL")
