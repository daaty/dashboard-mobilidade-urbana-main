import psycopg2

conn = psycopg2.connect(
    host='148.230.73.27',
    port=5432,
    database='n8n_db',
    user='n8n_user',
    password='n8n_pw'
)

cursor = conn.cursor()

# Verificar duplicatas por motorista
print("=" * 60)
print("ANÁLISE DE REGISTROS POR MOTORISTA (data_type='performance')")
print("=" * 60)

cursor.execute("""
    SELECT 
        driver_id, 
        COUNT(*) as registros,
        MAX(scraped_at) as ultimo_scrape
    FROM drivers_data 
    WHERE data_type = 'performance' 
    GROUP BY driver_id 
    ORDER BY registros DESC 
    LIMIT 10;
""")

result = cursor.fetchall()
print(f"\n{'Driver ID':<30} | {'Registros':<10} | {'Último Scrape'}")
print("-" * 70)
for row in result:
    print(f"{row[0]:<30} | {row[1]:<10} | {row[2]}")

# Total de motoristas únicos
cursor.execute("""
    SELECT 
        COUNT(DISTINCT driver_id) as motoristas_unicos,
        COUNT(*) as total_registros
    FROM drivers_data 
    WHERE data_type = 'performance';
""")

stats = cursor.fetchone()
print(f"\n{'='*60}")
print(f"Total de motoristas únicos: {stats[0]}")
print(f"Total de registros: {stats[1]}")
print(f"Média de registros por motorista: {stats[1] / stats[0]:.2f}")

# Verificar dados de um motorista específico
cursor.execute("""
    SELECT 
        scraped_at,
        additional_data->>'Success Rides' as success_rides,
        additional_data->>'Online Hours' as online_hours
    FROM drivers_data 
    WHERE data_type = 'performance' 
        AND driver_id = (
            SELECT driver_id 
            FROM drivers_data 
            WHERE data_type = 'performance' 
            GROUP BY driver_id 
            HAVING COUNT(*) > 1 
            LIMIT 1
        )
    ORDER BY scraped_at DESC;
""")

print(f"\n{'='*60}")
print("EXEMPLO DE MOTORISTA COM MÚLTIPLOS REGISTROS:")
print(f"{'='*60}")
print(f"{'Scrape Date':<25} | {'Success Rides':<15} | {'Online Hours'}")
print("-" * 70)
for row in cursor.fetchall():
    print(f"{str(row[0]):<25} | {row[1]:<15} | {row[2]}")

# Verificar a query atual (com SUM) vs a correta (último registro)
cursor.execute("""
    SELECT 
        SUM(CAST(additional_data->>'Success Rides' AS INTEGER)) as sum_total,
        COUNT(DISTINCT driver_id) as motoristas
    FROM drivers_data
    WHERE data_type = 'performance'
        AND additional_data->>'Success Rides' IS NOT NULL;
""")

sum_result = cursor.fetchone()

cursor.execute("""
    WITH latest_records AS (
        SELECT DISTINCT ON (driver_id)
            driver_id,
            CAST(additional_data->>'Success Rides' AS INTEGER) as success_rides
        FROM drivers_data
        WHERE data_type = 'performance'
            AND additional_data->>'Success Rides' IS NOT NULL
        ORDER BY driver_id, scraped_at DESC
    )
    SELECT SUM(success_rides) as correct_total
    FROM latest_records;
""")

correct_result = cursor.fetchone()

print(f"\n{'='*60}")
print("COMPARAÇÃO: SUM DE TODOS vs ÚLTIMO REGISTRO")
print(f"{'='*60}")
print(f"SUM de TODOS os registros: {sum_result[0]} corridas")
print(f"SUM do ÚLTIMO registro por motorista: {correct_result[0]} corridas")
print(f"Diferença: {sum_result[0] - correct_result[0]} corridas duplicadas")
print(f"\n⚠️  A query atual está contando {((sum_result[0] / correct_result[0]) - 1) * 100:.1f}% a mais!")

cursor.close()
conn.close()
