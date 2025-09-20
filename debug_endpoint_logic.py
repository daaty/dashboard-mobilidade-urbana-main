"""
DEBUG CORRETO - USANDO A MESMA LÓGICA DO ENDPOINT
"""
import asyncio
import asyncpg
import json
from datetime import datetime
from collections import defaultdict
import re

def extract_datetime_from_record(rec, index):
    """Extrai data/hora de um registro - MESMA FUNÇÃO DO ENDPOINT"""
    if index >= len(rec):
        return None
    
    value = str(rec[index]).strip()
    
    # Formato do scraper: "202508202025-08-20 16:59:50"
    scraper_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", value)
    if scraper_match:
        return scraper_match.group(1)
    
    # Formato do frontend: "2025-08-20 16:59:50" (sem prefixo)
    frontend_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", value)
    if frontend_match:
        return frontend_match.group(1)
    
    return None

async def debug_with_endpoint_logic():
    """Debug usando EXATAMENTE a mesma lógica do endpoint"""
    
    try:
        conn = await asyncpg.connect(
            host="148.230.73.27",
            port=5432,
            user="n8n_user",
            password="n8n_pw",
            database="n8n_db"
        )
        
        print("DEBUG COM LOGICA EXATA DO ENDPOINT")
        print("=" * 60)
        
        query = "SELECT id, source, ride_data FROM rides_data"
        rows = await conn.fetch(query)
        
        setembro_corridas = defaultdict(lambda: {"concluidas": 0, "canceladas": 0, "perdidas": 0})
        debug_info = []
        
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
            
            # PROCESSAR CONCLUÍDAS - EXATAMENTE COMO NO ENDPOINT
            if table_name in ["Completed Rides", "corridas_concluidas", "rides_data"]:
                for rec in new_records:
                    # Extrair data e validar status
                    if source == "import_excel":
                        hora = rec[6] if len(rec) > 6 else None
                        status = rec[9] if len(rec) > 9 else None
                    else:
                        hora = rec[7] if len(rec) > 7 else None
                        status = rec[10] if len(rec) > 10 else None
                    
                    # Debug: Registrar tentativa
                    if hora and "2025-09" in str(hora):
                        debug_info.append({
                            'id': row['id'],
                            'source': source,
                            'table': table_name,
                            'hora_raw': hora,
                            'status_raw': status,
                            'hora_index': 6 if source == "import_excel" else 7,
                            'status_index': 9 if source == "import_excel" else 10
                        })
                    
                    # Verificar se é realmente concluída - MESMA VALIDAÇÃO
                    if status and "Concluído" not in str(status) and "Completed" not in str(status):
                        continue
                    
                    # Extrair e validar data - MESMA FUNÇÃO
                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                mes_corrida = dt_corrida.strftime("%Y-%m")
                                dia_corrida = dt_corrida.day
                                
                                if mes_corrida == "2025-09":
                                    setembro_corridas[dia_corrida]["concluidas"] += 1
                            except:
                                continue
        
        print(f"REGISTROS COM DADOS DE SETEMBRO (RAW):")
        print("-" * 50)
        for info in debug_info[:10]:  # Só 10 primeiros
            print(f"ID {info['id']} ({info['source']}):")
            print(f"  Tabela: {info['table']}")
            print(f"  Hora raw (pos {info['hora_index']}): {info['hora_raw']}")
            print(f"  Status raw (pos {info['status_index']}): {info['status_raw']}")
            
            # Testar extração
            dt_str = extract_datetime_from_record([info['hora_raw']], 0)
            print(f"  Data extraída: {dt_str}")
            
            # Testar validação status
            status_ok = "Completed" in str(info['status_raw']) or "Concluído" in str(info['status_raw'])
            print(f"  Status válido: {status_ok}")
            print()
        
        print("RESULTADO FINAL:")
        print("-" * 30)
        total_concluidas = 0
        for dia in sorted(setembro_corridas.keys()):
            concl = setembro_corridas[dia]["concluidas"]
            if concl > 0:
                print(f"Dia {dia}: {concl} concluídas")
                total_concluidas += concl
        
        print(f"\nTOTAL CONCLUÍDAS SETEMBRO: {total_concluidas}")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")

# Executar análise
asyncio.run(debug_with_endpoint_logic())