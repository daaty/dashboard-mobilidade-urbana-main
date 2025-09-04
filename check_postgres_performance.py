import psycopg2
import json

try:
    conn = psycopg2.connect(
        host='148.230.73.27',
        database='n8n_db',
        user='n8n_user',
        password='n8n_pw',
        port=5432
    )
    cur = conn.cursor()

    # Verificar se MARCOS LEITE FERREIRA está na tabela driver_personal_details
    cur.execute("""
    SELECT 
        dd.driver_id,
        dd.name,
        CASE WHEN dpd.driver_id IS NOT NULL THEN 'SIM' ELSE 'NÃO' END as tem_personal_details
    FROM drivers_data dd
    LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
    WHERE dd.name LIKE '%MARCOS%LEITE%'
    AND dd.page_source = 'Driver Performance'
    GROUP BY dd.driver_id, dd.name, dpd.driver_id
    """)

    results = cur.fetchall()
    print('=== MARCOS LEITE FERREIRA - VERIFICAÇÃO ===')
    print(f'Total de registros: {len(results)}')
    
    for driver_id, name, tem_personal_details in results:
        print(f'{name} (ID: {driver_id}): Tem dados pessoais? {tem_personal_details}')

    conn.close()
    
except Exception as e:
    print(f'Erro: {e}')
