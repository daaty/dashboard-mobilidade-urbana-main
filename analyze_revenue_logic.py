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

def analyze_revenue_calculation():
    """Analisa em detalhe como a receita está sendo calculada"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("="*80)
    print("ANÁLISE DETALHADA DO CÁLCULO DE RECEITA")
    print("="*80)
    print()
    
    # 1. Verificar TODAS as corridas e seus valores de fare
    print("1️⃣  ANÁLISE DE VALORES DE FARE (RECEITA):\n")
    
    fare_analysis_query = """
        WITH rides_expanded AS (
            SELECT 
                d.driver_id,
                d.personal_data->>'driver_name' as driver_name,
                jsonb_array_elements(d.rides_history) as ride
            FROM driver_personal_details d
            WHERE jsonb_array_length(d.rides_history) > 0
        )
        SELECT 
            COUNT(*) as total_rides,
            COUNT(CASE WHEN ride->>'fare' IS NOT NULL AND ride->>'fare' != '' THEN 1 END) as rides_with_fare,
            COUNT(CASE WHEN ride->>'fare' IS NULL OR ride->>'fare' = '' THEN 1 END) as rides_without_fare,
            SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue,
            AVG(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as avg_fare,
            MIN(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as min_fare,
            MAX(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as max_fare,
            COUNT(DISTINCT driver_id) as total_drivers
        FROM rides_expanded;
    """
    
    cursor.execute(fare_analysis_query)
    result = cursor.fetchone()
    
    print(f"   Total de corridas no banco: {result[0]}")
    print(f"   Corridas COM valor de fare: {result[1]}")
    print(f"   Corridas SEM valor de fare: {result[2]}")
    print(f"   Total de motoristas: {result[7]}")
    print()
    print(f"   💰 RECEITA TOTAL (SUM de todos os fares): R$ {result[3]:.2f}" if result[3] else "   💰 RECEITA TOTAL: R$ 0.00")
    print(f"   📊 Ticket médio (AVG): R$ {result[4]:.2f}" if result[4] else "   📊 Ticket médio: R$ 0.00")
    print(f"   ⬇️  Menor fare: R$ {result[5]:.2f}" if result[5] else "   ⬇️  Menor fare: N/A")
    print(f"   ⬆️  Maior fare: R$ {result[6]:.2f}" if result[6] else "   ⬆️  Maior fare: N/A")
    print()
    print(f"   ➗ RECEITA POR MOTORISTA: R$ {result[3]/result[7]:.2f}" if result[3] and result[7] else "   ➗ RECEITA POR MOTORISTA: R$ 0.00")
    print()
    print("   LÓGICA DO CÁLCULO:")
    print("   • SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) = Soma todos os valores de 'fare'")
    print("   • NULLIF(ride->>'fare', '') = Trata strings vazias como NULL")
    print("   • CAST(...AS FLOAT) = Converte string para número")
    print()
    print("-"*80)
    print()
    
    # 2. Verificar alguns exemplos de corridas
    print("2️⃣  EXEMPLOS DE CORRIDAS E SEUS VALORES:\n")
    
    sample_rides_query = """
        WITH rides_expanded AS (
            SELECT 
                d.personal_data->>'driver_name' as driver_name,
                ride->>'fare' as fare,
                ride->>'drop_time' as drop_time,
                ride->>'duration' as duration
            FROM driver_personal_details d,
                 jsonb_array_elements(d.rides_history) as ride
            WHERE jsonb_array_length(d.rides_history) > 0
        )
        SELECT 
            driver_name,
            fare,
            drop_time,
            duration
        FROM rides_expanded
        WHERE fare IS NOT NULL AND fare != ''
        ORDER BY CAST(fare AS FLOAT) DESC
        LIMIT 10;
    """
    
    cursor.execute(sample_rides_query)
    samples = cursor.fetchall()
    
    print("   Top 10 corridas com MAIOR valor de fare:")
    for i, row in enumerate(samples, 1):
        print(f"   {i:2d}. {row[0]:30s} | R$ {float(row[1]):7.2f} | {row[2]} | {row[3]} min")
    print()
    print("-"*80)
    print()
    
    # 3. Distribuição de valores de fare
    print("3️⃣  DISTRIBUIÇÃO DE VALORES DE FARE:\n")
    
    distribution_query = """
        WITH rides_expanded AS (
            SELECT 
                CAST(NULLIF(ride->>'fare', '') AS FLOAT) as fare
            FROM driver_personal_details d,
                 jsonb_array_elements(d.rides_history) as ride
            WHERE jsonb_array_length(d.rides_history) > 0
                AND ride->>'fare' IS NOT NULL 
                AND ride->>'fare' != ''
        )
        SELECT 
            CASE 
                WHEN fare >= 50 THEN '≥ R$ 50'
                WHEN fare >= 30 THEN 'R$ 30-49'
                WHEN fare >= 20 THEN 'R$ 20-29'
                WHEN fare >= 10 THEN 'R$ 10-19'
                WHEN fare >= 5 THEN 'R$ 5-9'
                ELSE '< R$ 5'
            END as faixa_preco,
            COUNT(*) as quantidade,
            SUM(fare) as receita_faixa,
            AVG(fare) as media_faixa
        FROM rides_expanded
        GROUP BY faixa_preco
        ORDER BY media_faixa DESC;
    """
    
    cursor.execute(distribution_query)
    distribution = cursor.fetchall()
    
    print("   Faixa de Preço    | Quantidade | Receita da Faixa | Média da Faixa")
    print("   " + "-"*70)
    total_dist = 0
    total_revenue_dist = 0
    for row in distribution:
        total_dist += row[1]
        total_revenue_dist += row[2]
        print(f"   {row[0]:17s} | {row[1]:10d} | R$ {row[2]:13.2f} | R$ {row[3]:6.2f}")
    print("   " + "-"*70)
    print(f"   {'TOTAL':17s} | {total_dist:10d} | R$ {total_revenue_dist:13.2f} |")
    print()
    print("-"*80)
    print()
    
    # 4. Receita por motorista
    print("4️⃣  RECEITA POR MOTORISTA (Top 5):\n")
    
    revenue_by_driver_query = """
        WITH driver_revenue AS (
            SELECT 
                d.personal_data->>'driver_name' as driver_name,
                COUNT(*) as total_rides,
                SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue
            FROM driver_personal_details d,
                 jsonb_array_elements(d.rides_history) as ride
            WHERE jsonb_array_length(d.rides_history) > 0
            GROUP BY d.personal_data->>'driver_name'
        )
        SELECT 
            driver_name,
            total_rides,
            total_revenue,
            total_revenue / total_rides as avg_per_ride
        FROM driver_revenue
        WHERE total_revenue IS NOT NULL
        ORDER BY total_revenue DESC
        LIMIT 5;
    """
    
    cursor.execute(revenue_by_driver_query)
    top_drivers = cursor.fetchall()
    
    print("   Motorista                      | Corridas | Receita Total | Média/Corrida")
    print("   " + "-"*75)
    for row in top_drivers:
        print(f"   {row[0]:30s} | {row[1]:8d} | R$ {row[2]:11.2f} | R$ {row[3]:7.2f}")
    print()
    print("-"*80)
    print()
    
    # 5. Verificação de dados nulos ou vazios
    print("5️⃣  VERIFICAÇÃO DE DADOS NULOS/VAZIOS:\n")
    
    null_check_query = """
        WITH rides_expanded AS (
            SELECT 
                ride->>'fare' as fare_raw
            FROM driver_personal_details d,
                 jsonb_array_elements(d.rides_history) as ride
            WHERE jsonb_array_length(d.rides_history) > 0
        )
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN fare_raw IS NULL THEN 1 END) as null_count,
            COUNT(CASE WHEN fare_raw = '' THEN 1 END) as empty_string_count,
            COUNT(CASE WHEN fare_raw = '0' THEN 1 END) as zero_count,
            COUNT(CASE WHEN fare_raw IS NOT NULL AND fare_raw != '' AND fare_raw != '0' THEN 1 END) as valid_count
        FROM rides_expanded;
    """
    
    cursor.execute(null_check_query)
    null_check = cursor.fetchone()
    
    print(f"   Total de corridas: {null_check[0]}")
    print(f"   Fares NULL: {null_check[1]}")
    print(f"   Fares string vazia (''): {null_check[2]}")
    print(f"   Fares = '0': {null_check[3]}")
    print(f"   Fares VÁLIDOS (com valor): {null_check[4]}")
    print()
    print("="*80)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_revenue_calculation()
