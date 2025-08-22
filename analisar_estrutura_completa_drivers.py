#!/usr/bin/env python3

import psycopg2
import json
from datetime import datetime

def analisar_estrutura_completa():
    """Análise completa da estrutura da tabela drivers_data"""
    
    try:
        # Conectar ao PostgreSQL
        DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔍 ANÁLISE COMPLETA DA ESTRUTURA DE DRIVERS_DATA")
        print("=" * 60)
        
        # Buscar alguns registros para análise detalhada
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
            WHERE data_type = 'active'
            ORDER BY id ASC
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        
        for i, row in enumerate(rows, 1):
            id_rec, driver_id, name, mobile, data_type, additional_data, scraped_at = row
            
            print(f"\n📋 REGISTRO {i} (ID: {id_rec}):")
            print(f"   driver_id: {driver_id}")
            print(f"   name: {name}")
            print(f"   mobile: {mobile}")
            print(f"   data_type: {data_type}")
            print(f"   scraped_at: {scraped_at}")
            
            # Parse do additional_data para encontrar o nome real
            if isinstance(additional_data, str):
                data = json.loads(additional_data)
            elif isinstance(additional_data, dict):
                data = additional_data
            else:
                data = {}
            
            print(f"   📊 ESTRUTURA additional_data:")
            
            # Verificar se tem headers e raw_row
            if 'headers' in data and 'raw_row' in data:
                headers = data['headers']
                raw_row = data['raw_row']
                
                print(f"      Headers: {len(headers)} campos")
                print(f"      Raw Row: {len(raw_row)} valores")
                
                # Mapear headers -> valores
                if len(headers) == len(raw_row):
                    print(f"      🔍 MAPEAMENTO COMPLETO:")
                    for j, (header, value) in enumerate(zip(headers, raw_row)):
                        if 'name' in header.lower() or 'otp' in header.lower() or header == 'OTP':
                            print(f"         [{j}] {header}: '{value}' ⭐ (POSSÍVEL NOME)")
                        else:
                            print(f"         [{j}] {header}: '{value}'")
                else:
                    print(f"      ⚠️ INCONSISTÊNCIA: {len(headers)} headers ≠ {len(raw_row)} valores")
            
            # Verificar outros campos que podem ter o nome
            campos_suspeitos = ['otp', 'driver_name', 'franchise_name']
            for campo in campos_suspeitos:
                if campo in data:
                    print(f"      {campo}: '{data[campo]}' ⭐")
            
            print("-" * 50)
        
        # Estatísticas gerais
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        
        cursor.execute("SELECT COUNT(*) FROM drivers_data WHERE data_type = 'active'")
        total_active = cursor.fetchone()[0]
        print(f"   Total registros 'active': {total_active}")
        
        cursor.execute("SELECT COUNT(DISTINCT driver_id) FROM drivers_data WHERE data_type = 'active'")
        unique_driver_ids = cursor.fetchone()[0]
        print(f"   Driver IDs únicos: {unique_driver_ids}")
        
        cursor.execute("SELECT COUNT(DISTINCT name) FROM drivers_data WHERE data_type = 'active'")
        unique_names = cursor.fetchone()[0]
        print(f"   Names únicos: {unique_names}")
        
        # Verificar padrões nos nomes
        cursor.execute("""
            SELECT name, COUNT(*) as count 
            FROM drivers_data 
            WHERE data_type = 'active' 
            GROUP BY name 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        print(f"\n📋 TOP 10 NOMES MAIS FREQUENTES:")
        name_counts = cursor.fetchall()
        for name, count in name_counts:
            tipo = "ID NUMÉRICO" if name.isdigit() else "NOME/TEXTO"
            print(f"   '{name}' ({count}x) - {tipo}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    analisar_estrutura_completa()
