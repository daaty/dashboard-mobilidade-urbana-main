#!/usr/bin/env python3
"""
Script para testar se a função extract_datetime_from_record está funcionando
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import re
import sys
sys.path.append('/Users/arcti/OneDrive/Área de Trabalho/dashboard-mobilidade-urbana-main/dashboard-mobilidade-urbana-main/backend')

# Tentar importar a função do backend
try:
    from app.api.metrics import extract_datetime_from_record
    print("✅ Função extract_datetime_from_record importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar função: {e}")
    print("🔧 Vou definir função de teste")
    
    def extract_datetime_from_record(record_list, index):
        """Função de teste para extrair datetime"""
        if index >= len(record_list) or not record_list[index]:
            return None
            
        value = str(record_list[index])
        
        # Tentar diferentes formatos
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2})',
            r'2025(\d{4})(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'  # Formato especial que vimos
        ]
        
        for pattern in patterns:
            match = re.search(pattern, value)
            if match:
                if len(match.groups()) == 1:
                    return match.group(1)
                elif len(match.groups()) == 3:  # Formato especial
                    return match.group(3)
        
        return None

load_dotenv()

async def test_datetime_extraction():
    print("🔍 TESTANDO EXTRAÇÃO DE DATETIME DOS DADOS REAIS")
    print("=" * 60)
    
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'mobilidade_urbana'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'admin')
        )
        
        result = await conn.fetch("SELECT * FROM rides_data LIMIT 3")
        
        for i, r in enumerate(result):
            print(f"\n📋 TESTE {i+1}:")
            print(f"ID: {r['id']}, Tabela: {r['table_name']}, Fonte: {r['source']}")
            
            ride_data = r['ride_data']
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except:
                    print("❌ Erro ao fazer parse do JSON")
                    continue
                    
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            source = r['source']
            
            print(f"Tabela JSON: {table_name}, Fonte: {source}")
            print(f"Total de registros: {len(new_records)}")
            
            if new_records:
                # Testar primeiro registro
                rec = new_records[0]
                print(f"Primeiro registro tem {len(rec)} campos")
                
                # Testar índices corretos baseado na fonte e tabela
                test_indices = []
                
                if source == "import_excel":
                    if table_name in ["Completed Rides", "rides_data"]:
                        test_indices = [6]  # Data no índice 6
                    elif table_name == "Cancelled Rides":
                        test_indices = [11]  # Data no índice 11
                    elif table_name == "Missed Rides":
                        test_indices = [6]  # Data no índice 6
                else:  # monitoring-service-adapted
                    if table_name == "Completed Rides":
                        test_indices = [7]  # Data no índice 7
                    elif table_name == "Cancelled Rides":
                        test_indices = [12]  # Data no índice 12
                    elif table_name == "Missed Rides":
                        test_indices = [6]  # Data no índice 6
                    elif table_name == "Scheduled Rides":
                        test_indices = [10]  # Data no índice 10
                
                print(f"🔍 Testando índices: {test_indices}")
                
                for idx in test_indices:
                    if idx < len(rec):
                        raw_value = rec[idx]
                        print(f"  Índice {idx}: '{raw_value}' ({type(raw_value).__name__})")
                        
                        # Testar extração
                        extracted = extract_datetime_from_record([raw_value], 0)
                        print(f"    Extraído: '{extracted}'")
                        
                        if extracted:
                            try:
                                dt = datetime.strptime(extracted, "%Y-%m-%d %H:%M:%S")
                                print(f"    ✅ Parsed como datetime: {dt}")
                                
                                # Verificar se está no range de 6 meses
                                now = datetime.now()
                                six_months_ago = now - timedelta(days=180)
                                in_range = six_months_ago <= dt <= now
                                print(f"    📅 No range 6m? {in_range} ({six_months_ago.date()} <= {dt.date()} <= {now.date()})")
                                
                            except Exception as e:
                                print(f"    ❌ Erro ao fazer parse: {e}")
                        else:
                            print(f"    ❌ Nada extraído")
                    else:
                        print(f"  Índice {idx}: FORA DO RANGE (registro tem {len(rec)} campos)")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_datetime_extraction())