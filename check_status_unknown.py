#!/usr/bin/env python3

import psycopg2
import json
from datetime import datetime

def check_status_in_database():
    try:
        # Usando as credenciais corretas do arquivo db.py
        print("🔗 Conectando à base de dados...")
        
        # Credenciais corretas da aplicação
        db_config = {
            'host': '148.230.73.27',
            'database': 'n8n_db',
            'user': 'n8n_user',
            'password': 'n8n_pw'
        }
        
        print(f"Conectando com database: {db_config['database']}")
        conn = psycopg2.connect(**db_config)
        print(f"✅ Conectado com sucesso!")
            
        cursor = conn.cursor()
        
        # Verificar registros ESPECÍFICOS da aba Active Drivers
        print("\n📊 Analisando registros da aba 'Active Drivers'...")
        cursor.execute("""
            SELECT id, driver_id, name, additional_data::text, page_source
            FROM drivers_data 
            WHERE additional_data IS NOT NULL
            AND page_source = 'Active Drivers'
            ORDER BY scraped_at DESC
            LIMIT 20;
        """)
        
        records = cursor.fetchall()
        print(f"\n🔍 Analisando {len(records)} registros da aba Active Drivers:")
        
        status_found = {}
        
        for record in records:
            record_id, driver_id, name, additional_data_str, page_source = record
            
            print(f"\n--- Record ID: {record_id}, Driver: {driver_id} ({name}) ---")
            print(f"Page Source: {page_source}")
            
            if additional_data_str:
                try:
                    # Parse do JSON direto (não é array, é objeto)
                    additional_data = json.loads(additional_data_str)
                    
                    if isinstance(additional_data, dict):
                        print("✅ É um objeto JSON direto:")
                        
                        # Verificar campo Status
                        if 'Status' in additional_data:
                            status = additional_data['Status']
                            print(f"✅ ENCONTRADO Status: '{status}'")
                            status_found[status] = status_found.get(status, 0) + 1
                            
                            # Mostrar alguns outros campos importantes
                            city = additional_data.get('City', 'N/A')
                            last_login = additional_data.get('Last Login', 'N/A')
                            driver_name = additional_data.get('Driver Name', 'N/A')
                            print(f"   - City: {city}")
                            print(f"   - Driver Name: {driver_name}")
                            print(f"   - Last Login: {last_login}")
                        else:
                            print("❌ Campo 'Status' NÃO encontrado no objeto Active Drivers!")
                            print(f"Campos disponíveis: {list(additional_data.keys())}")
                    
                    else:
                        print(f"❌ Tipo inesperado: {type(additional_data)}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao fazer parse do JSON: {e}")
                    print(f"Raw data: {additional_data_str[:200]}...")
            else:
                print("❌ additional_data é NULL")
        
        # Resumo dos Status encontrados na aba Active Drivers
        print(f"\n📈 RESUMO DOS STATUS NA ABA 'Active Drivers':")
        for status, count in status_found.items():
            print(f"  '{status}': {count} ocorrências")
        
        if not status_found:
            print("❌ Nenhum campo 'Status' foi encontrado na aba Active Drivers!")
        
        # Verificar quantos registros de Active Drivers existem vs têm Status
        print(f"\n🔢 CONTAGEM ESPECÍFICA DA ABA 'Active Drivers':")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_active_drivers,
                COUNT(CASE 
                    WHEN additional_data IS NOT NULL AND 
                         additional_data::jsonb ? 'Status'
                    THEN 1 END) as has_status_field
            FROM drivers_data
            WHERE page_source = 'Active Drivers';
        """)
        
        count_result = cursor.fetchone()
        total_active, has_status = count_result
        
        print(f"  Total de registros 'Active Drivers': {total_active}")
        print(f"  Com campo Status: {has_status}")
        print(f"  Sem campo Status: {total_active - has_status}")
        
        # Mostrar distribuição de Status na aba Active Drivers
        print(f"\n📊 DISTRIBUIÇÃO DE STATUS NA ABA 'Active Drivers':")
        cursor.execute("""
            SELECT 
                additional_data->>'Status' as status_value,
                COUNT(*) as count
            FROM drivers_data
            WHERE page_source = 'Active Drivers'
            AND additional_data IS NOT NULL
            AND additional_data::jsonb ? 'Status'
            GROUP BY additional_data->>'Status'
            ORDER BY count DESC;
        """)
        
        status_distribution = cursor.fetchall()
        for status_val, count in status_distribution:
            print(f"  Status '{status_val}': {count} motoristas")
        
        cursor.close()
        conn.close()
        print("\n✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_status_in_database()