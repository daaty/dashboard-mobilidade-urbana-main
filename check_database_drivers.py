"""
Script para verificar dados reais na tabela drivers_data do PostgreSQL
"""

import os
import psycopg2
import json
from datetime import datetime

def check_drivers_data():
    # String de conexão
    DATABASE_URL = "postgresql://postgres:kQc1HUdJxW7g6e9F76bFy1U9y3T4C3Wl@autorack.proxy.rlwy.net:20565/railway"
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔗 Conectado ao PostgreSQL!")
        
        # Verificar estrutura da tabela
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'drivers_data'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📊 Estrutura da tabela drivers_data:")
        for col, dtype in columns:
            print(f"  - {col}: {dtype}")
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM drivers_data;")
        total_count = cursor.fetchone()[0]
        print(f"\n📈 Total de registros: {total_count}")
        
        # Buscar alguns registros para análise
        cursor.execute("""
            SELECT driver_id, driver_name, additional_data 
            FROM drivers_data 
            LIMIT 5;
        """)
        
        records = cursor.fetchall()
        print(f"\n🔍 Primeiros 5 registros:")
        
        for i, (driver_id, driver_name, additional_data) in enumerate(records, 1):
            print(f"\n--- Registro {i} ---")
            print(f"Driver ID: {driver_id}")
            print(f"Driver Name: {driver_name}")
            
            if additional_data:
                try:
                    data = json.loads(additional_data) if isinstance(additional_data, str) else additional_data
                    print(f"Additional Data structure:")
                    
                    # Verificar as chaves principais
                    if isinstance(data, dict):
                        print(f"  - Chaves principais: {list(data.keys())}")
                        
                        # Verificar se tem métricas
                        if 'metrics' in data:
                            print(f"  - Métricas: {data['metrics']}")
                        
                        # Verificar se tem raw_data
                        if 'raw_data' in data:
                            raw = data['raw_data']
                            print(f"  - Raw Data keys: {list(raw.keys()) if isinstance(raw, dict) else 'Não é dict'}")
                            if isinstance(raw, dict):
                                print(f"  - Online Hours: {raw.get('Online Hours', 'N/A')}")
                                print(f"  - Total Rides: {raw.get('Total Rides', 'N/A')}")
                                print(f"  - Success Rides: {raw.get('Success Rides', 'N/A')}")
                        
                        # Verificar se tem profile
                        if 'profile' in data:
                            print(f"  - Profile: {data['profile']}")
                    else:
                        print(f"  - Additional Data não é um dict: {type(data)}")
                
                except Exception as e:
                    print(f"  - Erro ao parsear JSON: {e}")
                    print(f"  - Raw additional_data: {additional_data[:200]}...")
            else:
                print(f"  - Additional Data: NULL")
        
        # Verificar motoristas únicos
        cursor.execute("""
            SELECT COUNT(DISTINCT driver_id) as unique_drivers,
                   COUNT(DISTINCT driver_name) as unique_names
            FROM drivers_data;
        """)
        
        unique_stats = cursor.fetchone()
        print(f"\n📊 Estatísticas:")
        print(f"  - Motoristas únicos (ID): {unique_stats[0]}")
        print(f"  - Nomes únicos: {unique_stats[1]}")
        
        # Verificar dados mais recentes
        cursor.execute("""
            SELECT driver_name, additional_data->>'import_info' as import_info
            FROM drivers_data 
            WHERE additional_data->>'import_info' IS NOT NULL
            ORDER BY (additional_data->'import_info'->>'import_timestamp')::timestamp DESC
            LIMIT 3;
        """)
        
        recent = cursor.fetchall()
        print(f"\n⏰ Dados mais recentes:")
        for name, import_info in recent:
            print(f"  - {name}: {import_info}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_drivers_data()
