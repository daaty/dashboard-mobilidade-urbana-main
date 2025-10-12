#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair e analisar estrutura JSON dentro de rides_data
"""

import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import json
from collections import Counter

# Carregar variáveis de ambiente
load_dotenv('backend/.env.production')

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def analisar_json_rides():
    """Análise do JSON dentro de ride_data"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    print("\n" + "="*80)
    print("📊 ESTRUTURA JSON DE rides_data")
    print("="*80 + "\n")
    
    # Buscar amostras de cada tipo de tabela
    cursor.execute("""
        SELECT DISTINCT table_name
        FROM rides_data
        WHERE table_name IS NOT NULL;
    """)
    
    table_types = cursor.fetchall()
    print(f"📋 Tipos de tabela encontrados: {len(table_types)}")
    for t in table_types:
        print(f"  - {t['table_name']}")
    
    print("\n" + "="*80)
    
    # Análise detalhada para cada tipo
    for table_type in table_types:
        table_name = table_type['table_name']
        print(f"\n🔍 ANALISANDO: {table_name}")
        print("-" * 80)
        
        cursor.execute("""
            SELECT ride_data, scraped_at, source
            FROM rides_data
            WHERE table_name = %s
            LIMIT 2;
        """, (table_name,))
        
        samples = cursor.fetchall()
        
        for i, sample in enumerate(samples, 1):
            print(f"\n  Amostra {i}:")
            print(f"    Fonte: {sample['source']}")
            print(f"    Data: {sample['scraped_at']}")
            
            try:
                data = json.loads(sample['ride_data'])
                print(f"    Estrutura JSON:")
                print(f"      - Chaves principais: {list(data.keys())}")
                
                if 'newRecords' in data and len(data['newRecords']) > 0:
                    first_record = data['newRecords'][0]
                    print(f"      - Primeiro registro (total de campos: {len(first_record)}):")
                    
                    # Mostrar primeiros campos
                    for idx, field in enumerate(first_record[:15]):  # Primeiros 15 campos
                        if isinstance(field, str) and len(field) > 100:
                            field = field[:100] + "..."
                        print(f"          [{idx}]: {field}")
                    
                    if len(first_record) > 15:
                        print(f"          ... e mais {len(first_record) - 15} campos")
                    
                    # Total de registros
                    print(f"      - Total de registros no JSON: {len(data['newRecords'])}")
                    
                    # Tentar identificar campo de cidade
                    print(f"\n      🏙️ Identificando cidade:")
                    for idx, field in enumerate(first_record):
                        if isinstance(field, str):
                            # Procurar por nomes de cidades conhecidas
                            cidades_conhecidas = ['Matupá', 'MATUPA', 'Peixoto', 'PEIXOTO', 'Guarantã', 'GUARANTA', 
                                                  'Nova Monte Verde', 'NOVA MONTE VERDE', 'Nova Bandeirantes']
                            if any(cidade.lower() in str(field).lower() for cidade in cidades_conhecidas):
                                print(f"          Possível cidade no índice [{idx}]: {field}")
                
            except json.JSONDecodeError as e:
                print(f"    ⚠️ Erro ao decodificar JSON: {e}")
            except Exception as e:
                print(f"    ⚠️ Erro: {e}")
    
    # Contar registros por tipo de tabela
    print("\n" + "="*80)
    print("📊 CONTAGEM POR TIPO DE TABELA:")
    print("="*80 + "\n")
    
    cursor.execute("""
        SELECT 
            table_name,
            COUNT(*) as total_records,
            MIN(scraped_at) as first_scrape,
            MAX(scraped_at) as last_scrape
        FROM rides_data
        WHERE table_name IS NOT NULL
        GROUP BY table_name
        ORDER BY total_records DESC;
    """)
    
    counts = cursor.fetchall()
    for row in counts:
        print(f"  {row['table_name']}:")
        print(f"    Registros: {row['total_records']}")
        print(f"    Período: {row['first_scrape']} até {row['last_scrape']}\n")
    
    # Analisar um JSON completo de "Completed Rides" para mapear campos
    print("="*80)
    print("🎯 MAPEAMENTO DETALHADO: Completed Rides")
    print("="*80 + "\n")
    
    cursor.execute("""
        SELECT ride_data
        FROM rides_data
        WHERE table_name = 'Completed Rides'
        LIMIT 1;
    """)
    
    completed_sample = cursor.fetchone()
    if completed_sample:
        try:
            data = json.loads(completed_sample['ride_data'])
            if 'newRecords' in data and len(data['newRecords']) > 0:
                record = data['newRecords'][0]
                print(f"Total de campos por registro: {len(record)}\n")
                print("Campos identificados:")
                
                # Baseado na estrutura que vimos nos exemplos anteriores
                # [[engagement_id, driver_id, driver_name, user_id, user_mobile, user_name, vehicle_type, pickup_location, ...]]
                field_map = [
                    "engagement_id",
                    "driver_id", 
                    "driver_name",
                    "user_id",
                    "user_mobile",
                    "user_name",
                    "vehicle_type",
                    "pickup_location",
                    "drop_location",
                    "ride_start_time",
                    "ride_end_time",
                    "ride_fare",
                    "ride_distance",
                    # ... outros campos
                ]
                
                for idx, (field_name, value) in enumerate(zip(field_map, record)):
                    if isinstance(value, str) and len(value) > 150:
                        value = value[:150] + "..."
                    print(f"  [{idx:2d}] {field_name:20s} = {value}")
                
                if len(record) > len(field_map):
                    print(f"\n  ... e mais {len(record) - len(field_map)} campos não mapeados")
                    print("\n  Valores restantes:")
                    for idx in range(len(field_map), min(len(record), len(field_map) + 5)):
                        value = record[idx]
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"  [{idx:2d}] {value}")
                        
        except Exception as e:
            print(f"⚠️ Erro: {e}")
    
    conn.close()

if __name__ == "__main__":
    try:
        analisar_json_rides()
        print("\n✅ Análise concluída!")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
