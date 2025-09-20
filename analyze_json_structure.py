#!/usr/bin/env python3
"""
Script para analisar a estrutura dos dados JSON na tabela rides_data
e identificar os índices corretos para data, hora e status
"""
import asyncio
import asyncpg
from datetime import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def analyze_json_structure():
    print("🔍 ANALISANDO ESTRUTURA JSON DOS DADOS DE CORRIDAS")
    print("=" * 60)
    
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'mobilidade_urbana'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'admin')
        )
        
        # Buscar diferentes tipos de dados na tabela
        print("📋 BUSCANDO DIFERENTES CATEGORIAS DE DADOS:")
        categories = await conn.fetch("""
            SELECT DISTINCT table_name, source, COUNT(*) as count
            FROM rides_data 
            GROUP BY table_name, source
            ORDER BY count DESC
        """)
        
        for cat in categories:
            print(f"  📊 {cat['table_name']} (fonte: {cat['source']}): {cat['count']} registros")
        
        print(f"\n🔍 ANALISANDO ESTRUTURAS DE CADA CATEGORIA:")
        print("-" * 60)
        
        for cat in categories:
            table_name = cat['table_name']
            source = cat['source']
            
            print(f"\n📋 CATEGORIA: {table_name} (fonte: {source})")
            
            # Buscar um exemplo de cada categoria
            sample = await conn.fetchrow("""
                SELECT ride_data FROM rides_data 
                WHERE table_name = $1 AND source = $2 
                LIMIT 1
            """, table_name, source)
            
            if sample and sample['ride_data']:
                try:
                    data = json.loads(sample['ride_data'])
                    
                    print(f"  🗂️ Estrutura JSON:")
                    print(f"     tableName: {data.get('tableName', 'N/A')}")
                    
                    if 'newRecords' in data and data['newRecords']:
                        records = data['newRecords']
                        print(f"     Total de registros: {len(records)}")
                        
                        if records:
                            first_record = records[0]
                            print(f"     Colunas por registro: {len(first_record)}")
                            print(f"     Exemplo do primeiro registro:")
                            
                            # Analisar cada campo do primeiro registro
                            for i, field in enumerate(first_record):
                                field_type = type(field).__name__
                                field_preview = str(field)[:50] if field is not None else "NULL"
                                print(f"       [{i:2}] {field_type:10} {field_preview}")
                            
                            # Tentar identificar campos de data/hora
                            print(f"\n  🗓️ IDENTIFICANDO CAMPOS DE DATA/HORA:")
                            date_indices = []
                            status_indices = []
                            
                            for i, field in enumerate(first_record):
                                if field is not None:
                                    field_str = str(field)
                                    
                                    # Verificar se é data (formato 2025-XX-XX)
                                    if "2025-" in field_str and len(field_str) >= 10:
                                        date_indices.append((i, field_str))
                                        print(f"       🗓️ Índice {i}: Possível data = {field_str}")
                                    
                                    # Verificar se é status (palavras relacionadas)
                                    status_words = ['Concluído', 'Cancelado', 'Perdida', 'Timeout', 'Missed']
                                    if any(word in field_str for word in status_words):
                                        status_indices.append((i, field_str))
                                        print(f"       📊 Índice {i}: Possível status = {field_str}")
                            
                            # Analisar alguns registros adicionais para confirmar padrão
                            print(f"\n  🔍 VERIFICANDO PADRÃO EM OUTROS REGISTROS:")
                            for j in range(1, min(4, len(records))):
                                record = records[j]
                                print(f"     Registro {j+1}:")
                                
                                for date_idx, _ in date_indices:
                                    if date_idx < len(record):
                                        print(f"       Data[{date_idx}]: {record[date_idx]}")
                                
                                for status_idx, _ in status_indices:
                                    if status_idx < len(record):
                                        print(f"       Status[{status_idx}]: {record[status_idx]}")
                        
                        print(f"\n  📈 RESUMO PARA {table_name}:")
                        if date_indices:
                            print(f"     Campos de data encontrados: {date_indices}")
                        if status_indices:
                            print(f"     Campos de status encontrados: {status_indices}")
                        
                except Exception as e:
                    print(f"  ❌ Erro ao analisar JSON: {e}")
            
            print("-" * 40)
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "=" * 60)
    print("🔚 ANÁLISE CONCLUÍDA")

if __name__ == "__main__":
    asyncio.run(analyze_json_structure())