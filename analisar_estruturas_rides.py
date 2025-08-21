#!/usr/bin/env python3

import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta

# Configuração do banco de dados
VPS_CONFIG = {
    'host': '148.230.73.27',
    'port': '5432',
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def analisar_estruturas_rides():
    """Analisar diferentes estruturas de dados na tabela rides_data"""
    try:
        conn = psycopg2.connect(**VPS_CONFIG)
        cursor = conn.cursor()
        
        # Buscar uma amostra representativa de dados
        cursor.execute("""
            SELECT id, ride_data, 
                   CASE 
                       WHEN ride_data::text LIKE '%tableName%' THEN 'scraper'
                       WHEN ride_data::text LIKE '%Corridas%' THEN 'frontend'
                       ELSE 'outro'
                   END as tipo_origem
            FROM rides_data 
            ORDER BY id DESC 
            LIMIT 50
        """)
        
        rides = cursor.fetchall()
        
        print(f"🔍 ANÁLISE DE ESTRUTURAS DOS DADOS DE CORRIDAS")
        print(f"📊 Total de registros analisados: {len(rides)}")
        print("=" * 60)
        
        tipos_encontrados = {}
        estruturas_por_tipo = {}
        
        for ride_id, ride_data, tipo_origem in rides:
            
            if tipo_origem not in tipos_encontrados:
                tipos_encontrados[tipo_origem] = 0
                estruturas_por_tipo[tipo_origem] = []
                
            tipos_encontrados[tipo_origem] += 1
            
            try:
                if isinstance(ride_data, str):
                    data = json.loads(ride_data)
                else:
                    data = ride_data
                    
                # Analisar estrutura
                estrutura = {
                    'id': ride_id,
                    'chaves_principais': list(data.keys()) if isinstance(data, dict) else ['não é dict'],
                    'exemplo_data': data
                }
                
                # Adicionar apenas alguns exemplos por tipo
                if len(estruturas_por_tipo[tipo_origem]) < 3:
                    estruturas_por_tipo[tipo_origem].append(estrutura)
                    
            except Exception as e:
                print(f"❌ Erro ao processar registro {ride_id}: {e}")
        
        # Relatório por tipo
        for tipo, count in tipos_encontrados.items():
            print(f"\n🔸 TIPO: {tipo.upper()}")
            print(f"   Quantidade: {count} registros")
            
            if tipo in estruturas_por_tipo:
                for i, exemplo in enumerate(estruturas_por_tipo[tipo]):
                    print(f"\n   📋 Exemplo {i+1} (ID: {exemplo['id']}):")
                    print(f"      Chaves: {exemplo['chaves_principais']}")
                    
                    # Mostrar estrutura mais detalhada
                    if isinstance(exemplo['exemplo_data'], dict):
                        if 'tableName' in exemplo['exemplo_data']:
                            print(f"      TableName: {exemplo['exemplo_data'].get('tableName')}")
                            if 'records' in exemplo['exemplo_data']:
                                records = exemplo['exemplo_data']['records']
                                if records and len(records) > 0:
                                    print(f"      Primeiro record: {records[0][:5] if isinstance(records[0], list) else records[0]}")
                        
                        # Para dados do frontend
                        if any(key.startswith('Corridas') for key in exemplo['exemplo_data'].keys()):
                            print(f"      Planilhas encontradas: {[k for k in exemplo['exemplo_data'].keys() if 'Corridas' in k]}")
                            
        print("\n" + "=" * 60)
        
        # Buscar especificamente corridas concluídas de diferentes fontes
        print(f"\n🎯 ANÁLISE ESPECÍFICA DE CORRIDAS CONCLUÍDAS")
        
        # Corridas do scraper
        cursor.execute("""
            SELECT COUNT(*) 
            FROM rides_data 
            WHERE ride_data::text LIKE '%"tableName":"Completed Rides"%'
        """)
        scraper_concluidas = cursor.fetchone()[0]
        
        # Corridas do frontend (XLS)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM rides_data 
            WHERE ride_data::text LIKE '%CorridasConcluidas%'
        """)
        frontend_concluidas = cursor.fetchone()[0]
        
        print(f"📈 Corridas do Scraper (Completed Rides): {scraper_concluidas}")
        print(f"📊 Corridas do Frontend (CorridasConcluidas): {frontend_concluidas}")
        
        # Verificar corridas do dia 20
        cursor.execute("""
            SELECT ride_data::text
            FROM rides_data 
            WHERE ride_data::text LIKE '%2025-08-20%'
            LIMIT 5
        """)
        
        corridas_dia_20 = cursor.fetchall()
        print(f"\n📅 Corridas do dia 20/08: {len(corridas_dia_20)} registros encontrados")
        
        if corridas_dia_20:
            for i, (data_text,) in enumerate(corridas_dia_20[:2]):
                print(f"\n   Exemplo {i+1}:")
                try:
                    data = json.loads(data_text)
                    if 'tableName' in data:
                        print(f"      Tipo: Scraper - {data['tableName']}")
                    else:
                        print(f"      Tipo: Frontend - Chaves: {list(data.keys())[:5]}")
                except:
                    print(f"      Tipo: Texto bruto")
        
        cursor.close()
        conn.close()
        
        return tipos_encontrados, estruturas_por_tipo
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None, None

if __name__ == "__main__":
    analisar_estruturas_rides()
