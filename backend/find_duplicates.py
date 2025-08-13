#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
import json
from datetime import datetime, timedelta
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

def find_duplicate_ids():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    now = datetime.now()
    dt_ini = now - timedelta(days=150)
    dt_fim = now
    
    all_rides = []
    
    with SessionLocal() as session:
        rides = session.query(RidesData).all()
        
        for ride_entry in rides:
            try:
                data = json.loads(ride_entry.ride_data)
                table_name = data.get("tableName", "")
                records = data.get("newRecords", [])
                
                for rec in records:
                    city = None
                    date_field = None
                    
                    if table_name == "Completed Rides" and len(rec) > 15:
                        city = rec[15] if len(rec) > 15 else None
                        date_field = rec[6] if len(rec) > 6 else None
                        
                    elif table_name == "Cancelled Rides" and len(rec) > 17:
                        city = rec[17] if len(rec) > 17 else None
                        date_field = rec[11] if len(rec) > 11 else None
                        
                    elif table_name == "Missed Rides" and len(rec) > 8:
                        city = rec[8] if len(rec) > 8 else None
                        date_field = rec[6] if len(rec) > 6 else None
                    
                    # Verificar se a data está no período
                    valid_date = False
                    if date_field and "2025" in str(date_field):
                        try:
                            dt_corrida = datetime.strptime(str(date_field), "%Y-%m-%d %H:%M:%S")
                            if dt_ini <= dt_corrida <= dt_fim:
                                valid_date = True
                        except:
                            pass
                    
                    if valid_date:
                        if city:
                            city = str(city).strip()
                            if city in ['', 'nan', '--', 'Unnamed']:
                                city = "SEM_CIDADE"
                        else:
                            city = "SEM_CIDADE"
                        
                        ride_id = rec[0] if len(rec) > 0 else None
                        all_rides.append({
                            'type': table_name,
                            'city': city,
                            'id': ride_id,
                            'date': date_field
                        })
                        
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # Encontrar duplicatas
        ids = [r['id'] for r in all_rides if r['id']]
        id_counter = Counter(ids)
        duplicates = {id_val: count for id_val, count in id_counter.items() if count > 1}
        
        print(f"🔍 DUPLICATAS ENCONTRADAS:")
        for dup_id, count in duplicates.items():
            print(f"\n  ID {dup_id} aparece {count} vezes:")
            for ride in all_rides:
                if ride['id'] == dup_id:
                    print(f"    - {ride['type']}: {ride['city']} ({ride['date']})")
        
        print(f"\n📊 RESUMO:")
        print(f"  Total de corridas: {len(all_rides)}")
        print(f"  IDs únicos: {len(set(ids))}")
        print(f"  Duplicatas: {len(duplicates)} IDs duplicados")
        print(f"  Registros extras: {len(all_rides) - len(set(ids))}")

if __name__ == "__main__":
    find_duplicate_ids()
