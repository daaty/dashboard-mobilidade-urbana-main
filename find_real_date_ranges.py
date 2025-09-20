#!/usr/bin/env python3
"""
Script para identificar exatamente quando são as datas das corridas reais
"""
import asyncio
import asyncpg
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

async def find_real_date_ranges():
    print("🔍 IDENTIFICANDO PERÍODO REAL DOS DADOS")
    print("=" * 60)
    
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'mobilidade_urbana'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'admin')
        )
        
        result = await conn.fetch("SELECT * FROM rides_data")
        
        all_dates = []
        
        for r in result:
            ride_data = r['ride_data']  # Usar notação de dicionário
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            source = r['source']  # Usar notação de dicionário
            
            for rec in new_records:
                dates_found = []
                
                # Para Excel/import_excel
                if source == "import_excel":
                    if table_name == "Completed Rides" or table_name == "rides_data":
                        # Data no índice 6
                        if len(rec) > 6 and rec[6]:
                            dates_found.append(rec[6])
                    elif table_name == "Cancelled Rides":
                        # Data no índice 11
                        if len(rec) > 11 and rec[11]:
                            dates_found.append(rec[11])
                    elif table_name == "Missed Rides":
                        # Data no índice 6
                        if len(rec) > 6 and rec[6]:
                            dates_found.append(rec[6])
                
                # Para Scraper/monitoring-service-adapted
                else:
                    if table_name == "Completed Rides":
                        # Data no índice 7
                        if len(rec) > 7 and rec[7]:
                            dates_found.append(rec[7])
                    elif table_name == "Cancelled Rides":
                        # Data no índice 12
                        if len(rec) > 12 and rec[12]:
                            dates_found.append(rec[12])
                    elif table_name == "Missed Rides":
                        # Data no índice 6
                        if len(rec) > 6 and rec[6]:
                            dates_found.append(rec[6])
                    elif table_name == "Scheduled Rides":
                        # Data no índice 10
                        if len(rec) > 10 and rec[10]:
                            dates_found.append(rec[10])
                        
                for date_str in dates_found:
                    if date_str and str(date_str) != "nan":
                        # Extrair datas no formato 2025-XX-XX
                        date_matches = re.findall(r'2025-\d{2}-\d{2}', str(date_str))
                        for match in date_matches:
                            try:
                                date_obj = datetime.strptime(match, "%Y-%m-%d")
                                all_dates.append({
                                    "date": date_obj,
                                    "table": table_name,
                                    "source": source,
                                    "raw": str(date_str)[:50]
                                })
                            except:
                                pass
        
        if all_dates:
            all_dates.sort(key=lambda x: x["date"])
            
            print(f"📊 TOTAL DE DATAS ENCONTRADAS: {len(all_dates)}")
            
            min_date = all_dates[0]["date"]
            max_date = all_dates[-1]["date"]
            
            print(f"\n📅 PERÍODO REAL DOS DADOS:")
            print(f"  De: {min_date.strftime('%Y-%m-%d')} ({min_date.strftime('%d/%m/%Y')})")
            print(f"  Até: {max_date.strftime('%Y-%m-%d')} ({max_date.strftime('%d/%m/%Y')})")
            
            # Mostrar distribuição por mês
            months = {}
            for item in all_dates:
                month_key = item["date"].strftime("%Y-%m")
                if month_key not in months:
                    months[month_key] = {"count": 0, "tables": set()}
                months[month_key]["count"] += 1
                months[month_key]["tables"].add(f"{item['table']} ({item['source']})")
            
            print(f"\n📊 DISTRIBUIÇÃO POR MÊS:")
            for month, data in sorted(months.items()):
                month_obj = datetime.strptime(f"{month}-01", "%Y-%m-%d")
                month_name = month_obj.strftime("%B %Y")
                print(f"  {month_name}: {data['count']} corridas")
                for table in sorted(data['tables']):
                    print(f"    - {table}")
            
            # Primeiras 10 datas
            print(f"\n🔍 PRIMEIRAS 10 CORRIDAS:")
            for item in all_dates[:10]:
                print(f"  {item['date'].strftime('%Y-%m-%d')}: {item['table']} ({item['source']}) - {item['raw']}")
            
            # Últimas 10 datas
            print(f"\n🔍 ÚLTIMAS 10 CORRIDAS:")
            for item in all_dates[-10:]:
                print(f"  {item['date'].strftime('%Y-%m-%d')}: {item['table']} ({item['source']}) - {item['raw']}")
        
        else:
            print("❌ Nenhuma data válida encontrada!")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(find_real_date_ranges())