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

print("🔍 ANALISANDO TABELA driver_personal_details:")

# Verificar estrutura da tabela
cursor.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'driver_personal_details'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
print("Colunas da tabela driver_personal_details:")
for col in columns:
    print(f"   - {col[0]} ({col[1]}) - Null: {col[2]}")

# Verificar quantos registros existem
cursor.execute("SELECT COUNT(*) FROM driver_personal_details")
total_count = cursor.fetchone()[0]
print(f"\nTotal de registros em driver_personal_details: {total_count}")

# Exemplo de alguns registros
print("\n📋 EXEMPLOS DE REGISTROS:")
cursor.execute("SELECT * FROM driver_personal_details LIMIT 3")
examples = cursor.fetchall()
for example in examples:
    print(f"Registro: {example}")
    print()

print("\n🔍 ANALISANDO TABELA drivers_data:")

# Verificar estrutura da tabela drivers_data
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

# Verificar quantos registros existem na drivers_data
cursor.execute("SELECT COUNT(*) FROM drivers_data")
drivers_count = cursor.fetchone()[0]
print(f"\nTotal de registros em drivers_data: {drivers_count}")

# Exemplo de alguns registros da drivers_data
print("\n📋 EXEMPLOS DE REGISTROS drivers_data:")
cursor.execute("SELECT driver_id, name, additional_data FROM drivers_data LIMIT 3")
driver_examples = cursor.fetchall()
for example in driver_examples:
    print(f"Driver ID: {example[0]}, Nome: {example[1]}")
    if example[2]:
        print(f"Additional data: {json.dumps(example[2], indent=2)}")
    print()

cursor.close()
conn.close()
