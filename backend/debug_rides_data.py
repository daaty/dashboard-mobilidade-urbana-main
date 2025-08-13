#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
import json
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    # Converter para psycopg2 para conexão síncrona
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        rides = session.query(RidesData).all()
        print(f'Total de registros rides_data: {len(rides)}')
        
        if len(rides) == 0:
            print("❌ Nenhum registro encontrado na tabela rides_data")
            return
            
        for i, ride in enumerate(rides):
            print(f'\n📋 Registro {i+1}:')
            print(f'  🆔 ID: {ride.id}')
            print(f'  📝 table_name: {ride.table_name}')
            print(f'  📤 source: {ride.source}')
            print(f'  📅 scraped_at: {ride.scraped_at}')
            print(f'  🔗 data_hash: {ride.data_hash[:20]}...' if ride.data_hash else '  🔗 data_hash: None')
            
            if ride.ride_data:
                try:
                    data = json.loads(ride.ride_data)
                    print(f'  🏷️ tableName: {data.get("tableName", "N/A")}')
                    records = data.get("newRecords", [])
                    print(f'  📊 newRecords count: {len(records)}')
                    
                    if len(records) > 0:
                        print(f'  👀 Primeiro registro: {records[0][:5] if len(records[0]) >= 5 else records[0]}')
                        
                except Exception as e:
                    print(f'  ❌ ride_data: JSON inválido - {e}')
            else:
                print(f'  ❌ ride_data: Vazio')
            print('=' * 50)

if __name__ == "__main__":
    main()
