import psycopg2

try:
    # Conectar na VPS
    DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Contar todos os registros
    cursor.execute("SELECT COUNT(*) FROM drivers_data WHERE data_type = 'active'")
    total_registros = cursor.fetchone()[0]
    
    # Contar telefones únicos
    cursor.execute("""
        SELECT COUNT(DISTINCT mobile) 
        FROM drivers_data 
        WHERE data_type = 'active' AND mobile IS NOT NULL
    """)
    telefones_unicos = cursor.fetchone()[0]
    
    # Listar alguns exemplos
    cursor.execute("""
        SELECT driver_id, name, mobile, scraped_at 
        FROM drivers_data 
        WHERE data_type = 'active'
        ORDER BY scraped_at DESC
        LIMIT 20
    """)
    exemplos = cursor.fetchall()
    
    print(f"=== ANÁLISE DA BASE DE DADOS ===")
    print(f"Total de registros: {total_registros}")
    print(f"Telefones únicos: {telefones_unicos}")
    print(f"\n=== PRIMEIROS 20 REGISTROS ===")
    
    for i, (driver_id, name, mobile, scraped_at) in enumerate(exemplos, 1):
        print(f"{i:2d}. ID: {driver_id} | Nome: {name} | Tel: {mobile} | Data: {scraped_at}")
    
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
