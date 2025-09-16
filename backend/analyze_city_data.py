#!/usr/bin/env python3
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from services.city_service import normalize_city_name
import asyncio

async def analyze_city_data():
    """Analisar dados de cidades nos registros brutos"""
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/dashboard_db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        cities_found = {
            "completed": set(),
            "cancelled": set(),
            "missed": set()
        }

        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue

            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])

            if table_name in ["Completed Rides", "corridas_concluidas"]:
                for rec in new_records:
                    if len(rec) > 15:
                        city = str(rec[15]).strip() if rec[15] else None
                        if city:
                            normalized = normalize_city_name(city)
                            if normalized:
                                cities_found["completed"].add(normalized)

            elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                for rec in new_records:
                    # Verificar múltiplos índices para cidade
                    city = None
                    for idx in [8, 17, 15]:
                        if len(rec) > idx and rec[idx]:
                            city = str(rec[idx]).strip()
                            break
                    if city:
                        normalized = normalize_city_name(city)
                        if normalized:
                            cities_found["cancelled"].add(normalized)

            elif table_name in ["Missed Rides", "corridas_perdidas"]:
                for rec in new_records:
                    if len(rec) > 8 and rec[8]:
                        city = str(rec[8]).strip()
                        normalized = normalize_city_name(city)
                        if normalized:
                            cities_found["missed"].add(normalized)

        print("=== CIDADES ENCONTRADAS NOS DADOS BRUTOS ===")
        print(f"Completed Rides: {sorted(cities_found['completed'])}")
        print(f"Cancelled Rides: {sorted(cities_found['cancelled'])}")
        print(f"Missed Rides: {sorted(cities_found['missed'])}")

        # Verificar especificamente as cidades do filtro
        target_cities = ["MATUPA", "PEIXOTO DE AZEVEDO", "NOVA MONTE VERDE", "GUARANTA DO NORTE", "NOVA BANDEIRANTES"]

        print("\n=== VERIFICAÇÃO DAS CIDADES ALVO ===")
        for city in target_cities:
            normalized_target = normalize_city_name(city)
            print(f"\n{city} (normalizado: {normalized_target}):")
            print(f"  - Completed: {normalized_target in cities_found['completed']}")
            print(f"  - Cancelled: {normalized_target in cities_found['cancelled']}")
            print(f"  - Missed: {normalized_target in cities_found['missed']}")

if __name__ == "__main__":
    asyncio.run(analyze_city_data())