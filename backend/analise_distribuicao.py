import sys
import os
import asyncio
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select

def extract_datetime_from_record(rec, index):
    """Extrai data/hora de um registro"""
    if index >= len(rec):
        return None

    value = str(rec[index]).strip()

    # Formato do scraper: "202508202025-08-20 16:59:50"
    scraper_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", value)
    if scraper_match:
        return scraper_match.group(1)

    # Formato do frontend: "2025-08-20 16:59:50"
    frontend_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", value)
    if frontend_match:
        return frontend_match.group(1)

    return None

async def analyze_data_distribution():
    """Analisa distribuição temporal dos dados"""

    print("=== ANÁLISE DE DISTRIBUIÇÃO TEMPORAL DOS DADOS ===\n")

    # Contadores por data
    data_por_dia = defaultdict(lambda: {"completed": 0, "cancelled": 0, "missed": 0, "total": 0})
    datas_unicas = set()

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"Total de registros na tabela: {len(rides)}\n")

        for i, r in enumerate(rides):
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name in ["Completed Rides", "Cancelled Rides", "Missed Rides"]:
                        for rec in new_records:
                            # Tentar extrair data dos índices mais prováveis
                            data_indices = []
                            if table_name == "Completed Rides":
                                data_indices = [7, 8, 6]
                            elif table_name == "Cancelled Rides":
                                data_indices = [12, 11, 8, 7]
                            elif table_name == "Missed Rides":
                                data_indices = [6]

                            for idx in data_indices:
                                if idx < len(rec) and rec[idx]:
                                    dt_str = extract_datetime_from_record([rec[idx]], 0)
                                    if dt_str:
                                        try:
                                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                            data_str = dt_corrida.strftime("%Y-%m-%d")
                                            datas_unicas.add(data_str)

                                            # Incrementar contador
                                            if table_name == "Completed Rides":
                                                data_por_dia[data_str]["completed"] += 1
                                            elif table_name == "Cancelled Rides":
                                                data_por_dia[data_str]["cancelled"] += 1
                                            elif table_name == "Missed Rides":
                                                data_por_dia[data_str]["missed"] += 1

                                            data_por_dia[data_str]["total"] += 1
                                            break
                                        except Exception as e:
                                            continue

                except Exception as e:
                    continue

        # Ordenar datas e mostrar distribuição
        datas_ordenadas = sorted(datas_unicas)

        print("=== DISTRIBUIÇÃO POR DATA ===")
        print("Data\t\tConcluídas\tCanceladas\tPerdidas\tTotal")
        print("-" * 60)

        for data in datas_ordenadas:
            stats = data_por_dia[data]
            print(f"{data}\t{stats['completed']}\t\t{stats['cancelled']}\t\t{stats['missed']}\t\t{stats['total']}")

        print(f"\nTotal de datas únicas encontradas: {len(datas_unicas)}")
        print(f"Período coberto: {min(datas_ordenadas)} até {max(datas_ordenadas)}")

        # Análise dos últimos dias
        hoje = datetime.now().strftime("%Y-%m-%d")
        ontem = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        print("\n=== ANÁLISE DOS ÚLTIMOS DIAS ===")
        print(f"Hoje ({hoje}): {data_por_dia[hoje]['total']} registros")
        print(f"Ontem ({ontem}): {data_por_dia[ontem]['total']} registros")

        # Verificar se há dados recentes
        ultimas_7_datas = sorted(datas_unicas, reverse=True)[:7]
        print("\nÚltimas 7 datas com dados:")
        for data in ultimas_7_datas:
            stats = data_por_dia[data]
            print(f"  {data}: {stats['total']} registros")

if __name__ == "__main__":
    asyncio.run(analyze_data_distribution())