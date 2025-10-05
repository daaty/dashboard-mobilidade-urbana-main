import psycopg2

conn = psycopg2.connect(
    host='148.230.73.27',
    port=5432,
    database='n8n_db',
    user='n8n_user',
    password='n8n_pw'
)

cursor = conn.cursor()

print("=" * 80)
print("ANÁLISE DE TODOS OS ENDPOINTS - IDENTIFICANDO DUPLICATAS")
print("=" * 80)

# 1. BY-CITY (Active Drivers)
print("\n1. BY-CITY (data_type='active')")
cursor.execute("""
    SELECT 
        COUNT(DISTINCT driver_id) as motoristas_unicos,
        COUNT(*) as total_registros,
        AVG(cnt) as media_registros_por_motorista
    FROM (
        SELECT driver_id, COUNT(*) as cnt
        FROM drivers_data 
        WHERE data_type = 'active'
        GROUP BY driver_id
    ) sub;
""")
stats = cursor.fetchone()
print(f"   Motoristas únicos: {stats[0]}")
print(f"   Total registros: {stats[1]}")
print(f"   Média registros/motorista: {stats[2]:.2f}")
print(f"   ⚠️ PRECISA CORREÇÃO: {'SIM' if stats[2] > 1.5 else 'NÃO'}")

# 2. RATINGS DISTRIBUTION (Active Drivers)
print("\n2. RATINGS DISTRIBUTION (data_type='active')")
cursor.execute("""
    SELECT 
        COUNT(DISTINCT driver_id) as motoristas_unicos,
        COUNT(*) as total_registros
    FROM drivers_data 
    WHERE data_type = 'active'
        AND additional_data->>'Driver Ratings' IS NOT NULL;
""")
stats = cursor.fetchone()
print(f"   Motoristas únicos: {stats[0]}")
print(f"   Total registros: {stats[1]}")
if stats[0]:
    print(f"   Média registros/motorista: {stats[1] / stats[0]:.2f}")
    print(f"   ⚠️ PRECISA CORREÇÃO: {'SIM' if (stats[1] / stats[0]) > 1.5 else 'NÃO'}")

# 3. ONLINE ACTIVITY (Active Drivers)
print("\n3. ONLINE ACTIVITY (data_type='active')")
cursor.execute("""
    SELECT 
        COUNT(DISTINCT driver_id) as motoristas_unicos,
        COUNT(*) as total_registros
    FROM drivers_data 
    WHERE data_type = 'active';
""")
stats = cursor.fetchone()
print(f"   Motoristas únicos: {stats[0]}")
print(f"   Total registros: {stats[1]}")
if stats[0]:
    print(f"   Média registros/motorista: {stats[1] / stats[0]:.2f}")
    print(f"   ⚠️ PRECISA CORREÇÃO: {'SIM' if (stats[1] / stats[0]) > 1.5 else 'NÃO'}")

# 4. ACTIVITY COMPARISON (Active Drivers)
print("\n4. ACTIVITY COMPARISON (data_type='active')")
cursor.execute("""
    SELECT 
        COUNT(DISTINCT driver_id) as motoristas_unicos,
        COUNT(*) as total_registros
    FROM drivers_data 
    WHERE data_type = 'active'
        AND additional_data->>'Rides in Last 30 Days' IS NOT NULL;
""")
stats = cursor.fetchone()
print(f"   Motoristas únicos: {stats[0]}")
print(f"   Total registros: {stats[1]}")
if stats[0]:
    print(f"   Média registros/motorista: {stats[1] / stats[0]:.2f}")
    print(f"   ⚠️ PRECISA CORREÇÃO: {'SIM' if (stats[1] / stats[0]) > 1.5 else 'NÃO'}")

# 5. RECENT ENROLLMENTS (Enrollment)
print("\n5. RECENT ENROLLMENTS (data_type='enrollment')")
cursor.execute("""
    SELECT 
        COUNT(DISTINCT driver_id) as motoristas_unicos,
        COUNT(*) as total_registros
    FROM drivers_data 
    WHERE data_type = 'enrollment';
""")
stats = cursor.fetchone()
print(f"   Motoristas únicos: {stats[0]}")
print(f"   Total registros: {stats[1]}")
if stats[0]:
    print(f"   Média registros/motorista: {stats[1] / stats[0]:.2f}")
    print(f"   ⚠️ PRECISA CORREÇÃO: {'SIM' if (stats[1] / stats[0]) > 1.5 else 'NÃO'}")

# Exemplo de duplicata em active
print("\n" + "=" * 80)
print("EXEMPLO DE MOTORISTA COM DUPLICATAS (data_type='active'):")
print("=" * 80)
cursor.execute("""
    SELECT 
        driver_id,
        COUNT(*) as registros
    FROM drivers_data
    WHERE data_type = 'active'
    GROUP BY driver_id
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC
    LIMIT 1;
""")
example = cursor.fetchone()
if example:
    driver_id, count = example
    print(f"Driver ID: {driver_id}")
    print(f"Registros: {count}")
    
    cursor.execute(f"""
        SELECT 
            scraped_at,
            additional_data->>'City' as city,
            additional_data->>'Status' as status,
            additional_data->>'Rides in Last 7 Days' as rides_7d
        FROM drivers_data
        WHERE driver_id = '{driver_id}'
            AND data_type = 'active'
        ORDER BY scraped_at DESC
        LIMIT 5;
    """)
    
    print(f"\n{'Scraped At':<25} | {'City':<15} | {'Status':<10} | Rides 7d")
    print("-" * 75)
    for row in cursor.fetchall():
        print(f"{str(row[0]):<25} | {row[1]:<15} | {row[2]:<10} | {row[3]}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("RESUMO:")
print("  - Performance Metrics: JÁ CORRIGIDO ✅")
print("  - Top Performers: JÁ CORRIGIDO ✅") 
print("  - BY-CITY: PRECISA CORREÇÃO ⚠️")
print("  - RATINGS DISTRIBUTION: PRECISA CORREÇÃO ⚠️")
print("  - ONLINE ACTIVITY: PRECISA CORREÇÃO ⚠️")
print("  - ACTIVITY COMPARISON: PRECISA CORREÇÃO ⚠️")
print("  - RECENT ENROLLMENTS: VERIFICAR")
print("=" * 80)
