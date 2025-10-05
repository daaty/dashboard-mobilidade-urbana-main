import psycopg2
import json
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def analyze_rides_data():
    """Analisa dados disponíveis no rides_history para propor métricas melhores"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=== ANÁLISE DOS DADOS DE CORRIDAS ===\n")
    
    # 1. Verificar campos disponíveis em rides_history
    query = """
        SELECT 
            rides_history->0 as sample_ride
        FROM driver_personal_details
        WHERE jsonb_array_length(rides_history) > 0
        LIMIT 1;
    """
    
    cursor.execute(query)
    sample = cursor.fetchone()
    
    if sample:
        ride_data = sample[0]
        print("1. CAMPOS DISPONÍVEIS EM CADA CORRIDA:")
        print(json.dumps(ride_data, indent=2))
        print("\n" + "="*60 + "\n")
    
    # 2. Estatísticas gerais
    stats_query = """
        WITH rides_data AS (
            SELECT 
                d.driver_id,
                d.personal_data->>'driver_name' as driver_name,
                jsonb_array_length(d.rides_history) as total_rides,
                d.rides_history
            FROM driver_personal_details d
            WHERE jsonb_array_length(d.rides_history) > 0
        )
        SELECT 
            COUNT(DISTINCT driver_id) as motoristas_com_corridas,
            SUM(total_rides) as total_corridas,
            AVG(total_rides) as media_corridas_por_motorista,
            MAX(total_rides) as max_corridas_motorista,
            MIN(total_rides) as min_corridas_motorista
        FROM rides_data;
    """
    
    cursor.execute(stats_query)
    stats = cursor.fetchone()
    
    print("2. ESTATÍSTICAS GERAIS:")
    print(f"   Motoristas com corridas: {stats[0]}")
    print(f"   Total de corridas: {stats[1]}")
    print(f"   Média de corridas por motorista: {stats[2]:.1f}")
    print(f"   Máximo de corridas (1 motorista): {stats[3]}")
    print(f"   Mínimo de corridas: {stats[4]}")
    print("\n" + "="*60 + "\n")
    
    # 3. Analisar valores de fare (receita)
    fare_query = """
        WITH rides_expanded AS (
            SELECT 
                jsonb_array_elements(rides_history) as ride
            FROM driver_personal_details
            WHERE jsonb_array_length(rides_history) > 0
            LIMIT 100
        )
        SELECT 
            COUNT(*) as total_rides,
            SUM(CAST(ride->>'fare' AS FLOAT)) as total_revenue,
            AVG(CAST(ride->>'fare' AS FLOAT)) as avg_fare,
            MAX(CAST(ride->>'fare' AS FLOAT)) as max_fare,
            MIN(CAST(ride->>'fare' AS FLOAT)) as min_fare
        FROM rides_expanded
        WHERE ride->>'fare' IS NOT NULL;
    """
    
    cursor.execute(fare_query)
    fare_stats = cursor.fetchone()
    
    print("3. ANÁLISE DE RECEITA (FARE):")
    print(f"   Total de corridas analisadas: {fare_stats[0]}")
    print(f"   Receita total: R$ {fare_stats[1]:.2f}")
    print(f"   Ticket médio: R$ {fare_stats[2]:.2f}")
    print(f"   Maior valor: R$ {fare_stats[3]:.2f}")
    print(f"   Menor valor: R$ {fare_stats[4]:.2f}")
    print("\n" + "="*60 + "\n")
    
    # 4. Analisar duração das corridas
    duration_query = """
        WITH rides_expanded AS (
            SELECT 
                jsonb_array_elements(rides_history) as ride
            FROM driver_personal_details
            WHERE jsonb_array_length(rides_history) > 0
            LIMIT 100
        )
        SELECT 
            AVG(CAST(ride->>'duration' AS FLOAT)) as avg_duration_min,
            MAX(CAST(ride->>'duration' AS FLOAT)) as max_duration_min,
            MIN(CAST(ride->>'duration' AS FLOAT)) as min_duration_min
        FROM rides_expanded
        WHERE ride->>'duration' IS NOT NULL;
    """
    
    cursor.execute(duration_query)
    duration_stats = cursor.fetchone()
    
    print("4. ANÁLISE DE DURAÇÃO DAS CORRIDAS:")
    print(f"   Duração média: {duration_stats[0]:.1f} minutos ({duration_stats[0]/60:.2f} horas)")
    print(f"   Duração máxima: {duration_stats[1]:.1f} minutos")
    print(f"   Duração mínima: {duration_stats[2]:.1f} minutos")
    print("\n" + "="*60 + "\n")
    
    # 5. Análise de distribuição por período do dia
    period_query = """
        WITH rides_expanded AS (
            SELECT 
                jsonb_array_elements(rides_history) as ride
            FROM driver_personal_details
            WHERE jsonb_array_length(rides_history) > 0
            LIMIT 200
        ),
        rides_with_hour AS (
            SELECT 
                ride->>'drop_time' as drop_time,
                CASE 
                    WHEN ride->>'drop_time' LIKE '%am%' THEN 'Manhã/Madrugada'
                    WHEN ride->>'drop_time' LIKE '%pm%' THEN 'Tarde/Noite'
                    ELSE 'Desconhecido'
                END as periodo
            FROM rides_expanded
            WHERE ride->>'drop_time' IS NOT NULL
        )
        SELECT 
            periodo,
            COUNT(*) as quantidade
        FROM rides_with_hour
        GROUP BY periodo
        ORDER BY quantidade DESC;
    """
    
    cursor.execute(period_query)
    period_stats = cursor.fetchall()
    
    print("5. DISTRIBUIÇÃO POR PERÍODO DO DIA:")
    for row in period_stats:
        print(f"   {row[0]}: {row[1]} corridas")
    print("\n" + "="*60 + "\n")
    
    # 6. Top motoristas por receita
    top_revenue_query = """
        WITH driver_revenue AS (
            SELECT 
                d.personal_data->>'driver_name' as driver_name,
                SUM(CAST(ride->>'fare' AS FLOAT)) as total_revenue,
                COUNT(*) as total_rides
            FROM driver_personal_details d,
                 jsonb_array_elements(d.rides_history) as ride
            WHERE ride->>'fare' IS NOT NULL
            GROUP BY d.personal_data->>'driver_name'
        )
        SELECT 
            driver_name,
            total_revenue,
            total_rides,
            CAST(total_revenue / total_rides AS DECIMAL(10,2)) as avg_ticket
        FROM driver_revenue
        ORDER BY total_revenue DESC
        LIMIT 5;
    """
    
    cursor.execute(top_revenue_query)
    top_drivers = cursor.fetchall()
    
    print("6. TOP 5 MOTORISTAS POR RECEITA:")
    for i, row in enumerate(top_drivers, 1):
        print(f"   {i}. {row[0]}")
        print(f"      Receita: R$ {row[1]:.2f} | Corridas: {row[2]} | Ticket Médio: R$ {row[3]:.2f}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_rides_data()
