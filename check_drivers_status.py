#!/usr/bin/env python3

import psycopg2
import json
from datetime import datetime

# Configuração da base de dados
DB_CONFIG = {
    'host': '148.230.73.27',
    'database': 'matupa_db',
    'user': 'postgres',
    'password': 'postgres'
}

def check_drivers_status():
    try:
        # Conectar à base de dados
        print("🔗 Conectando à base de dados...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela drivers_data
        print("\n📊 Verificando estrutura da tabela drivers_data...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'drivers_data'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("Colunas na tabela drivers_data:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        # Verificar alguns registros para ver o campo additional_data
        print("\n🔍 Verificando registros da tabela drivers_data...")
        cursor.execute("""
            SELECT id, additional_data
            FROM drivers_data 
            LIMIT 5;
        """)
        records = cursor.fetchall()
        
        print(f"\nEncontrados {len(records)} registros:")
        for record in records:
            driver_id, additional_data = record
            print(f"\n--- Driver ID: {driver_id} ---")
            
            if additional_data:
                if isinstance(additional_data, str):
                    try:
                        data = json.loads(additional_data)
                        print(f"Additional data (JSON): {json.dumps(data, indent=2)}")
                        
                        # Verificar se é uma lista e tem índice 5
                        if isinstance(data, list) and len(data) > 5:
                            print(f"Índice 5: {data[5]}")
                            # Verificar se o índice 5 tem Status
                            if isinstance(data[5], dict) and 'Status' in data[5]:
                                print(f"✓ ENCONTRADO Status no índice 5: {data[5]['Status']}")
                            elif isinstance(data[5], str) and 'Status' in data[5]:
                                print(f"✓ ENCONTRADO Status no índice 5 (string): {data[5]}")
                        
                    except json.JSONDecodeError:
                        print(f"Additional data (raw): {additional_data}")
                elif isinstance(additional_data, list):
                    print(f"Additional data (list): {additional_data}")
                    if len(additional_data) > 5:
                        print(f"Índice 5: {additional_data[5]}")
                        if isinstance(additional_data[5], dict) and 'Status' in additional_data[5]:
                            print(f"✓ ENCONTRADO Status no índice 5: {additional_data[5]['Status']}")
                else:
                    print(f"Additional data (type: {type(additional_data)}): {additional_data}")
            else:
                print("Additional data: NULL")
        
        # Contar quantos drivers têm Status Online vs Offline
        print("\n📈 Contando drivers por Status...")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN additional_data IS NOT NULL AND 
                         json_array_length(additional_data::json) > 5 AND
                         additional_data::json->5->>'Status' IS NOT NULL
                    THEN additional_data::json->5->>'Status'
                    ELSE 'Unknown'
                END as status,
                COUNT(*) as total
            FROM drivers_data
            GROUP BY status
            ORDER BY total DESC;
        """)
        
        status_counts = cursor.fetchall()
        print("Contagem por Status:")
        for status, count in status_counts:
            print(f"  {status}: {count} motoristas")
        
        cursor.close()
        conn.close()
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_drivers_status()