import psycopg2
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def test_city_growth():
    """Testa o endpoint de crescimento por cidade"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Período de 6 meses
    start_date = datetime.now() - timedelta(days=180)
    
    print("=== Testando Query de Crescimento por Cidade ===\n")
    
    # Query cadastrados
    cadastrados_query = """
        WITH city_registrations AS (
            SELECT 
                city,
                COUNT(DISTINCT driver_id) as total_cadastrados,
                COUNT(DISTINCT CASE 
                    WHEN personal_data->>'joining_date' IS NOT NULL 
                        AND personal_data->>'joining_date' ~ '^\d{2}/\d{2}/\d{4}$'
                        AND TO_DATE(personal_data->>'joining_date', 'DD/MM/YYYY') >= %s 
                    THEN driver_id 
                END) as novos_cadastrados
            FROM driver_personal_details
            WHERE city IS NOT NULL 
                AND city != ''
            GROUP BY city
        )
        SELECT * FROM city_registrations
        WHERE total_cadastrados > 0
        ORDER BY total_cadastrados DESC
        LIMIT 5;
    """
    
    cursor.execute(cadastrados_query, (start_date,))
    cadastrados_data = {row[0]: {"total_cadastrados": row[1], "novos_cadastrados": row[2]} for row in cursor.fetchall()}
    
    # Query ativos
    ativos_query = """
        SELECT 
            city,
            COUNT(DISTINCT driver_id) as total_ativos
        FROM driver_personal_details
        WHERE city IS NOT NULL 
            AND city != ''
            AND jsonb_array_length(rides_history) > 0
        GROUP BY city
        ORDER BY total_ativos DESC
        LIMIT 5;
    """
    cursor.execute(ativos_query)
    ativos_data = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Combinar
    all_cities = set(list(cadastrados_data.keys()) + list(ativos_data.keys()))
    
    print("Top 5 Cidades - Crescimento de Motoristas:\n")
    for cidade in list(all_cities)[:5]:
        cadastrados_info = cadastrados_data.get(cidade, {"total_cadastrados": 0, "novos_cadastrados": 0})
        ativos = ativos_data.get(cidade, 0)
        
        total_cadastrados = cadastrados_info["total_cadastrados"]
        taxa_ativacao = round((ativos / total_cadastrados * 100), 1) if total_cadastrados > 0 else 0
        
        print(f"{cidade}:")
        print(f"  Total Cadastrados: {total_cadastrados}")
        print(f"  Novos (6 meses): {cadastrados_info['novos_cadastrados']}")
        print(f"  Total Ativos: {ativos}")
        print(f"  Taxa de Ativação: {taxa_ativacao}%")
        print()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_city_growth()
