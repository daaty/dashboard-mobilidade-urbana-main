import psycopg2

conn = psycopg2.connect(
    host='148.230.73.27',
    port=5432,
    database='n8n_db',
    user='n8n_user',
    password='n8n_pw'
)

cursor = conn.cursor()

# Testar query sem filtro
query = """
    SELECT 
        d.personal_data->>'driver_name' as name,
        d.driver_id,
        jsonb_array_length(d.rides_history) as success_rides,
        0 as online_hours,
        0 as rejected_rides,
        0 as missed_rides,
        d.personal_data->>'phone_no' as phone
    FROM driver_personal_details d
    WHERE d.rides_history IS NOT NULL 
        AND jsonb_array_length(d.rides_history) > 0
    ORDER BY success_rides DESC
    LIMIT 10;
"""

print("=== Top 10 Motoristas (todas as corridas) ===")
cursor.execute(query)
results = cursor.fetchall()

for row in results:
    print(f"  {row[0]}: {row[2]} corridas")

cursor.close()
conn.close()
print("\n✅ Query funcionou!")
