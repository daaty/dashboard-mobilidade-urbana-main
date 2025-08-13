#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_completed_rides_processing():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Buscar corridas concluídas
        completed_rides = session.query(RidesData).filter(
            RidesData.table_name == "Completed Rides"
        ).all()
        
        print(f"🔍 Encontradas {len(completed_rides)} entradas de corridas concluídas")
        
        for ride_entry in completed_rides:
            try:
                data = json.loads(ride_entry.ride_data)
                records = data.get("newRecords", [])
                print(f"\n📊 Processando {len(records)} registros...")
                
                # Testar processamento como na API
                concluidas = []
                for i, rec in enumerate(records[:3]):  # Só primeiros 3 para debug
                    print(f"\n🔍 Registro {i+1}:")
                    print(f"  📋 Estrutura completa: {rec}")
                    print(f"  📏 Tamanho: {len(rec)} campos")
                    
                    try:
                        # Tentar extrair dados como na API original
                        if len(rec) >= 12:
                            ride_id = rec[0]
                            passenger = rec[1] if len(rec) > 1 else "N/A"
                            driver = rec[2] if len(rec) > 2 else "N/A"
                            phone = rec[3] if len(rec) > 3 else "N/A"
                            address = rec[4] if len(rec) > 4 else "N/A"
                            
                            # Procurar campo de data
                            date_field = None
                            for idx, field in enumerate(rec):
                                if isinstance(field, str) and ("2025" in str(field) or "2024" in str(field)):
                                    date_field = field
                                    print(f"  📅 Data encontrada no índice {idx}: {field}")
                                    break
                            
                            print(f"  🆔 ID: {ride_id}")
                            print(f"  👤 Passageiro: {passenger}")
                            print(f"  🚗 Motorista: {driver}")
                            print(f"  📞 Telefone: {phone}")
                            print(f"  📍 Endereço: {address}")
                            print(f"  📅 Data: {date_field}")
                            
                        else:
                            print(f"  ❌ Registro muito pequeno: {len(rec)} campos")
                            
                    except Exception as e:
                        print(f"  ❌ Erro ao processar registro: {e}")
                        
            except Exception as e:
                print(f"❌ Erro ao processar dados JSON: {e}")

if __name__ == "__main__":
    test_completed_rides_processing()
