"""
🔍 SCRIPT - Verificar estrutura das tabelas de dados reais
Analisa rides_data, driver_personal_details, drivers_data e passenger_personal_details
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('backend/.env.production')

DB_HOST = os.getenv('DB_HOST', '148.230.73.27')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'n8n_db')
DB_USER = os.getenv('DB_USER', 'n8n_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'n8n_pw')

def analisar_tabela(cursor, nome_tabela):
    """Analisa estrutura e amostra de dados de uma tabela"""
    print("\n" + "="*80)
    print(f"  📊 TABELA: {nome_tabela}")
    print("="*80)
    
    # Verificar se tabela existe
    cursor.execute(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{nome_tabela}'
        );
    """)
    existe = cursor.fetchone()[0]
    
    if not existe:
        print(f"  ❌ Tabela '{nome_tabela}' NÃO EXISTE!")
        return
    
    # Estrutura
    print("\n📋 ESTRUTURA:")
    cursor.execute(f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = '{nome_tabela}'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"  - {col[0]:30} {col[1]:20} (Nullable: {col[2]})")
    
    # Contagem
    cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
    total = cursor.fetchone()[0]
    print(f"\n📊 TOTAL DE REGISTROS: {total:,}")
    
    # Amostra
    if total > 0:
        print("\n📄 AMOSTRA (3 primeiros registros):")
        cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        
        for i, row in enumerate(rows, 1):
            print(f"\n  Registro {i}:")
            for col_name, value in zip(col_names, row):
                if value is not None and str(value).strip():
                    print(f"    {col_name}: {value}")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("  🔍 ANÁLISE DAS TABELAS DE DADOS REAIS")
    print("="*80)
    
    # Analisar cada tabela
    tabelas = [
        'rides_data',
        'driver_personal_details',
        'drivers_data',
        'passenger_personal_details'
    ]
    
    for tabela in tabelas:
        analisar_tabela(cursor, tabela)
    
    # Análise de relacionamentos
    print("\n" + "="*80)
    print("  🔗 ANÁLISE DE RELACIONAMENTOS")
    print("="*80)
    
    # Verificar cidades nas corridas
    print("\n📍 CIDADES COM CORRIDAS:")
    cursor.execute("""
        SELECT 
            COALESCE(pickup_city, 'SEM_CIDADE') as cidade,
            COUNT(*) as total_corridas,
            COUNT(DISTINCT driver_id) as motoristas_unicos,
            COUNT(DISTINCT passenger_id) as passageiros_unicos
        FROM rides_data
        WHERE pickup_city IS NOT NULL AND pickup_city != ''
        GROUP BY pickup_city
        ORDER BY total_corridas DESC
        LIMIT 15;
    """)
    
    results = cursor.fetchall()
    for row in results:
        print(f"  {row[0]:30} | Corridas: {row[1]:6} | Motoristas: {row[2]:4} | Passageiros: {row[3]:4}")
    
    # Verificar período de dados
    print("\n📅 PERÍODO DOS DADOS:")
    cursor.execute("""
        SELECT 
            MIN(created_at) as primeira_corrida,
            MAX(created_at) as ultima_corrida,
            COUNT(*) as total
        FROM rides_data
        WHERE created_at IS NOT NULL;
    """)
    
    periodo = cursor.fetchone()
    if periodo:
        print(f"  Primeira corrida: {periodo[0]}")
        print(f"  Última corrida: {periodo[1]}")
        print(f"  Total de corridas: {periodo[2]:,}")
    
    # Verificar status das corridas
    print("\n📊 STATUS DAS CORRIDAS:")
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as total
        FROM rides_data
        GROUP BY status
        ORDER BY total DESC;
    """)
    
    status_results = cursor.fetchall()
    for row in status_results:
        print(f"  {row[0]:20} | {row[1]:,} corridas")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Análise concluída!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
