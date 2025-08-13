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

def analyze_missed_rides():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Buscar corridas perdidas
        missed_rides = session.query(RidesData).filter(
            RidesData.table_name == "Missed Rides"
        ).all()
        
        print(f"🔍 Encontradas {len(missed_rides)} entradas de corridas perdidas")
        
        for ride_entry in missed_rides:
            try:
                data = json.loads(ride_entry.ride_data)
                records = data.get("newRecords", [])
                print(f"\n📊 Processando {len(records)} registros...")
                
                # Analisar estrutura dos primeiros registros
                for i, rec in enumerate(records[:5]):  # Primeiros 5 para análise
                    print(f"\n🔍 Registro {i+1}:")
                    print(f"  📋 Estrutura completa: {rec}")
                    print(f"  📏 Tamanho: {len(rec)} campos")
                    
                    # Identificar onde podem estar os campos importantes
                    for idx, field in enumerate(rec):
                        field_str = str(field)
                        if "2025" in field_str or "2024" in field_str:
                            print(f"  📅 Possível data no índice {idx}: {field}")
                        elif isinstance(field, str) and len(field) > 10 and any(char.isalpha() for char in field):
                            print(f"  👤 Possível nome no índice {idx}: {field}")
                        elif isinstance(field, (int, float)) and len(str(field)) > 8:
                            print(f"  📞 Possível telefone no índice {idx}: {field}")
                            
            except Exception as e:
                print(f"❌ Erro ao processar dados JSON: {e}")

if __name__ == "__main__":
    analyze_missed_rides()
