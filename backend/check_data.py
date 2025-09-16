import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select
import json

async def check_rides_data():
    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()
        print(f'Total de registros na tabela rides_data: {len(rides)}')

        if rides:
            print('\nPrimeiro registro:')
            ride = rides[0]
            print(f'ID: {ride.id}')
            print(f'Source: {ride.source}')
            print(f'Scraped at: {ride.scraped_at}')

            if ride.ride_data:
                try:
                    data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                    print(f'Table name: {data.get("tableName")}')
                    records = data.get('newRecords', [])
                    print(f'Number of records: {len(records)}')
                    if records:
                        print('Primeiro record:')
                        print(records[0])
                except Exception as e:
                    print(f'Erro ao parsear ride_data: {e}')
        else:
            print('Nenhum registro encontrado na tabela')

if __name__ == "__main__":
    asyncio.run(check_rides_data())