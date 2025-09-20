"""
SCRIPT DE DEBUG PARA ENCONTRAR O PROBLEMA REAL DOS DADOS DUPLICADOS
Este script vai analisar EXATAMENTE o que está no banco e mostrar onde está o problema
"""
import asyncio
import asyncpg
import json
from datetime import datetime
from collections import defaultdict

async def debug_real_problem():
    """Encontrar o verdadeiro problema dos dados duplicados"""
    
    try:
        conn = await asyncpg.connect(
            host="148.230.73.27",
            port=5432,
            user="n8n_user",
            password="n8n_pw",
            database="n8n_db"
        )
        
        print("ANALISANDO PROBLEMA REAL DOS DADOS DUPLICADOS")
        print("=" * 60)
        
        # Buscar todos os registros
        query = "SELECT id, source, scraped_at, ride_data FROM rides_data ORDER BY scraped_at"
        rows = await conn.fetch(query)
        
        print(f"TOTAL REGISTROS NO BANCO: {len(rows)}")
        
        # Contar corridas por dia de setembro EXATAMENTE como o endpoint faz
        setembro_corridas = defaultdict(lambda: {"concluidas": 0, "canceladas": 0, "perdidas": 0})
        
        # Processar cada registro EXATAMENTE como o endpoint
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
            scraped_at = row['scraped_at']
            
            print(f"\nREGISTRO ID {record_id} ({source}):")
            print(f"  Scraped em: {scraped_at}")
            print(f"  Tabela: {table_name}")
            print(f"  Total records: {len(new_records)}")
            
            # PROCESSAR CONCLUÍDAS
            if table_name in ["Completed Rides", "corridas_concluidas", "rides_data"]:
                setembro_count = 0
                for rec in new_records:
                    if source == "import_excel":
                        hora = rec[6] if len(rec) > 6 else None
                        status = rec[9] if len(rec) > 9 else None
                    else:
                        hora = rec[7] if len(rec) > 7 else None
                        status = rec[10] if len(rec) > 10 else None
                    
                    # Verificar status
                    if status and "Concluído" not in str(status) and "Completed" not in str(status):
                        continue
                    
                    # Extrair data
                    if hora and "2025-09" in str(hora):
                        try:
                            # Simular extract_datetime_from_record
                            hora_str = str(hora).replace('T', ' ').split('.')[0]
                            if len(hora_str) == 19:  # YYYY-MM-DD HH:MM:SS
                                dt_corrida = datetime.strptime(hora_str, "%Y-%m-%d %H:%M:%S")
                                dia = dt_corrida.day
                                setembro_corridas[dia]["concluidas"] += 1
                                setembro_count += 1
                        except:
                            continue
                
                if setembro_count > 0:
                    print(f"    → {setembro_count} corridas CONCLUÍDAS de setembro")
            
            # PROCESSAR CANCELADAS
            elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                setembro_count = 0
                for rec in new_records:
                    if source == "import_excel":
                        hora = rec[11] if len(rec) > 11 else None
                        status = rec[13] if len(rec) > 13 else None
                    else:
                        hora = rec[12] if len(rec) > 12 else None
                        status = rec[14] if len(rec) > 14 else None
                    
                    # Verificar status
                    if status and "Cancel" not in str(status) and "cancel" not in str(status):
                        continue
                    
                    # Extrair data
                    if hora and "2025-09" in str(hora):
                        try:
                            hora_str = str(hora).replace('T', ' ').split('.')[0]
                            if len(hora_str) == 19:
                                dt_corrida = datetime.strptime(hora_str, "%Y-%m-%d %H:%M:%S")
                                dia = dt_corrida.day
                                setembro_corridas[dia]["canceladas"] += 1
                                setembro_count += 1
                        except:
                            continue
                
                if setembro_count > 0:
                    print(f"    → {setembro_count} corridas CANCELADAS de setembro")
            
            # PROCESSAR PERDIDAS
            elif table_name in ["Missed Rides", "corridas_perdidas", "Scheduled Rides", "corridas_agendadas"]:
                setembro_count = 0
                for rec in new_records:
                    if source == "import_excel":
                        hora = rec[6] if len(rec) > 6 else None
                        status = rec[5] if len(rec) > 5 else None
                    else:
                        if table_name in ["Scheduled Rides", "corridas_agendadas"]:
                            hora = rec[10] if len(rec) > 10 else None
                            status = rec[14] if len(rec) > 14 else None
                        else:
                            hora = rec[6] if len(rec) > 6 else None
                            status = rec[5] if len(rec) > 5 else None
                    
                    # Verificar status
                    if status and not any(word in str(status) for word in ["Timeout", "Missed", "Process", "perdida"]):
                        continue
                    
                    # Extrair data
                    if hora and "2025-09" in str(hora):
                        try:
                            hora_str = str(hora).replace('T', ' ').split('.')[0]
                            if len(hora_str) == 19:
                                dt_corrida = datetime.strptime(hora_str, "%Y-%m-%d %H:%M:%S")
                                dia = dt_corrida.day
                                setembro_corridas[dia]["perdidas"] += 1
                                setembro_count += 1
                        except:
                            continue
                
                if setembro_count > 0:
                    print(f"    → {setembro_count} corridas PERDIDAS de setembro")
        
        print("\n" + "=" * 60)
        print("RESULTADO FINAL - SETEMBRO DIA POR DIA:")
        print("=" * 60)
        
        total_concluidas = total_canceladas = total_perdidas = 0
        
        for dia in sorted(setembro_corridas.keys()):
            concl = setembro_corridas[dia]["concluidas"]
            cancel = setembro_corridas[dia]["canceladas"]
            perd = setembro_corridas[dia]["perdidas"]
            total = concl + cancel + perd
            
            total_concluidas += concl
            total_canceladas += cancel
            total_perdidas += perd
            
            if total > 0:
                print(f"Dia {dia:2d}: {total:3d} total ({concl} concl + {cancel} cancel + {perd} perdidas)")
                
                if total > 30:
                    print(f"       ⚠️ MUITO ALTO! Investigar este dia específico")
        
        total_geral = total_concluidas + total_canceladas + total_perdidas
        print(f"\nTOTAL SETEMBRO:")
        print(f"  Concluídas: {total_concluidas}")
        print(f"  Canceladas: {total_canceladas}")
        print(f"  Perdidas: {total_perdidas}")
        print(f"  TOTAL GERAL: {total_geral}")
        
        dias_com_dados = len([d for d in setembro_corridas.keys() if (setembro_corridas[d]["concluidas"] + setembro_corridas[d]["canceladas"] + setembro_corridas[d]["perdidas"]) > 0])
        if dias_com_dados > 0:
            media = total_geral / dias_com_dados
            print(f"  Média por dia: {media:.1f}")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")

# Executar análise
asyncio.run(debug_real_problem())