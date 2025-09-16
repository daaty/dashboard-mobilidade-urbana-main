import sys
import os
import asyncio
import json
import re
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select

def extract_datetime_from_record(rec, index):
    """Extrai data/hora de um registro, lidando com AMBOS os formatos (scraper + frontend)"""
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

async def debug_overview_endpoint():
    """Debug do endpoint overview para entender por que retorna dados zerados"""

    # Configurar período "hoje"
    now = datetime.now()
    dt_ini = now.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_fim = now

    print(f"Período filtro: {dt_ini} até {dt_fim}")
    print(f"Data atual: {now}")

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"\nTotal de registros na tabela: {len(rides)}")

        total_concluidas = 0
        total_canceladas = 0
        total_perdidas = 0

        for i, r in enumerate(rides[:5]):  # Analisar apenas os primeiros 5 registros
            print(f"\n--- Registro {i+1} ---")
            print(f"ID: {r.id}, Source: {r.source}")

            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    print(f"Table name: {table_name}")
                    print(f"Records count: {len(new_records)}")

                    if new_records:
                        print("Analisando primeiros 3 records:")
                        for j, rec in enumerate(new_records[:3]):
                            print(f"  Record {j}: {rec}")

                            # Tentar extrair data
                            if table_name in ["Completed Rides", "corridas_concluidas"]:
                                # Para Completed Rides, tentar diferentes índices de data
                                for idx in [7, 8, 6]:
                                    if idx < len(rec) and rec[idx]:
                                        dt_str = extract_datetime_from_record([rec[idx]], 0)
                                        if dt_str:
                                            try:
                                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                                print(f"    Data extraída (idx {idx}): {dt_corrida}")
                                                if dt_ini <= dt_corrida <= dt_fim:
                                                    total_concluidas += 1
                                                    print("    ✅ Dentro do período HOJE!")
                                                break
                                            except Exception as e:
                                                print(f"    Erro ao parsear data: {e}")
                            elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                                # Para Cancelled Rides, tentar diferentes índices
                                for idx in [12, 11, 8, 7]:
                                    if idx < len(rec) and rec[idx]:
                                        dt_str = extract_datetime_from_record([rec[idx]], 0)
                                        if dt_str:
                                            try:
                                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                                print(f"    Data extraída (idx {idx}): {dt_corrida}")
                                                if dt_ini <= dt_corrida <= dt_fim:
                                                    total_canceladas += 1
                                                    print("    ✅ Dentro do período HOJE!")
                                                break
                                            except Exception as e:
                                                print(f"    Erro ao parsear data: {e}")

                except Exception as e:
                    print(f"Erro ao processar registro: {e}")

        print("\n--- RESULTADO FINAL ---")
        print(f"Concluídas encontradas: {total_concluidas}")
        print(f"Canceladas encontradas: {total_canceladas}")
        print(f"Perdidas encontradas: {total_perdidas}")

if __name__ == "__main__":
    asyncio.run(debug_overview_endpoint())