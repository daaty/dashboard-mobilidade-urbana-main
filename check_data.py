import asyncio
import sys
sys.path.append('backend')
from backend.app.database.db import SessionLocal
from backend.app.models.rides_data import RidesData
from sqlalchemy.future import select
import json

async def check_data():
    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()
        print(f'Total de registros encontrados: {len(rides)}')
        
        for i, ride in enumerate(rides):
            print(f'Registro {i+1}:')
            print(f'  table_name: {ride.table_name}')
            print(f'  source: {ride.source}')
            print(f'  scraped_at: {ride.scraped_at}')
            
            # Verificar estrutura do JSON
            try:
                data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                table_name = data.get('tableName', 'N/A')
                records_count = len(data.get('newRecords', []))
                print(f'  tableName: {table_name}')
                print(f'  newRecords count: {records_count}')
                
                if data.get('newRecords') and records_count > 0:
                    sample = data['newRecords'][0]
                    print(f'  Sample record length: {len(sample)}')
                    print(f'  Sample record first 5 fields: {sample[:5] if len(sample) > 5 else sample}')
                    
            except Exception as e:
                print(f'  Erro ao processar JSON: {e}')
            print()

if __name__ == "__main__":
    asyncio.run(check_data())
