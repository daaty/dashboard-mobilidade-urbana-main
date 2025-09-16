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

async def debug_hoje_filter():
    """Debug específico do filtro de hoje"""

    # Configurar período "hoje" exatamente como no endpoint
    now = datetime.now()
    dt_ini = now.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_fim = now
    dt_ini_ant = dt_ini - timedelta(days=1)
    dt_fim_ant = dt_ini

    print("=== CONFIGURAÇÃO DO FILTRO HOJE ===")
    print(f"Data/hora atual: {now}")
    print(f"dt_ini (início hoje): {dt_ini}")
    print(f"dt_fim (agora): {dt_fim}")
    print(f"dt_ini_ant (início ontem): {dt_ini_ant}")
    print(f"dt_fim_ant (fim ontem): {dt_fim_ant}")
    print()

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"Total de registros na tabela: {len(rides)}")
        print()

        total_hoje = 0
        total_ontem = 0

        # Analisar apenas registros que podem ter datas recentes
        for i, r in enumerate(rides):
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name in ["Completed Rides", "Cancelled Rides", "Missed Rides"]:
                        print(f"--- Registro {i+1}: {table_name} ({len(new_records)} records) ---")

                        for j, rec in enumerate(new_records[:2]):  # Apenas primeiros 2 para debug
                            print(f"  Record {j}: {rec}")

                            # Tentar extrair data dos índices mais prováveis
                            data_indices = []
                            if table_name == "Completed Rides":
                                data_indices = [7, 8, 6]  # data_conclusao, data_solicitacao
                            elif table_name == "Cancelled Rides":
                                data_indices = [12, 11, 8, 7]  # vários possíveis
                            elif table_name == "Missed Rides":
                                data_indices = [6]  # data

                            dt_corrida = None
                            for idx in data_indices:
                                if idx < len(rec) and rec[idx]:
                                    dt_str = extract_datetime_from_record([rec[idx]], 0)
                                    if dt_str:
                                        try:
                                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                            print(f"    ✅ Data encontrada no idx {idx}: {dt_corrida}")

                                            # Verificar se cai nos filtros
                                            if dt_ini <= dt_corrida <= dt_fim:
                                                print("    🎯 DENTRO DO PERÍODO HOJE!")
                                                total_hoje += 1
                                            elif dt_ini_ant <= dt_corrida < dt_fim_ant:
                                                print("    📅 DENTRO DO PERÍODO ONTEM!")
                                                total_ontem += 1
                                            else:
                                                print(f"    ❌ Fora do período (diferença: {(dt_corrida - dt_ini).days} dias)")
                                            break
                                        except Exception as e:
                                            print(f"    ❌ Erro ao parsear data: {e}")
                                else:
                                    print(f"    ⚠️  idx {idx} fora dos limites ou vazio")

                            if not dt_corrida:
                                print("    ❌ Nenhuma data válida encontrada neste record")

                except Exception as e:
                    print(f"Erro ao processar registro {i}: {e}")

        print("\n=== RESULTADO FINAL ===")
        print(f"Records encontrados para HOJE: {total_hoje}")
        print(f"Records encontrados para ONTEM: {total_ontem}")

if __name__ == "__main__":
    asyncio.run(debug_hoje_filter())