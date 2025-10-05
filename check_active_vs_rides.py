import psycopg2
import json

DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def check_active_drivers():
    """Verifica motoristas ATIVOS (status != unknown) vs motoristas com corridas no período"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("="*80)
    print("COMPARAÇÃO: MOTORISTAS ATIVOS vs MOTORISTAS COM CORRIDAS")
    print("="*80)
    print()
    
    # 1. Total de motoristas por status (ATIVOS = status válido)
    print("1️⃣  MOTORISTAS POR STATUS (DEFINIÇÃO DE 'ATIVOS'):\n")
    
    status_query = """
        SELECT 
            CASE 
                WHEN personal_data->>'status' IN ('online', 'offline', 'busy', 'active') THEN 'ATIVOS'
                ELSE 'UNKNOWN/INATIVOS'
            END as categoria_status,
            personal_data->>'status' as status,
            COUNT(*) as quantidade
        FROM driver_personal_details
        GROUP BY personal_data->>'status'
        ORDER BY quantidade DESC;
    """
    
    cursor.execute(status_query)
    status_results = cursor.fetchall()
    
    total_ativos = 0
    total_unknown = 0
    
    print("   Categoria          | Status      | Quantidade")
    print("   " + "-"*55)
    for row in status_results:
        print(f"   {row[0]:18s} | {row[1] or 'NULL':11s} | {row[2]:10d}")
        if row[0] == 'ATIVOS':
            total_ativos += row[2]
        else:
            total_unknown += row[2]
    
    print("   " + "-"*55)
    print(f"   {'TOTAL ATIVOS':18s} | {'':11s} | {total_ativos:10d}")
    print(f"   {'TOTAL UNKNOWN':18s} | {'':11s} | {total_unknown:10d}")
    print(f"   {'TOTAL GERAL':18s} | {'':11s} | {total_ativos + total_unknown:10d}")
    print()
    print("   ⚠️  DEFINIÇÃO DE 'ATIVOS': Status em ['online', 'offline', 'busy', 'active']")
    print("   ⚠️  'UNKNOWN/INATIVOS': Status NULL ou qualquer outro valor")
    print()
    print("="*80)
    print()
    
    # 2. Motoristas com corridas nos últimos 6 meses
    print("2️⃣  MOTORISTAS COM CORRIDAS NOS ÚLTIMOS 6 MESES:\n")
    
    rides_6months_query = """
        WITH rides_data AS (
            SELECT 
                d.driver_id,
                d.personal_data->>'driver_name' as driver_name,
                d.personal_data->>'status' as status,
                jsonb_array_elements(d.rides_history) as ride
            FROM driver_personal_details d
            WHERE jsonb_array_length(d.rides_history) > 0
        ),
        filtered_rides AS (
            SELECT 
                driver_id,
                driver_name,
                status,
                ride,
                CASE 
                    WHEN (ride->>'drop_time') ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4} : [0-9]{1,2}:[0-9]{2} am$' 
                    THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH12:MI am')
                    WHEN (ride->>'drop_time') ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4} : [0-9]{1,2}:[0-9]{2} pm$' 
                    THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH12:MI pm')
                END as drop_timestamp
            FROM rides_data
        )
        SELECT 
            COUNT(DISTINCT driver_id) as motoristas_com_corridas,
            COUNT(*) as total_corridas,
            COUNT(DISTINCT CASE WHEN status IN ('online', 'offline', 'busy', 'active') THEN driver_id END) as ativos_com_corridas,
            COUNT(DISTINCT CASE WHEN status NOT IN ('online', 'offline', 'busy', 'active') OR status IS NULL THEN driver_id END) as unknown_com_corridas
        FROM filtered_rides
        WHERE drop_timestamp IS NOT NULL 
            AND drop_timestamp >= NOW() - INTERVAL '180 days';
    """
    
    cursor.execute(rides_6months_query)
    result = cursor.fetchone()
    
    print(f"   Total de motoristas com corridas (últimos 6 meses): {result[0]}")
    print(f"   Total de corridas (últimos 6 meses): {result[1]}")
    print()
    print(f"   └─ ATIVOS com corridas: {result[2]}")
    print(f"   └─ UNKNOWN/INATIVOS com corridas: {result[3]}")
    print()
    print("="*80)
    print()
    
    # 3. Breakdown detalhado
    print("3️⃣  BREAKDOWN DETALHADO:\n")
    
    breakdown_query = """
        WITH motoristas_info AS (
            SELECT 
                d.driver_id,
                d.personal_data->>'driver_name' as driver_name,
                d.personal_data->>'status' as status,
                jsonb_array_length(d.rides_history) as total_corridas_historico,
                CASE 
                    WHEN d.personal_data->>'status' IN ('online', 'offline', 'busy', 'active') THEN 'ATIVO'
                    ELSE 'UNKNOWN/INATIVO'
                END as categoria_status
            FROM driver_personal_details d
        )
        SELECT 
            categoria_status,
            COUNT(*) as quantidade_motoristas,
            SUM(total_corridas_historico) as total_corridas_historico,
            AVG(total_corridas_historico) as media_corridas
        FROM motoristas_info
        GROUP BY categoria_status
        ORDER BY quantidade_motoristas DESC;
    """
    
    cursor.execute(breakdown_query)
    breakdown = cursor.fetchall()
    
    print("   Categoria Status    | Motoristas | Total Corridas | Média Corridas/Motorista")
    print("   " + "-"*80)
    for row in breakdown:
        avg_corridas = row[3] if row[3] else 0
        print(f"   {row[0]:19s} | {row[1]:10d} | {row[2]:14d} | {avg_corridas:7.1f}")
    
    print()
    print("="*80)
    print()
    
    # 4. CONCLUSÃO
    print("4️⃣  CONCLUSÃO E CORREÇÃO NECESSÁRIA:\n")
    print(f"   📊 KPI mostra: 42 ATIVOS (status != unknown)")
    print(f"   📊 Performance Metrics mostra: 24 motoristas com corridas nos últimos 6 meses")
    print()
    print("   🔴 PROBLEMA IDENTIFICADO:")
    print("      O card 'Motoristas Ativos' no Performance Metrics está usando")
    print("      'motoristas_com_corridas_no_periodo' ao invés de 'motoristas_ativos_por_status'")
    print()
    print("   ✅ CORREÇÃO:")
    print("      Deve buscar o total de motoristas ATIVOS do endpoint /drivers/dashboard")
    print(f"      que considera status em ['online', 'offline', 'busy', 'active'] = {total_ativos}")
    print()
    print("="*80)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_active_drivers()
