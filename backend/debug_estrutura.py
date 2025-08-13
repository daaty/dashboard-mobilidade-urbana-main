#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
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
        rides = session.query(RidesData).filter_by(table_name="Cancelled Rides").all()
        
        for ride in rides:
            if not ride.ride_data:
                continue
                
            try:
                ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                new_records = ride_data.get("newRecords", [])
                
                print("🔍 Estrutura completa do primeiro registro cancelado:")
                if new_records:
                    rec = new_records[0]
                    for i, value in enumerate(rec):
                        print(f"  [{i}]: {value} ({type(value).__name__})")
                        
                    print("\n📋 Análise dos campos importantes:")
                    print(f"  [0] ID: {rec[0]}")
                    print(f"  [2] Nome passageiro: {rec[2]}")
                    print(f"  [9] Campo atual (--): {rec[9]}")  
                    print(f"  [10] Campo atual (--): {rec[10]}")
                    print(f"  [11] Data real: {rec[11]}")
                    print(f"  [12] Motivo cancelamento: {rec[12]}")
                    print(f"  [13] Responsável cancelamento: {rec[13]}")
                        
            except Exception as e:
                print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
