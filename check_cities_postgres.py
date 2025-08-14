import psycopg2
import os
from urllib.parse import urlparse

# String de conexão do PostgreSQL
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/mobilidade_urbana'
print(f'🔗 Conectando ao PostgreSQL: {DATABASE_URL}')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Verificar cidades na tabela rides
    print('\n🏙️ CIDADES ÚNICAS na tabela rides:')
    cursor.execute('SELECT DISTINCT cidade_origem, COUNT(*) FROM rides GROUP BY cidade_origem ORDER BY COUNT(*) DESC;')
    cidades_rides = cursor.fetchall()
    for cidade, count in cidades_rides:
        print(f'   "{cidade}" -> {count} corridas')
    
    # Testar especificamente Guarantã do Norte
    print('\n🔍 TESTANDO variações de Guarantã do Norte:')
    variacoes = ['Guarantã do Norte', 'GUARANTÃ DO NORTE', 'Guaranta do Norte', 'GUARANTA DO NORTE']
    for variacao in variacoes:
        cursor.execute('SELECT COUNT(*) FROM rides WHERE cidade_origem = %s;', (variacao,))
        count = cursor.fetchone()[0]
        print(f'   "{variacao}" -> {count} corridas')
    
    cursor.close()
    conn.close()
    print('✅ Conexão fechada')
    
except Exception as e:
    print(f'❌ Erro: {e}')
