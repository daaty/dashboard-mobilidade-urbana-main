#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def debug_city_counts():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Configurar período como na API
    now = datetime.now()
    dt_ini = now - timedelta(days=150)  # Mesmo período da API
    dt_fim = now
    
    all_rides = []
    city_counts = {}
    
    with SessionLocal() as session:
        rides = session.query(RidesData).all()
        
        print(f"🔍 Total de registros na tabela: {len(rides)}")
        
        for ride_entry in rides:
            try:
                data = json.loads(ride_entry.ride_data)
                table_name = data.get("tableName", "")
                records = data.get("newRecords", [])
                
                print(f"\n📋 {table_name}: {len(records)} registros")
                
                for rec in records:
                    city = None
                    date_field = None
                    
                    # Extrair cidade e data baseado no tipo
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
                        # Normalizar cidade
                        if city:
                            city = str(city).strip()
                            if city in ['', 'nan', '--', 'Unnamed']:
                                city = "SEM_CIDADE"
                        else:
                            city = "SEM_CIDADE"
                        
                        all_rides.append({
                            'type': table_name,
                            'city': city,
                            'id': rec[0] if len(rec) > 0 else None
                        })
                        
                        # Contar por cidade
                        if city not in city_counts:
                            city_counts[city] = {'total': 0, 'completed': 0, 'cancelled': 0, 'missed': 0}
                        
                        city_counts[city]['total'] += 1
                        if table_name == "Completed Rides":
                            city_counts[city]['completed'] += 1
                        elif table_name == "Cancelled Rides":
                            city_counts[city]['cancelled'] += 1
                        elif table_name == "Missed Rides":
                            city_counts[city]['missed'] += 1
                        
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        print(f"\n📊 RESUMO GERAL:")
        print(f"Total de corridas válidas: {len(all_rides)}")
        
        print(f"\n🏙️ CONTAGEM POR CIDADE:")
        total_verificacao = 0
        for cidade, counts in city_counts.items():
            print(f"  {cidade}: {counts['total']} total ({counts['completed']} concluídas, {counts['cancelled']} canceladas, {counts['missed']} perdidas)")
            total_verificacao += counts['total']
        
        print(f"\n🔢 VERIFICAÇÃO:")
        print(f"  Soma das cidades: {total_verificacao}")
        print(f"  Total direto: {len(all_rides)}")
        print(f"  Diferença: {abs(total_verificacao - len(all_rides))}")
        
        # Verificar duplicatas por ID
        ids = [r['id'] for r in all_rides if r['id']]
        unique_ids = set(ids)
        print(f"\n🔍 ANÁLISE DE IDs:")
        print(f"  Total de IDs: {len(ids)}")
        print(f"  IDs únicos: {len(unique_ids)}")
        print(f"  Duplicatas: {len(ids) - len(unique_ids)}")

if __name__ == "__main__":
    debug_city_counts()
