import psycopg2

conn = psycopg2.connect(
    host='148.230.73.27',
    port=5432,
    database='n8n_db',
    user='n8n_user',
    password='n8n_pw'
)

cursor = conn.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
        AND table_name LIKE '%driver%' 
    ORDER BY table_name;
""")

print("Tabelas com 'driver' no nome:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.close()
conn.close()
