#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
import json
from dotenv import load_dotenv

load_dotenv()

def analyze_all_cities():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        rides = session.query(RidesData).all()
        
        for ride_entry in rides:
            try:
                data = json.loads(ride_entry.ride_data)
                table_name = data.get("tableName", "")
                records = data.get("newRecords", [])
                
                print(f"\n🏷️ {table_name} - {len(records)} registros")
                
                if len(records) > 0:
                    rec = records[0]  # Primeiro registro para análise
                    print(f"📋 Estrutura: {len(rec)} campos")
                    
                    if table_name == "Completed Rides":
                        # Índice 15 seria a cidade nas corridas concluídas
                        print(f"🏙️ Possível cidade (último campo): {rec[-1] if len(rec) > 0 else 'N/A'}")
                        
                    elif table_name == "Cancelled Rides":
                        # Verificar onde está a cidade nas canceladas
                        for idx, field in enumerate(rec):
                            if isinstance(field, str) and len(field) < 20 and field.isupper():
                                print(f"🏙️ Possível cidade no índice {idx}: {field}")
                                
                    elif table_name == "Missed Rides":
                        print(f"🏙️ Cidade no índice 8: {rec[8] if len(rec) > 8 else 'N/A'}")
                        
            except Exception as e:
                print(f"❌ Erro: {e}")

if __name__ == "__main__":
    analyze_all_cities()
