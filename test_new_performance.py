import psycopg2
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def test_new_performance_metrics():
    """Testa novo endpoint de performance com métricas reais"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=== Testando Novas Métricas de Performance ===\n")
    
    # Query principal
    query = """
        WITH rides_data AS (
            SELECT 
                d.driver_id,
                d.personal_data->>'driver_name' as driver_name,
                jsonb_array_elements(d.rides_history) as ride
            FROM driver_personal_details d
            WHERE d.rides_history IS NOT NULL 
                AND jsonb_array_length(d.rides_history) > 0
        )
        SELECT 
            COUNT(*) as total_rides,
            COUNT(DISTINCT driver_id) as total_drivers,
            SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue,
            AVG(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as avg_ticket,
            SUM(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as total_duration_minutes,
            AVG(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as avg_duration_minutes,
            SUM(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as total_distance_km,
            AVG(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as avg_distance_km
        FROM rides_data;
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    print("📊 MÉTRICAS PRINCIPAIS:")
    print(f"   Total de Corridas: {result[0]}")
    print(f"   Total de Motoristas: {result[1]}")
    print(f"   Receita Total: R$ {result[2]:.2f}" if result[2] else "   Receita Total: R$ 0.00")
    print(f"   Ticket Médio: R$ {result[3]:.2f}" if result[3] else "   Ticket Médio: R$ 0.00")
    print(f"   Tempo Total em Corrida: {result[4]/60:.2f}h" if result[4] else "   Tempo Total: 0h")
    print(f"   Duração Média: {result[5]:.1f} min" if result[5] else "   Duração Média: 0 min")
    print(f"   Distância Total: {result[6]:.2f} km" if result[6] else "   Distância Total: 0 km")
    print(f"   Distância Média: {result[7]:.2f} km/corrida" if result[7] else "   Distância Média: 0 km")
    print(f"\n   Média de corridas por motorista: {result[0]/result[1]:.1f}")
    print(f"   Receita por motorista: R$ {result[2]/result[1]:.2f}" if result[2] else "   Receita por motorista: R$ 0.00")
    print("\n" + "="*60 + "\n")
    
    # Distribuição de corridas
    dist_query = """
        WITH driver_rides AS (
            SELECT 
                d.driver_id,
                jsonb_array_length(d.rides_history) as total_rides
            FROM driver_personal_details d
            WHERE jsonb_array_length(d.rides_history) > 0
        )
        SELECT 
            CASE 
                WHEN total_rides >= 50 THEN '50+ corridas'
                WHEN total_rides >= 20 THEN '20-49 corridas'
                WHEN total_rides >= 10 THEN '10-19 corridas'
                WHEN total_rides >= 5 THEN '5-9 corridas'
                ELSE '1-4 corridas'
            END as faixa_corridas,
            COUNT(*) as quantidade_motoristas
        FROM driver_rides
        GROUP BY faixa_corridas
        ORDER BY quantidade_motoristas DESC;
    """
    
    cursor.execute(dist_query)
    dist_result = cursor.fetchall()
    
    print("📈 DISTRIBUIÇÃO DE CORRIDAS POR MOTORISTA:")
    for row in dist_result:
        print(f"   {row[0]}: {row[1]} motoristas")
    print("\n" + "="*60 + "\n")
    
    # Período do dia
    period_query = """
        WITH rides_expanded AS (
            SELECT 
                jsonb_array_elements(rides_history) as ride
            FROM driver_personal_details
            WHERE jsonb_array_length(rides_history) > 0
        )
        SELECT 
            CASE 
                WHEN ride->>'drop_time' LIKE '%am%' THEN 'Manhã (AM)'
                WHEN ride->>'drop_time' LIKE '%pm%' THEN 'Tarde/Noite (PM)'
                ELSE 'Não identificado'
            END as periodo,
            COUNT(*) as quantidade
        FROM rides_expanded
        WHERE ride->>'drop_time' IS NOT NULL
        GROUP BY periodo
        ORDER BY quantidade DESC;
    """
    
    cursor.execute(period_query)
    period_result = cursor.fetchall()
    
    print("🕐 DISTRIBUIÇÃO POR PERÍODO DO DIA:")
    for row in period_result:
        pct = (row[1] / sum([r[1] for r in period_result]) * 100)
        print(f"   {row[0]}: {row[1]} corridas ({pct:.1f}%)")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_new_performance_metrics()
