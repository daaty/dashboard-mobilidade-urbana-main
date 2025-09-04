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

print("🔍 ANALISANDO TABELA drivers_data:")

# Verificar estrutura da tabela
cursor.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'drivers_data'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
print("Colunas da tabela drivers_data:")
for col in columns:
    print(f"   - {col[0]} ({col[1]}) - Null: {col[2]}")

# Verificar quantos registros existem
cursor.execute("SELECT COUNT(*) FROM drivers_data")
total_count = cursor.fetchone()[0]
print(f"\nTotal de registros em drivers_data: {total_count}")

# Verificar se tem coluna personal_data
cursor.execute("SELECT COUNT(*) FROM drivers_data WHERE personal_data IS NOT NULL")
personal_data_count = cursor.fetchone()[0]
print(f"Registros com personal_data não NULL: {personal_data_count}")

cursor.execute("SELECT COUNT(*) FROM drivers_data WHERE personal_data IS NULL")
null_personal_data_count = cursor.fetchone()[0]
print(f"Registros com personal_data NULL: {null_personal_data_count}")

# Exemplo de alguns registros
print("\n📋 EXEMPLOS DE REGISTROS:")
cursor.execute("SELECT driver_id, driver_name, cidade FROM drivers_data LIMIT 5")
examples = cursor.fetchall()
for example in examples:
    print(f"   - {example[1]} (ID: {example[0]}, Cidade: {example[2]})")

# Verificar personal_data de exemplo
print("\n🔍 VERIFICANDO PERSONAL_DATA:")
cursor.execute("SELECT driver_id, driver_name, personal_data FROM drivers_data WHERE personal_data IS NOT NULL LIMIT 3")
personal_examples = cursor.fetchall()
for example in personal_examples:
    print(f"Driver: {example[1]} (ID: {example[0]})")
    if example[2]:
        personal_data = json.loads(example[2]) if isinstance(example[2], str) else example[2]
        vehicle_type = personal_data.get('vehicle_type', 'SEM VEHICLE_TYPE')
        print(f"   Vehicle type: {vehicle_type}")
    else:
        print("   Personal data é NULL")
    print()

cursor.close()
conn.close()
