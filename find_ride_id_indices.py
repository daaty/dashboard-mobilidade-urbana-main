#!/usr/bin/env python3
import psycopg2
import json
from datetime import datetime

def find_ride_id_indices():
    """Encontrar o índice do ID de corrida para cada tipo e fonte"""
    
    # Conectar ao banco
    conn = psycopg2.connect(
        host="148.230.73.27",
        port=5432,
        database="n8n_db",
        user="n8n_user",
        password="n8n_pw"
    )
    cur = conn.cursor()
    
    # Buscar dados
    cur.execute("SELECT * FROM rides_data ORDER BY id LIMIT 10")  # Primeiro alguns registros
    rows = cur.fetchall()
    
    print("🔍 ANÁLISE DOS ÍNDICES DE ID DAS CORRIDAS POR FONTE")
    print("=" * 70)
    
    for row in rows:
        table_id, table_name, data_hash, ride_data_str, scraped_at, session_info, source = row
        
        try:
            ride_data = json.loads(ride_data_str)
        except:
            continue
            
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        
        print(f"\n📋 Tabela: {table_name}")
        print(f"   Fonte: {source}")
        print(f"   Total registros: {len(new_records)}")
        
        # Mostrar apenas os primeiros 2 registros para análise
        for i, rec in enumerate(new_records[:2]):
            print(f"\n   📝 Registro {i+1}:")
            print(f"      Tamanho: {len(rec)} campos")
            
            # Mostrar primeiros 10 campos com seus índices
            for idx, field in enumerate(rec[:10]):
                field_str = str(field)[:50] + "..." if len(str(field)) > 50 else str(field)
                print(f"      [{idx:2d}]: {field_str}")
                
                # Detectar possível ID (número grande no início)
                if idx < 3:  # Primeiros 3 campos são mais prováveis de conter ID
                    try:
                        if isinstance(field, int) and field > 1000000:
                            print(f"           *** POSSÍVEL ID DE CORRIDA ***")
                        elif isinstance(field, str) and field.isdigit() and int(field) > 1000000:
                            print(f"           *** POSSÍVEL ID DE CORRIDA (string) ***")
                    except:
                        pass
            
            if i == 0:  # Para o primeiro registro, mostrar mais detalhes
                print(f"\n   🎯 ANÁLISE DETALHADA DO PRIMEIRO REGISTRO:")
                if source == "import_excel":
                    print(f"      Fonte Excel - Estrutura esperada:")
                    if len(rec) > 0:
                        print(f"      [0] ID: {rec[0]} ({type(rec[0])})")
                    if len(rec) > 1:
                        print(f"      [1] Campo1: {rec[1]}")
                    if len(rec) > 2:
                        print(f"      [2] Campo2: {rec[2]}")
                        
                elif source == "monitoring-service-adapted":
                    print(f"      Fonte Monitoring - Estrutura esperada:")
                    if len(rec) > 0:
                        print(f"      [0] ID: {rec[0]} ({type(rec[0])})")
                    if len(rec) > 1:
                        print(f"      [1] Campo1: {rec[1]}")
                    if len(rec) > 2:
                        print(f"      [2] Campo2: {rec[2]}")
        
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    find_ride_id_indices()