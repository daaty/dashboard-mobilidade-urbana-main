import psycopg2
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def test_inactive_by_city():
    """Testa o endpoint de motoristas inativos por cidade"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Período de 6 meses
    start_date = datetime.now() - timedelta(days=180)
    
    print("=== Testando Query de Motoristas Inativos por Cidade ===\n")
    
    query = """
        WITH city_stats AS (
            SELECT 
                city,
                COUNT(DISTINCT driver_id) as total_cadastrados,
                COUNT(DISTINCT CASE 
                    WHEN jsonb_array_length(rides_history) = 0 
                    THEN driver_id 
                END) as total_inativos,
                COUNT(DISTINCT CASE 
                    WHEN jsonb_array_length(rides_history) = 0
                        AND personal_data->>'joining_date' IS NOT NULL 
                        AND personal_data->>'joining_date' ~ '^\d{2}/\d{2}/\d{4}$'
                        AND TO_DATE(personal_data->>'joining_date', 'DD/MM/YYYY') >= %s
                    THEN driver_id 
                END) as novos_inativos,
                COUNT(DISTINCT CASE 
                    WHEN jsonb_array_length(rides_history) > 0 
                    THEN driver_id 
                END) as total_ativos
            FROM driver_personal_details
            WHERE city IS NOT NULL 
                AND city != ''
            GROUP BY city
        )
        SELECT 
            city,
            total_cadastrados,
            total_inativos,
            novos_inativos,
            total_ativos,
            ROUND((total_inativos::DECIMAL / NULLIF(total_cadastrados, 0) * 100), 1) as taxa_inatividade
        FROM city_stats
        WHERE total_inativos > 0
        ORDER BY total_inativos DESC
        LIMIT 5;
    """
    
    cursor.execute(query, (start_date,))
    result = cursor.fetchall()
    
    print("Top 5 Cidades - Motoristas Inativos:\n")
    for row in result:
        print(f"{row[0]}:")
        print(f"  Total Cadastrados: {row[1]}")
        print(f"  Total Inativos: {row[2]}")
        print(f"  Novos Inativos (6 meses): {row[3]}")
        print(f"  Total Ativos: {row[4]}")
        print(f"  Taxa de Inatividade: {row[5]}%")
        print()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_inactive_by_city()
