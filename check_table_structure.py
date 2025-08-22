import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'dashboard_mobilidade'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )
    cur = conn.cursor()
    
    # Verificar se a tabela driver_personal_details existe
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'driver_personal_details'
        );
    """)
    
    exists = cur.fetchone()[0]
    print(f'Tabela driver_personal_details existe: {exists}')
    
    if exists:
        # Obter estrutura da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'driver_personal_details'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print('\nEstrutura da tabela:')
        for col in columns:
            print(f'  {col[0]}: {col[1]} (nullable: {col[2]})')
            
        # Contar registros
        cur.execute("SELECT COUNT(*) FROM driver_personal_details;")
        count = cur.fetchone()[0]
        print(f'\nTotal de registros: {count}')
    else:
        print('Tabela não existe. Listando todas as tabelas disponíveis:')
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        for table in tables:
            print(f'  - {table[0]}')
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f'Erro: {e}')
