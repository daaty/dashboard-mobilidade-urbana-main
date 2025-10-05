import psycopg2
import sys

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        personal_data->>'status' as status, 
        COUNT(*) as quantidade
    FROM driver_personal_details 
    WHERE personal_data IS NOT NULL
    GROUP BY personal_data->>'status' 
    ORDER BY COUNT(*) DESC;
""")

results = cursor.fetchall()

print("STATUS DISTINTOS NO BANCO:", flush=True)
print("="*50, flush=True)
print(f"Total de resultados: {len(results)}", flush=True)
print(flush=True)
for row in results:
    status_value = row[0] if row[0] else "NULL"
    print(f"  '{status_value}': {row[1]} motoristas", flush=True)

cursor.close()
conn.close()
