import psycopg2

c = psycopg2.connect(host='148.230.73.27', port=5432, database='n8n_db', user='n8n_user', password='n8n_pw')
cur = c.cursor()

# Todos os status distintos
cur.execute("SELECT personal_data->>'status' as st, COUNT(*) FROM driver_personal_details WHERE personal_data IS NOT NULL GROUP BY st ORDER BY COUNT(*) DESC;")
results = cur.fetchall()

print("\n=== STATUS DISTINTOS ===")
for row in results:
    print(f"{row[0]}: {row[1]}")

# Total geral
cur.execute("SELECT COUNT(*) FROM driver_personal_details WHERE personal_data IS NOT NULL;")
total = cur.fetchone()[0]
print(f"\nTOTAL GERAL: {total}")

# Motoristas ATIVOS (status = Active, Offline, Online, Busy)
cur.execute("""
    SELECT COUNT(*) 
    FROM driver_personal_details 
    WHERE personal_data->>'status' IN ('Active', 'Offline', 'Online', 'Busy', 'active', 'offline', 'online', 'busy');
""")
ativos = cur.fetchone()[0]
print(f"MOTORISTAS ATIVOS (status válido): {ativos}")

cur.close()
c.close()
