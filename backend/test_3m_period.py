#!/usr/bin/env python3
"""
Teste específico da API com período de 3 meses
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from app.api.metrics import extract_datetime_from_record
from sqlalchemy.future import select

async def test_3m_period_processing():
    """Testa o processamento do período de 3 meses"""
    print("🧪 TESTANDO PROCESSAMENTO DO PERÍODO DE 3 MESES")
    print("=" * 50)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        # Definir período de 3 meses como na API
        now = datetime.now()
        dt_ini = now - timedelta(days=90)
        dt_fim = now

        print(f"📅 Período: {dt_ini.date()} até {dt_fim.date()}")

        # Processar como a API faz
        concluidas = []
        total_processed = 0
        date_issues = 0

        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue

            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])

            if table_name == "Completed Rides":
                for rec in new_records:
                    total_processed += 1

                    # Tentar extrair data como na API
                    dt_corrida = None

                    # Detectar se é dado do scraper ou Excel
                    if r.source == "monitoring-service-adapted":
                        # Dados do scraper
                        hora_solicitacao = rec[7] if len(rec) > 7 else None
                        hora_conclusao = rec[8] if len(rec) > 8 else None
                    else:
                        # Dados do Excel
                        hora_solicitacao = rec[6] if len(rec) > 6 else None
                        hora_conclusao = rec[7] if len(rec) > 7 else None

                    # Usar hora de conclusão como principal
                    hora = hora_conclusao or hora_solicitacao

                    if hora:
                        dt_str = extract_datetime_from_record([hora], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                dt_corrida = None
                                date_issues += 1

                    # Verificar se está no período
                    if dt_corrida and dt_ini <= dt_corrida <= dt_fim:
                        concluidas.append({
                            "id": rec[0] if len(rec) > 0 else None,
                            "data": dt_corrida
                        })

        print("\n📈 RESULTADOS:")
        print(f"   🔢 Total de corridas processadas: {total_processed}")
        print(f"   📅 Problemas de data: {date_issues}")
        print(f"   ✅ Corridas no período de 3 meses: {len(concluidas)}")

        if concluidas:
            print("\n🔍 Amostra de corridas encontradas:")
            for i, corrida in enumerate(concluidas[:5]):
                print(f"   {i+1}. ID: {corrida['id']}, Data: {corrida['data']}")

        # Verificar se o problema está na extração de datas
        print("\n🔧 Verificando extração de datas:")
        sample_dates = []
        count = 0
        for r in rides:
            if count >= 10:  # Apenas primeiras 10
                break

            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue

            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])

            if table_name == "Completed Rides" and new_records:
                rec = new_records[0]
                if len(rec) > 7:
                    hora = rec[7]  # hora_conclusao
                    dt_str = extract_datetime_from_record([hora], 0)
                    sample_dates.append({
                        "hora_original": str(hora)[:50],
                        "dt_extraida": dt_str
                    })
                    count += 1

        print("   📅 Amostra de extração de datas:")
        for i, sample in enumerate(sample_dates[:5]):
            print(f"      {i+1}. Original: '{sample['hora_original']}' → Extraída: '{sample['dt_extraida']}'")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_3m_period_processing())