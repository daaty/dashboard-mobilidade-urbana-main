#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: analisar valores de fare em Completed Rides de Matupá
"""

import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env.production')

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

print("="*80)
print("🔍 DEBUG: Analisando valores de FARE em Completed Rides de Matupá")
print("="*80 + "\n")

# Buscar Completed Rides com cidade Matupá/MATUPA
cursor.execute("""
    SELECT 
        id,
        table_name,
        ride_data
    FROM rides_data
    WHERE table_name = 'Completed Rides'
    LIMIT 100;
""")

matupa_rides = []
total_rides = 0

for row in cursor.fetchall():
    total_rides += 1
    try:
        ride_json = json.loads(row[2])
        
        # ride_json já É o array newRecords
        if isinstance(ride_json, list):
            records = ride_json
        else:
            records = ride_json.get('newRecords', [])
        
        # Extrair cidade (índice 15 em Completed Rides)
        for record in records:
            if len(record) > 15:
                city = record[15]
                
                if city and ('MATUPA' in str(city).upper() or 'MATUPÁ' in str(city).upper()):
                    fare_value = record[12] if len(record) > 12 else None
                    
                    matupa_rides.append({
                        'id': row[0],
                        'driver': record[1] if len(record) > 1 else None,
                        'passenger': record[2] if len(record) > 2 else None,
                        'city': city,
                        'fare_raw': fare_value,
                        'fare_type': type(fare_value).__name__,
                        'record_length': len(record)
                    })
    except (json.JSONDecodeError, IndexError) as e:
        continue

print(f"Total Completed Rides analisados: {total_rides}")
print(f"Corridas de Matupá encontradas: {len(matupa_rides)}\n")

if matupa_rides:
    print("📊 Primeiras 20 corridas de Matupá:")
    print("-" * 80)
    
    for i, ride in enumerate(matupa_rides[:20], 1):
        print(f"\n{i}. ID: {ride['id']}")
        print(f"   Driver: {ride['driver']}")
        print(f"   Passenger: {ride['passenger']}")
        print(f"   City: {ride['city']}")
        print(f"   Fare (raw): {repr(ride['fare_raw'])}")
        print(f"   Fare Type: {ride['fare_type']}")
        print(f"   Record Length: {ride['record_length']}")
        
        # Tentar converter
        if ride['fare_raw']:
            try:
                fare_str = str(ride['fare_raw']).replace(',', '.').strip()
                if fare_str and fare_str != '-':
                    fare_float = float(fare_str)
                    print(f"   ✅ Fare convertido: R$ {fare_float:.2f}")
                else:
                    print(f"   ⚠️ Fare vazio ou '-'")
            except ValueError as e:
                print(f"   ❌ Erro ao converter: {e}")
        else:
            print(f"   ⚠️ Fare é None/null")
    
    # Estatísticas
    print("\n" + "="*80)
    print("📈 ESTATÍSTICAS DE FARE:")
    print("="*80)
    
    fare_none = sum(1 for r in matupa_rides if r['fare_raw'] is None)
    fare_empty = sum(1 for r in matupa_rides if r['fare_raw'] == '' or r['fare_raw'] == '-')
    
    valid_fares = []
    for ride in matupa_rides:
        if ride['fare_raw']:
            try:
                fare_str = str(ride['fare_raw']).replace(',', '.').strip()
                if fare_str and fare_str != '-':
                    valid_fares.append(float(fare_str))
            except ValueError:
                pass
    
    print(f"  Total corridas Matupá: {len(matupa_rides)}")
    print(f"  Fare = None: {fare_none} ({fare_none/len(matupa_rides)*100:.1f}%)")
    print(f"  Fare vazio/'-': {fare_empty} ({fare_empty/len(matupa_rides)*100:.1f}%)")
    print(f"  Fare válido: {len(valid_fares)} ({len(valid_fares)/len(matupa_rides)*100:.1f}%)")
    
    if valid_fares:
        print(f"\n  Receita total: R$ {sum(valid_fares):.2f}")
        print(f"  Média por corrida: R$ {sum(valid_fares)/len(valid_fares):.2f}")
        print(f"  Menor fare: R$ {min(valid_fares):.2f}")
        print(f"  Maior fare: R$ {max(valid_fares):.2f}")

else:
    print("⚠️ Nenhuma corrida de Matupá encontrada!")

conn.close()
