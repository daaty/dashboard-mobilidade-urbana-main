"""
🔍 SCRIPT RÁPIDO - Verificar estrutura da tabela metas_progressivas
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
    print("  🔍 ESTRUTURA DA TABELA: metas_progressivas")
    print("="*80 + "\n")
    
    # Query para ver estrutura
    query = """
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'metas_progressivas'
    ORDER BY ordinal_position;
    """
    
    cursor.execute(query)
    columns = cursor.fetchall()
    
    print("Colunas encontradas:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]}) - Nullable: {col[2]}")
    
    print("\n" + "="*80)
    print("  📊 PRIMEIRAS 5 LINHAS")
    print("="*80 + "\n")
    
    cursor.execute("SELECT * FROM metas_progressivas LIMIT 5")
    rows = cursor.fetchall()
    
    # Pegar nomes das colunas
    col_names = [desc[0] for desc in cursor.description]
    print("Colunas: " + ", ".join(col_names))
    print()
    
    for row in rows:
        print(row)
    
    cursor.close()
    conn.close()
    
    print("\n✅ Análise concluída!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
