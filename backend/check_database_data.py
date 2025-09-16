#!/usr/bin/env python3
"""
Verificar se há dados no banco para o período solicitado
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy.future import select

async def check_database_data():
    """Verifica se há dados no banco de dados"""
    print("🔍 VERIFICANDO DADOS NO BANCO DE DADOS")
    print("=" * 50)

    async with SessionLocal() as session:
        # Buscar todos os registros
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Total de registros na tabela rides_data: {len(rides)}")

        # Verificar tipos de tabelas
        table_types = {}
        for ride in rides:
            if ride.ride_data:
                try:
                    ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                    table_name = ride_data.get("tableName", "Unknown")
                    if table_name not in table_types:
                        table_types[table_name] = 0
                    table_types[table_name] += 1
                except:
                    continue

        print("\n📋 Tipos de tabelas encontradas:")
        for table_name, count in table_types.items():
            print(f"   {table_name}: {count} registros")

        # Verificar dados de Completed Rides
        completed_rides = [r for r in rides if r.ride_data and
                          (json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data)
                          .get("tableName") == "Completed Rides"]

        print(f"\n✅ Completed Rides encontradas: {len(completed_rides)}")

        if completed_rides:
            # Verificar algumas amostras
            print("\n🔍 Amostra de dados de Completed Rides:")
            for i, ride in enumerate(completed_rides[:3]):
                try:
                    ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                    new_records = ride_data.get("newRecords", [])
                    print(f"   Registro {i+1}: {len(new_records)} corridas")
                    if new_records:
                        print(f"      Primeira corrida: {new_records[0][:5]}...")
                except Exception as e:
                    print(f"      Erro ao processar: {e}")

        # Verificar período dos dados
        print("\n📅 Verificando período dos dados:")
        now = datetime.now()
        dt_30d_ago = now - timedelta(days=30)

        recent_rides = []
        for ride in completed_rides:
            if hasattr(ride, 'scraped_at') and ride.scraped_at:
                if ride.scraped_at >= dt_30d_ago:
                    recent_rides.append(ride)

        print(f"   Corridas dos últimos 30 dias: {len(recent_rides)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_database_data())