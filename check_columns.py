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
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'driver_personal_details' 
    ORDER BY ordinal_position;
""")

print("Colunas da tabela driver_personal_details:")
for row in cursor.fetchall():
    print(f"  - {row[0]} ({row[1]})")

cursor.close()
conn.close()
