import psycopg2

conn = psycopg2.connect(
    host='148.230.73.27',
    database='n8n_db', 
    user='n8n_user',
    password='n8n_pw',
    port=5432
)

cursor = conn.cursor()

# Listar todas as tabelas
print("🗄️ TABELAS DISPONÍVEIS NO BANCO:")
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")

tables = cursor.fetchall()
for table in tables:
    print(f"   - {table[0]}")

print(f"\nTotal de tabelas: {len(tables)}")

# Procurar tabelas relacionadas a drivers
print("\n🔍 PROCURANDO TABELAS RELACIONADAS A DRIVERS:")
driver_tables = [table[0] for table in tables if 'driver' in table[0].lower()]
for table in driver_tables:
    print(f"   ✅ {table}")

if not driver_tables:
    print("   ❌ Nenhuma tabela com 'driver' no nome encontrada")

cursor.close()
conn.close()
