#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar estrutura detalhada da tabela rides_data
e descobrir campos de cidade e período
"""

import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente do backend
load_dotenv('backend/.env.production')

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

print(f"🔌 Conectando em: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

def analisar_rides_data():
    """Análise detalhada da tabela rides_data"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    print("\n" + "="*80)
    print("📊 ANÁLISE DETALHADA: rides_data")
    print("="*80 + "\n")
    
    # 1. Todas as colunas
    print("📋 COLUNAS DISPONÍVEIS:")
    cursor.execute("""
        SELECT 
            column_name, 
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_name = 'rides_data'
        ORDER BY ordinal_position;
    """)
    
    colunas = cursor.fetchall()
    for col in colunas:
        print(f"  - {col['column_name']:<30} {col['data_type']:<20} (Nullable: {col['is_nullable']})")
    
    # 2. Amostra de 5 registros COMPLETOS
    print("\n" + "="*80)
    print("📄 AMOSTRA DE 5 REGISTROS (todos os campos):")
    print("="*80 + "\n")
    
    cursor.execute("SELECT * FROM rides_data LIMIT 5;")
    samples = cursor.fetchall()
    
    for i, record in enumerate(samples, 1):
        print(f"\n🔸 Registro {i}:")
        for key, value in dict(record).items():
            # Truncar valores muito longos
            if isinstance(value, str) and len(value) > 200:
                value = value[:200] + "... [truncado]"
            elif isinstance(value, dict):
                value = json.dumps(value, indent=2, ensure_ascii=False)[:500] + "..."
            print(f"    {key}: {value}")
    
    # 3. Descobrir campos de cidade
    print("\n" + "="*80)
    print("🏙️ POSSÍVEIS CAMPOS DE CIDADE:")
    print("="*80 + "\n")
    
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'rides_data'
        AND (
            column_name ILIKE '%city%' OR
            column_name ILIKE '%cidade%' OR
            column_name ILIKE '%location%' OR
            column_name ILIKE '%local%'
        );
    """)
    
    city_columns = cursor.fetchall()
    if city_columns:
        for col in city_columns:
            print(f"  ✓ {col['column_name']}")
            
            # Valores únicos neste campo
            try:
                cursor.execute(f"""
                    SELECT DISTINCT {col['column_name']}, COUNT(*) as total
                    FROM rides_data
                    WHERE {col['column_name']} IS NOT NULL
                    GROUP BY {col['column_name']}
                    ORDER BY total DESC
                    LIMIT 10;
                """)
                valores = cursor.fetchall()
                if valores:
                    print(f"    Valores distintos:")
                    for val in valores:
                        print(f"      - {val[0]}: {val['total']} registros")
            except Exception as e:
                print(f"    ⚠️ Erro ao consultar valores: {e}")
    else:
        print("  ⚠️ Nenhum campo explícito de cidade encontrado")
        print("  💡 A cidade pode estar dentro de um campo JSON (additional_data)")
    
    # 4. Verificar se cidade está em additional_data
    print("\n" + "="*80)
    print("🔍 VERIFICANDO additional_data:")
    print("="*80 + "\n")
    
    cursor.execute("""
        SELECT additional_data
        FROM rides_data
        WHERE additional_data IS NOT NULL
        LIMIT 3;
    """)
    
    samples_json = cursor.fetchall()
    if samples_json:
        for i, rec in enumerate(samples_json, 1):
            print(f"\nAmostra {i}:")
            try:
                data = rec['additional_data']
                # Procurar chaves relacionadas a cidade
                if isinstance(data, dict):
                    city_keys = [k for k in data.keys() if 'city' in k.lower() or 'cidade' in k.lower()]
                    if city_keys:
                        print(f"  🎯 Chaves de cidade encontradas: {city_keys}")
                        for key in city_keys:
                            print(f"    - {key}: {data[key]}")
                    else:
                        print(f"  📦 Chaves disponíveis: {list(data.keys())[:10]}")
                        # Mostrar algumas chaves que podem conter informação de localização
                        location_keys = [k for k in data.keys() if any(x in k.lower() for x in ['location', 'local', 'address', 'endereco', 'pickup', 'drop'])]
                        if location_keys:
                            print(f"  🗺️ Chaves de localização: {location_keys}")
                            for key in location_keys[:5]:
                                print(f"    - {key}: {data[key]}")
            except Exception as e:
                print(f"  ⚠️ Erro ao processar JSON: {e}")
    
    # 5. Campos de data/período
    print("\n" + "="*80)
    print("📅 CAMPOS DE DATA/PERÍODO:")
    print("="*80 + "\n")
    
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'rides_data'
        AND (
            data_type ILIKE '%time%' OR
            data_type ILIKE '%date%' OR
            column_name ILIKE '%date%' OR
            column_name ILIKE '%time%' OR
            column_name ILIKE '%periodo%' OR
            column_name ILIKE '%created%' OR
            column_name ILIKE '%updated%'
        )
        ORDER BY column_name;
    """)
    
    date_columns = cursor.fetchall()
    for col in date_columns:
        print(f"  - {col['column_name']:<30} ({col['data_type']})")
        
        # Range de datas
        try:
            cursor.execute(f"""
                SELECT 
                    MIN({col['column_name']})::text as min_date,
                    MAX({col['column_name']})::text as max_date,
                    COUNT(DISTINCT {col['column_name']}) as distinct_dates
                FROM rides_data
                WHERE {col['column_name']} IS NOT NULL;
            """)
            range_data = cursor.fetchone()
            if range_data and range_data['min_date']:
                print(f"    Range: {range_data['min_date']} até {range_data['max_date']}")
                print(f"    Datas distintas: {range_data['distinct_dates']}")
        except Exception as e:
            print(f"    ⚠️ Erro ao consultar range: {e}")
    
    # 6. Estatísticas gerais
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS GERAIS:")
    print("="*80 + "\n")
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_registros,
            COUNT(DISTINCT driver_id) as motoristas_unicos,
            COUNT(DISTINCT passenger_id) as passageiros_unicos
        FROM rides_data;
    """)
    
    stats = cursor.fetchone()
    print(f"  Total de registros: {stats['total_registros']:,}")
    print(f"  Motoristas únicos: {stats['motoristas_unicos']:,}")
    print(f"  Passageiros únicos: {stats['passageiros_unicos']:,}")
    
    conn.close()

if __name__ == "__main__":
    try:
        analisar_rides_data()
        print("\n✅ Análise concluída com sucesso!")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
