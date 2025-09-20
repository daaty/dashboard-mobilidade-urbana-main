import asyncio
import asyncpg
import json
from datetime import datetime

async def debug_setembro_data():
    """Analisar dados específicos de setembro para encontrar duplicações"""
    
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="password",
            database="dashboard_db"
        )
        
        # Buscar todos os registros
        query = "SELECT id, source, created_at, ride_data FROM rides_data ORDER BY created_at"
        rows = await conn.fetch(query)
        
        print(f"TOTAL DE REGISTROS NO BANCO: {len(rows)}")
        print("="*60)
        
        setembro_records = []
        
        # Processar cada registro procurando dados de setembro
        for row in rows:
            ride_data = row['ride_data']
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except:
                    continue
            
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            source = row['source']
            record_id = row['id']
            created_at = row['created_at']
            
            # Procurar dados de setembro 2025
            setembro_count = 0
            setembro_samples = []
            
            for rec in new_records:
                # Dependendo do source e table_name, a posição da data é diferente
                data_positions = []
                
                if source == "import_excel":
                    if table_name == "Completed Rides":
                        data_positions = [6]  # Posição da data para concluídas
                    elif table_name == "Cancelled Rides":
                        data_positions = [11]  # Posição da data para canceladas
                else:
                    if table_name in ["Completed Rides", "corridas_concluidas"]:
                        data_positions = [7]
                    elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                        data_positions = [12]
                    elif table_name in ["Missed Rides", "corridas_perdidas"]:
                        data_positions = [6]
                
                # Verificar se tem dados de setembro em qualquer posição
                for pos in data_positions:
                    if len(rec) > pos and rec[pos]:
                        data_str = str(rec[pos])
                        if "2025-09" in data_str:
                            setembro_count += 1
                            if len(setembro_samples) < 5:  # Guardar alguns exemplos
                                setembro_samples.append({
                                    'data': data_str,
                                    'record': rec[:min(5, len(rec))]  # Apenas primeiros 5 campos
                                })
            
            if setembro_count > 0:
                setembro_records.append({
                    'record_id': record_id,
                    'source': source,
                    'table_name': table_name,
                    'created_at': created_at,
                    'setembro_count': setembro_count,
                    'total_records': len(new_records),
                    'samples': setembro_samples
                })
        
        print(f"REGISTROS COM DADOS DE SETEMBRO: {len(setembro_records)}")
        print("-" * 60)
        
        total_setembro_entries = 0
        for record in setembro_records:
            total_setembro_entries += record['setembro_count']
            print(f"ID {record['record_id']} ({record['source']})")
            print(f"  Tabela: {record['table_name']}")
            print(f"  Criado em: {record['created_at']}")
            print(f"  Entradas de setembro: {record['setembro_count']} de {record['total_records']} total")
            
            # Mostrar alguns exemplos
            if record['samples']:
                print(f"  Exemplos:")
                for sample in record['samples'][:2]:
                    print(f"    Data: {sample['data']}")
            print()
        
        print(f"TOTAL DE ENTRADAS DE SETEMBRO: {total_setembro_entries}")
        
        # Verificar se há possível duplicação
        if len(setembro_records) > 1:
            print(f"\n⚠️  POSSÍVEL DUPLICAÇÃO: {len(setembro_records)} registros diferentes contêm dados de setembro")
            print("   Isso pode estar causando contagem dupla!")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")

# Executar análise
asyncio.run(debug_setembro_data())