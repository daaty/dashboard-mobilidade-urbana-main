import asyncio
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from services.city_service import normalize_city_name, extract_city_from_address

def analyze_cancelled_structure(records):
    """Analisa a estrutura específica dos dados de corridas canceladas"""
    print("\n=== ANÁLISE DETALHADA - CANCELLED RIDES ===")

    for i, record in enumerate(records[:3]):  # Analisar apenas os primeiros 3
        print(f"\n--- Registro {i+1} ---")
        rec_data = json.loads(record.ride_data) if isinstance(record.ride_data, str) else record.ride_data

        if 'newRecords' in rec_data and rec_data['newRecords']:
            for j, ride in enumerate(rec_data['newRecords'][:2]):  # Apenas 2 corridas por registro
                print(f"Corrida {j+1}: {len(ride)} campos")
                for k, field in enumerate(ride):
                    print(f"  [{k}]: {field}")

                    # Tentar detectar cidade neste campo
                    if isinstance(field, str) and len(field) > 5:
                        normalized = normalize_city_name(field)
                        if normalized and normalized != "Unnamed":
                            print(f"    -> CIDADE DETECTADA: {normalized}")
                        else:
                            extracted = extract_city_from_address(field)
                            if extracted:
                                print(f"    -> CIDADE EXTRAÍDA: {extracted}")

def analyze_missed_structure(records):
    """Analisa a estrutura específica dos dados de corridas perdidas"""
    print("\n=== ANÁLISE DETALHADA - MISSED RIDES ===")

    for i, record in enumerate(records[:3]):  # Analisar apenas os primeiros 3
        print(f"\n--- Registro {i+1} ---")
        rec_data = json.loads(record.ride_data) if isinstance(record.ride_data, str) else record.ride_data

        if 'newRecords' in rec_data and rec_data['newRecords']:
            for j, ride in enumerate(rec_data['newRecords'][:2]):  # Apenas 2 corridas por registro
                print(f"Corrida {j+1}: {len(ride)} campos")
                for k, field in enumerate(ride):
                    print(f"  [{k}]: {field}")

                    # Tentar detectar cidade neste campo
                    if isinstance(field, str) and len(field) > 5:
                        normalized = normalize_city_name(field)
                        if normalized and normalized != "Unnamed":
                            print(f"    -> CIDADE DETECTADA: {normalized}")
                        else:
                            extracted = extract_city_from_address(field)
                            if extracted:
                                print(f"    -> CIDADE EXTRAÍDA: {extracted}")

async def analyze_structures():
    """Analisa estruturas de dados de corridas canceladas e perdidas"""
    async with SessionLocal() as session:
        # Analisar Cancelled Rides
        query = select(RidesData).where(RidesData.table_name == "Cancelled Rides").limit(3)
        result = await session.execute(query)
        cancelled_records = result.scalars().all()
        analyze_cancelled_structure(cancelled_records)

        # Analisar Missed Rides
        query = select(RidesData).where(RidesData.table_name == "Missed Rides").limit(3)
        result = await session.execute(query)
        missed_records = result.scalars().all()
        analyze_missed_structure(missed_records)

if __name__ == "__main__":
    # Adicionar caminho do projeto
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    import json
    asyncio.run(analyze_structures())