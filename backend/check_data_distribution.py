#!/usr/bin/env python3
"""
Verificar distribuição de dados por período
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy.future import select

async def check_data_distribution():
    """Verifica distribuição de dados por período"""
    print("📊 VERIFICANDO DISTRIBUIÇÃO DE DADOS POR PERÍODO")
    print("=" * 55)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        now = datetime.now()

        # Definir diferentes períodos
        periods = {
            "hoje": (now.replace(hour=0, minute=0, second=0, microsecond=0), now),
            "7d": (now - timedelta(days=7), now),
            "30d": (now - timedelta(days=30), now),
            "3m": (now - timedelta(days=90), now),
            "6m": (now - timedelta(days=180), now),
            "12m": (now - timedelta(days=365), now)
        }

        print(f"📅 Data atual: {now.date()}")
        print(f"📊 Total de registros no banco: {len(rides)}")

        # Verificar distribuição por período
        for period_name, (dt_ini, dt_fim) in periods.items():
            completed_in_period = 0
            total_rides_in_period = 0

            for r in rides:
                if r.ride_data:
                    try:
                        ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                        table_name = ride_data.get("tableName", "")
                        new_records = ride_data.get("newRecords", [])

                        if table_name == "Completed Rides":
                            for rec in new_records:
                                total_rides_in_period += 1

                                # Verificar se está no período (usando scraped_at)
                                if hasattr(r, 'scraped_at') and r.scraped_at:
                                    if dt_ini <= r.scraped_at <= dt_fim:
                                        completed_in_period += 1
                    except:
                        continue

            print(f"\n📆 Período: {period_name}")
            print(f"   🏁 Início: {dt_ini.date()}")
            print(f"   🎯 Fim: {dt_fim.date()}")
            print(f"   ✅ Completed Rides: {completed_in_period}")
            print(f"   🔢 Total de corridas no período: {total_rides_in_period}")

        # Verificar as datas mais recentes dos dados
        print("\n📅 DATAS MAIS RECENTES DOS DADOS:")
        recent_dates = []
        for r in rides:
            if hasattr(r, 'scraped_at') and r.scraped_at:
                recent_dates.append(r.scraped_at)

        if recent_dates:
            recent_dates.sort(reverse=True)
            print(f"   🕒 Data mais recente: {recent_dates[0]}")
            print(f"   📅 Data mais antiga: {recent_dates[-1]}")
            print(f"   📊 Total de registros com data: {len(recent_dates)}")

            # Contar por mês
            from collections import defaultdict
            monthly_count = defaultdict(int)
            for date in recent_dates:
                month_key = f"{date.year}-{date.month:02d}"
                monthly_count[month_key] += 1

            print("\n📈 Distribuição mensal:")
            for month in sorted(monthly_count.keys(), reverse=True):
                print(f"      {month}: {monthly_count[month]} registros")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_data_distribution())