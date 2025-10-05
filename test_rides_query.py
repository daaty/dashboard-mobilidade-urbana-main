import psycopg2
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Testar estrutura de rides_history
print("=== Verificando estrutura de rides_history ===")
cursor.execute("""
    SELECT 
        driver_id,
        name,
        rides_history
    FROM driver_personal_details
    WHERE rides_history IS NOT NULL 
        AND rides_history != '[]'
        AND rides_history != ''
    LIMIT 1;
""")

result = cursor.fetchone()
if result:
    print(f"\nDriver ID: {result[0]}")
    print(f"Name: {result[1]}")
    print(f"Rides History Type: {type(result[2])}")
    print(f"Rides History Sample: {result[2][:200]}")
    
    # Testar JSONB
    print("\n=== Testando conversão JSONB ===")
    try:
        cursor.execute("""
            SELECT 
                driver_id,
                jsonb_array_length(rides_history::jsonb) as total
            FROM driver_personal_details
            WHERE driver_id = %s;
        """, (result[0],))
        res = cursor.fetchone()
        print(f"JSONB array length: {res[1]}")
    except Exception as e:
        print(f"Erro ao converter para JSONB: {e}")
        
    # Testar extração de elementos
    print("\n=== Testando extração de elementos ===")
    try:
        cursor.execute("""
            WITH rides_data AS (
                SELECT 
                    d.driver_id,
                    d.name,
                    jsonb_array_elements(d.rides_history::jsonb) as ride
                FROM driver_personal_details d
                WHERE d.driver_id = %s
            )
            SELECT 
                driver_id,
                name,
                ride->>'drop_time' as drop_time,
                ride->>'fare' as fare,
                ride->>'duration' as duration
            FROM rides_data
            LIMIT 3;
        """, (result[0],))
        
        rides = cursor.fetchall()
        print(f"Corridas extraídas: {len(rides)}")
        for r in rides:
            print(f"  - {r[1]}: drop_time={r[2]}, fare={r[3]}, duration={r[4]}")
            
    except Exception as e:
        print(f"Erro ao extrair elementos: {e}")

else:
    print("Nenhum registro encontrado!")

# Testar query completa do endpoint
print("\n\n=== Testando query do endpoint (sem filtro de período) ===")
try:
    query = """
        WITH rides_data AS (
            SELECT 
                d.driver_id,
                d.name,
                d.phone,
                jsonb_array_length(d.rides_history::jsonb) as total_rides
            FROM driver_personal_details d
            WHERE d.rides_history IS NOT NULL 
                AND d.rides_history != '[]'
                AND d.rides_history != ''
        )
        SELECT 
            name,
            driver_id,
            total_rides as success_rides,
            0 as online_hours,
            0 as rejected_rides,
            0 as missed_rides,
            phone
        FROM rides_data
        WHERE total_rides > 0
        ORDER BY total_rides DESC
        LIMIT 5;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"Top 5 motoristas (total de corridas):")
    for row in results:
        print(f"  {row[0]}: {row[2]} corridas")
        
except Exception as e:
    print(f"Erro na query: {e}")

cursor.close()
conn.close()
