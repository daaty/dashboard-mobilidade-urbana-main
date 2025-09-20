#!/usr/bin/env python3
"""
Script para testar passo a passo a lógica do endpoint comparative
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def debug_comparative_logic():
    print("🔍 DEBUG: LÓGICA DO ENDPOINT COMPARATIVE")
    print("=" * 60)
    
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'mobilidade_urbana'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'admin')
        )
        
        # Simular lógica do endpoint para período 6m
        now = datetime.now()
        dt_ini = now - timedelta(days=180)
        dt_fim = now
        
        print(f"📅 PERÍODO: {dt_ini.date()} até {dt_fim.date()}")
        
        # Buscar dados
        result = await conn.fetch("SELECT * FROM rides_data")
        print(f"📊 Total de registros na base: {len(result)}")
        
        # Estrutura de dados para armazenar resultados
        data_structure = {}
        for i in range(6):
            month_date = datetime(now.year, now.month, 1) - timedelta(days=i*30)
            month_key = month_date.strftime("%Y-%m")
            data_structure[month_key] = {
                "concluidas": 0,
                "canceladas": 0,
                "perdidas": 0,
                "total": 0
            }
        
        print(f"🗓️ Meses para análise: {list(data_structure.keys())}")
        
        processed_count = 0
        matched_count = 0
        
        for r in result:
            ride_data = r['ride_data']
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            source = r['source']
            
            if not new_records:
                continue
                
            print(f"\n📋 Processando: {table_name} (fonte: {source}) - {len(new_records)} registros")
            processed_count += 1
            
            # Testar se entra na condição de Completed Rides
            if table_name in ["Completed Rides", "corridas_concluidas", "rides_data"]:
                print(f"  ✅ MATCH: Corridas concluídas")
                
                for i, rec in enumerate(new_records[:3]):  # Apenas primeiros 3 para debug
                    # Determinar índices corretos
                    if source == "import_excel":
                        hora_idx = 6
                        status_idx = 9
                    else:
                        hora_idx = 7
                        status_idx = 10
                    
                    print(f"    📝 Registro {i+1}:")
                    print(f"       Hora[{hora_idx}]: {rec[hora_idx] if len(rec) > hora_idx else 'FORA_RANGE'}")
                    print(f"       Status[{status_idx}]: {rec[status_idx] if len(rec) > status_idx else 'FORA_RANGE'}")
                    
                    # Verificar status
                    if len(rec) > status_idx:
                        status = str(rec[status_idx])
                        is_completed = "Concluído" in status or "Completed" in status
                        print(f"       Status válido? {is_completed}")
                        
                        if is_completed and len(rec) > hora_idx:
                            hora = rec[hora_idx]
                            if hora:
                                # Extrair datetime (versão simplificada)
                                hora_str = str(hora)
                                import re
                                match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', hora_str)
                                if match:
                                    dt_str = match.group(1)
                                    try:
                                        dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                        
                                        print(f"       Data parsed: {dt_corrida}")
                                        print(f"       No range? {dt_ini <= dt_corrida <= dt_fim}")
                                        
                                        if dt_ini <= dt_corrida <= dt_fim:
                                            month_key = dt_corrida.strftime("%Y-%m")
                                            print(f"       Mês: {month_key}")
                                            
                                            if month_key in data_structure:
                                                data_structure[month_key]["concluidas"] += 1
                                                data_structure[month_key]["total"] += 1
                                                matched_count += 1
                                                print(f"       ✅ ADICIONADO! Total concluídas {month_key}: {data_structure[month_key]['concluidas']}")
                                        
                                    except Exception as e:
                                        print(f"       ❌ Erro parse datetime: {e}")
                                else:
                                    print(f"       ❌ Regex não encontrou datetime em: {hora_str}")
                            else:
                                print(f"       ❌ Campo hora vazio")
                    
                    if i >= 2:  # Só processar primeiros 3 para debug
                        break
            
            elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                print(f"  ✅ MATCH: Corridas canceladas")
                # Similar para canceladas...
                
            elif table_name in ["Missed Rides", "corridas_perdidas"]:
                print(f"  ✅ MATCH: Corridas perdidas")
                # Similar para perdidas...
                
            else:
                print(f"  ❌ NO MATCH: '{table_name}' não reconhecida")
        
        print(f"\n📊 RESUMO:")
        print(f"   Registros processados: {processed_count}")
        print(f"   Corridas válidas encontradas: {matched_count}")
        
        print(f"\n📈 RESULTADO FINAL:")
        for month, data in sorted(data_structure.items()):
            print(f"   {month}: {data['total']} total ({data['concluidas']} concluídas, {data['canceladas']} canceladas, {data['perdidas']} perdidas)")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(debug_comparative_logic())