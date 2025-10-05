import psycopg2
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def get_period_date(period):
    """Retorna a data inicial para o filtro de período"""
    now = datetime.now()
    
    if period == 'hoje':
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == '7_days':
        return now - timedelta(days=7)
    elif period == '30_days':
        return now - timedelta(days=30)
    elif period == '3_months':
        return now - timedelta(days=90)
    elif period == '6_months':
        return now - timedelta(days=180)
    elif period == '12_months':
        return now - timedelta(days=365)
    else:
        return None

def test_period_filtering():
    """Testa o cálculo de receita COM diferentes filtros de período"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    periods = ['hoje', '7_days', '30_days', '3_months', '6_months', '12_months', None]
    
    print("="*100)
    print("TESTE DE RECEITA COM DIFERENTES PERÍODOS")
    print("="*100)
    print()
    
    for period in periods:
        period_name = period if period else "SEM FILTRO (TODOS OS DADOS)"
        start_date = get_period_date(period) if period else None
        
        print(f"📅 PERÍODO: {period_name}")
        if start_date:
            print(f"   Data inicial do filtro: {start_date.strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Query com filtro de período (igual ao backend)
        if start_date:
            query = f"""
                WITH rides_data AS (
                    SELECT 
                        d.driver_id,
                        d.personal_data->>'driver_name' as driver_name,
                        jsonb_array_elements(d.rides_history) as ride
                    FROM driver_personal_details d
                    WHERE jsonb_array_length(d.rides_history) > 0
                ),
                filtered_rides AS (
                    SELECT 
                        driver_id,
                        driver_name,
                        ride,
                        CASE 
                            WHEN (ride->>'drop_time') ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}} : [0-9]{{1,2}}:[0-9]{{2}} am$' 
                            THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH12:MI am')
                            WHEN (ride->>'drop_time') ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}} : [0-9]{{1,2}}:[0-9]{{2}} pm$' 
                            THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH12:MI pm')
                        END as drop_timestamp
                    FROM rides_data
                )
                SELECT 
                    COUNT(*) as total_rides,
                    COUNT(DISTINCT driver_id) as total_drivers,
                    SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue,
                    AVG(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as avg_ticket,
                    SUM(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as total_duration_minutes,
                    AVG(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as avg_duration_minutes,
                    SUM(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as total_distance_km,
                    AVG(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as avg_distance_km,
                    COUNT(DISTINCT CASE 
                        WHEN drop_timestamp >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}' 
                        THEN driver_id 
                    END) as active_drivers_period
                FROM filtered_rides
                WHERE drop_timestamp IS NOT NULL 
                    AND drop_timestamp >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}';
            """
        else:
            query = """
                WITH rides_data AS (
                    SELECT 
                        d.driver_id,
                        d.personal_data->>'driver_name' as driver_name,
                        jsonb_array_elements(d.rides_history) as ride
                    FROM driver_personal_details d
                    WHERE jsonb_array_length(d.rides_history) > 0
                )
                SELECT 
                    COUNT(*) as total_rides,
                    COUNT(DISTINCT driver_id) as total_drivers,
                    SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue,
                    AVG(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as avg_ticket,
                    SUM(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as total_duration_minutes,
                    AVG(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as avg_duration_minutes,
                    SUM(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as total_distance_km,
                    AVG(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as avg_distance_km,
                    COUNT(DISTINCT driver_id) as active_drivers_period
                FROM rides_data;
            """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        total_rides = int(result[0]) if result[0] else 0
        total_drivers = int(result[1]) if result[1] else 0
        total_revenue = round(float(result[2]), 2) if result[2] else 0.0
        avg_ticket = round(float(result[3]), 2) if result[3] else 0.0
        total_duration = round(float(result[4]) / 60.0, 2) if result[4] else 0.0
        avg_duration = round(float(result[5]), 1) if result[5] else 0.0
        total_distance = round(float(result[6]), 2) if result[6] else 0.0
        avg_distance = round(float(result[7]), 2) if result[7] else 0.0
        active_drivers = int(result[8]) if result[8] else 0
        
        revenue_per_driver = round(total_revenue / total_drivers, 2) if total_drivers > 0 else 0.0
        
        print(f"   📊 Total de Corridas: {total_rides}")
        print(f"   👥 Total de Motoristas: {total_drivers}")
        print(f"   👥 Motoristas Ativos no Período: {active_drivers}")
        print()
        print(f"   💰 RECEITA TOTAL: R$ {total_revenue:.2f}")
        print(f"   💵 RECEITA POR MOTORISTA: R$ {revenue_per_driver:.2f}")
        print(f"   🎫 Ticket Médio: R$ {avg_ticket:.2f}")
        print()
        print(f"   ⏱️  Tempo Total: {total_duration:.2f}h")
        print(f"   ⏱️  Duração Média: {avg_duration:.1f} min")
        print()
        print(f"   📏 Distância Total: {total_distance:.2f} km")
        print(f"   📏 Distância Média: {avg_distance:.2f} km")
        print()
        print("   " + "="*96)
        print()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_period_filtering()
