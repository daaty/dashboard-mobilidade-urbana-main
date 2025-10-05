import psycopg2

c = psycopg2.connect(host='148.230.73.27', port=5432, database='n8n_db', user='n8n_user', password='n8n_pw')
cur = c.cursor()

print("\n" + "="*80)
print("RESUMO FINAL - MOTORISTAS ATIVOS")
print("="*80)
print()

# 1. Total de motoristas e status
cur.execute("SELECT COUNT(*) FROM driver_personal_details WHERE personal_data IS NOT NULL;")
total = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*) 
    FROM driver_personal_details 
    WHERE personal_data->>'status' IN ('Active', 'Offline', 'Online', 'Busy', 'active', 'offline', 'online', 'busy');
""")
ativos = cur.fetchone()[0]

print(f"📊 TOTAL DE MOTORISTAS CADASTRADOS: {total}")
print(f"✅ MOTORISTAS ATIVOS (status != unknown): {ativos}")
print(f"❌ MOTORISTAS INATIVOS/UNKNOWN: {total - ativos}")
print()

# 2. Motoristas com corridas nos últimos 6 meses
cur.execute("""
    WITH rides_data AS (
        SELECT 
            d.driver_id,
            jsonb_array_elements(d.rides_history) as ride
        FROM driver_personal_details d
        WHERE jsonb_array_length(d.rides_history) > 0
    ),
    filtered_rides AS (
        SELECT 
            driver_id,
            ride,
            CASE 
                WHEN (ride->>'drop_time') ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4} : [0-9]{1,2}:[0-9]{2} am$' 
                THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH12:MI am')
                WHEN (ride->>'drop_time') ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4} : [0-9]{1,2}:[0-9]{2} pm$' 
                THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH12:MI pm')
            END as drop_timestamp
        FROM rides_data
    )
    SELECT 
        COUNT(DISTINCT driver_id) as motoristas_com_corridas,
        COUNT(*) as total_corridas,
        SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue
    FROM filtered_rides
    WHERE drop_timestamp IS NOT NULL 
        AND drop_timestamp >= NOW() - INTERVAL '180 days';
""")

result = cur.fetchone()
motoristas_com_corridas = result[0]
corridas_6m = result[1]
revenue_6m = result[2]

print(f"🚗 MOTORISTAS COM CORRIDAS (últimos 6 meses): {motoristas_com_corridas}")
print(f"📈 Total de corridas: {corridas_6m}")
print(f"💰 Receita total: R$ {revenue_6m:.2f}")
print()

print("="*80)
print("COMPARAÇÃO: O QUE CADA MÉTRICA REPRESENTA")
print("="*80)
print()
print(f"1. 'Motoristas Ativos' = {ativos} motoristas")
print(f"   └─ Definição: Status em ['Active', 'Online', 'Offline', 'Busy']")
print(f"   └─ Uso: KPI Principal no dashboard")
print()
print(f"2. 'Motoristas com Corridas (6 meses)' = {motoristas_com_corridas} motoristas")
print(f"   └─ Definição: Motoristas que realizaram corridas nos últimos 6 meses")
print(f"   └─ Uso: Performance Metrics (análise de produtividade)")
print()
print("✅ CORREÇÃO APLICADA:")
print(f"   O card 'Motoristas Ativos' no Performance Metrics agora busca")
print(f"   o valor correto do endpoint /drivers/dashboard = {ativos}")
print()
print("="*80)

cur.close()
c.close()
