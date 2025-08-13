#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.drivers_data import DriversData
import json
from dotenv import load_dotenv

load_dotenv()

def check_drivers_data():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        print(f'🔍 Total de registros drivers_data: {len(drivers)}')
        
        if len(drivers) == 0:
            print("❌ Nenhum registro encontrado na tabela drivers_data")
            return
            
        for i, driver in enumerate(drivers):
            print(f'\n📋 Registro {i+1}:')
            print(f'  🆔 ID: {driver.id}')
            print(f'  🚗 Driver ID: {driver.driver_id}')
            print(f'  👤 Name: {driver.name}')
            print(f'  📧 Email: {driver.email}')
            print(f'  📱 Mobile: {driver.mobile}')
            print(f'  🏷️ Data Type: {driver.data_type}')
            print(f'  📅 Scraped At: {driver.scraped_at}')
            
            if driver.additional_data:
                try:
                    data = json.loads(driver.additional_data)
                    print(f'  📊 Additional Data Keys: {list(data.keys())}')
                    if 'status' in data:
                        print(f'  ⚡ Status: {data["status"]}')
                    if 'rating' in data:
                        print(f'  ⭐ Rating: {data["rating"]}')
                    if 'total_rides' in data:
                        print(f'  🚖 Total Rides: {data["total_rides"]}')
                except Exception as e:
                    print(f'  ❌ Additional Data: JSON inválido - {e}')
            else:
                print(f'  ❌ Additional Data: Vazio')
            print('=' * 50)

if __name__ == "__main__":
    check_drivers_data()
