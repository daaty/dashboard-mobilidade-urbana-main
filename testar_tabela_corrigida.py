#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import json
from datetime import datetime

def testar_tabela_drivers():
    """Testar a estrutura da tabela drivers_data após correção"""
    try:
        # Conectar ao PostgreSQL na VPS
        DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("🔍 TESTANDO TABELA DRIVERS_DATA CORRIGIDA")
        print("=" * 80)
        
        # Verificar total de registros
        cursor.execute("SELECT COUNT(*) FROM drivers_data")
        total = cursor.fetchone()[0]
        print(f"📊 Total de registros: {total}")
        
        # Verificar estrutura dos campos principais
        cursor.execute("""
            SELECT 
                id,
                driver_id, 
                name, 
                mobile,
                data_type,
                additional_data,
                scraped_at
            FROM drivers_data 
            ORDER BY id 
            LIMIT 10
        """)
        
        registros = cursor.fetchall()
        
        print(f"\n📋 PRIMEIROS 10 REGISTROS:")
        print("-" * 80)
        
        for i, (id, driver_id, name, mobile, data_type, additional_data, scraped_at) in enumerate(registros, 1):
            print(f"\n{i}. ID: {id}")
            print(f"   Driver ID: {driver_id}")
            print(f"   Nome: {name}")
            print(f"   Mobile: {mobile}")
            print(f"   Data Type: {data_type}")
            print(f"   Scraped At: {scraped_at}")
            
            # Verificar estrutura do additional_data
            if additional_data:
                try:
                    if isinstance(additional_data, str):
                        data = json.loads(additional_data)
                    else:
                        data = additional_data
                    
                    print(f"   Additional Data Keys: {list(data.keys())}")
                    
                    # Se tem raw_row, mostrar primeiros campos
                    if 'raw_row' in data and isinstance(data['raw_row'], list):
                        print(f"   Raw Row (primeiros 5): {data['raw_row'][:5]}")
                    
                except Exception as e:
                    print(f"   Erro parsing additional_data: {e}")
            else:
                print(f"   Additional Data: None")
        
        # Verificar driver_ids únicos
        cursor.execute("SELECT DISTINCT driver_id FROM drivers_data ORDER BY driver_id")
        driver_ids = cursor.fetchall()
        
        print(f"\n🆔 DRIVER IDS ÚNICOS ({len(driver_ids)}):")
        print("-" * 40)
        for driver_id, in driver_ids[:20]:  # Mostrar apenas os primeiros 20
            print(f"   • {driver_id}")
        
        if len(driver_ids) > 20:
            print(f"   ... e mais {len(driver_ids) - 20} driver_ids")
        
        # Verificar data_types
        cursor.execute("SELECT data_type, COUNT(*) FROM drivers_data GROUP BY data_type ORDER BY COUNT(*) DESC")
        data_types = cursor.fetchall()
        
        print(f"\n📊 DISTRIBUIÇÃO POR DATA_TYPE:")
        print("-" * 30)
        for data_type, count in data_types:
            print(f"   {data_type}: {count} registros")
        
        # Verificar campos de nome vs driver_id
        cursor.execute("""
            SELECT 
                driver_id,
                name,
                mobile
            FROM drivers_data 
            WHERE name IS NOT NULL AND name != 'None'
            LIMIT 5
        """)
        
        nomes_validos = cursor.fetchall()
        
        print(f"\n✅ REGISTROS COM NOMES VÁLIDOS:")
        print("-" * 40)
        for driver_id, name, mobile in nomes_validos:
            print(f"   Driver ID: {driver_id}")
            print(f"   Nome: {name}")
            print(f"   Mobile: {mobile}")
            print()
        
        conn.close()
        
        print("=" * 80)
        print("✅ TESTE CONCLUÍDO!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_tabela_drivers()
