"""
DEBUG PARA VER OS VALORES REAIS DE STATUS
"""
import asyncio
import asyncpg
import json
from collections import defaultdict

async def debug_status_values():
    """Ver quais valores de status estão realmente no banco"""
    
    try:
        conn = await asyncpg.connect(
            host="148.230.73.27",
            port=5432,
            user="n8n_user",
            password="n8n_pw",
            database="n8n_db"
        )
        
        print("ANALISANDO VALORES DE STATUS REAIS")
        print("=" * 60)
        
        # Buscar todos os registros de setembro
        query = "SELECT id, source, ride_data FROM rides_data"
        rows = await conn.fetch(query)
        
        status_counts = defaultdict(int)
        setembro_status = defaultdict(lambda: defaultdict(int))
        
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
            
            # Analisar corridas concluídas
            if table_name in ["Completed Rides", "corridas_concluidas", "rides_data"]:
                for rec in new_records:
                    if source == "import_excel":
                        hora = rec[6] if len(rec) > 6 else None
                        status = rec[9] if len(rec) > 9 else None
                    else:
                        hora = rec[7] if len(rec) > 7 else None
                        status = rec[10] if len(rec) > 10 else None
                    
                    if status:
                        status_str = str(status)
                        status_counts[status_str] += 1
                        
                        # Se é de setembro
                        if hora and "2025-09" in str(hora):
                            setembro_status["completed"][status_str] += 1
            
            # Analisar corridas canceladas  
            elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                for rec in new_records:
                    if source == "import_excel":
                        status = rec[13] if len(rec) > 13 else None
                    else:
                        status = rec[14] if len(rec) > 14 else None
                    
                    if status:
                        status_str = str(status)
                        status_counts[status_str] += 1
            
            # Analisar corridas perdidas
            elif table_name in ["Missed Rides", "corridas_perdidas", "Scheduled Rides", "corridas_agendadas"]:
                for rec in new_records:
                    if source == "import_excel":
                        status = rec[5] if len(rec) > 5 else None
                    else:
                        if table_name in ["Scheduled Rides", "corridas_agendadas"]:
                            status = rec[14] if len(rec) > 14 else None
                        else:
                            status = rec[5] if len(rec) > 5 else None
                    
                    if status:
                        status_str = str(status)
                        status_counts[status_str] += 1
        
        print("VALORES DE STATUS ENCONTRADOS:")
        print("-" * 40)
        for status, count in sorted(status_counts.items()):
            print(f"'{status}': {count} vezes")
        
        print(f"\nSTATUS DE CORRIDAS CONCLUÍDAS EM SETEMBRO:")
        print("-" * 40)
        if setembro_status["completed"]:
            for status, count in setembro_status["completed"].items():
                print(f"'{status}': {count} vezes")
        else:
            print("NENHUM STATUS DE CORRIDA CONCLUÍDA EM SETEMBRO!")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")

# Executar análise
asyncio.run(debug_status_values())