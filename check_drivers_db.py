import psycopg2
import json

# String de conexão do PostgreSQL
import psycopg2
import json

# String de conexão PostgreSQL remoto
DATABASE_URL = 'postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db'
print(f'🔗 Conectando ao PostgreSQL: {DATABASE_URL}')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Verificar quantos motoristas existem na tabela drivers_data
    print('\n👨‍💼 MOTORISTAS na tabela drivers_data:')
    cursor.execute('SELECT COUNT(*) FROM drivers_data;')
    total_drivers = cursor.fetchone()[0]
    print(f'   Total de registros: {total_drivers}')
    
    # Verificar por data_type
    print('\n📊 MOTORISTAS por data_type:')
    cursor.execute('SELECT data_type, COUNT(*) FROM drivers_data GROUP BY data_type;')
    tipos = cursor.fetchall()
    for tipo, count in tipos:
        print(f'   {tipo}: {count} registros')
    
    # Verificar sample de additional_data para ver estrutura das cidades
    print('\n🏙️ SAMPLE de additional_data (para ver cidades):')
    cursor.execute('SELECT additional_data FROM drivers_data LIMIT 5;')
    samples = cursor.fetchall()
    for i, (sample,) in enumerate(samples, 1):
        try:
            data = json.loads(sample)
            print(f'   Sample {i}: {data}')
        except:
            print(f'   Sample {i}: {sample}')
    
    cursor.close()
    conn.close()
    print('✅ Conexão fechada')
    
except Exception as e:
    print(f'❌ Erro: {e}')
