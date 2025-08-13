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

def find_status_column():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        print(f'🔍 Procurando pela coluna STATUS que contém online/offline')
        print(f'Total de registros: {len(drivers)}')
        
        online_drivers = []
        offline_drivers = []
        
        for driver in drivers:
            driver_id = driver.driver_id
            driver_name = driver.name
            
            # Verificar additional_data
            try:
                if isinstance(driver.additional_data, dict):
                    data = driver.additional_data
                else:
                    data = json.loads(driver.additional_data) if driver.additional_data else {}
                
                # Procurar por todas as chaves que contenham "status" ou valores "online"/"offline"
                status_found = None
                
                for key, value in data.items():
                    value_str = str(value).lower()
                    key_str = str(key).lower()
                    
                    # Procurar explicitamente por "online" ou "offline"
                    if 'online' in value_str:
                        status_found = f"{key}: {value} (ONLINE)"
                        online_drivers.append({
                            'id': driver_id,
                            'name': driver_name,
                            'status_field': key,
                            'status_value': value,
                            'data_type': driver.data_type
                        })
                        break
                    elif 'offline' in value_str:
                        status_found = f"{key}: {value} (OFFLINE)"
                        offline_drivers.append({
                            'id': driver_id,
                            'name': driver_name,
                            'status_field': key,
                            'status_value': value,
                            'data_type': driver.data_type
                        })
                        break
                    # Também verificar se há campo "status" específico
                    elif 'status' in key_str and value and value != '0':
                        if value_str not in ['view otp', 'none', 'null']:
                            status_found = f"STATUS FIELD: {key}: {value}"
                
                if status_found:
                    print(f"\n🎯 {driver_id} ({driver_name}) - {status_found}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar {driver_id}: {e}")
                continue
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"🟢 MOTORISTAS ONLINE: {len(online_drivers)}")
        for driver in online_drivers:
            print(f"  - {driver['name']} ({driver['id']}) - {driver['status_field']}: {driver['status_value']}")
        
        print(f"\n🔴 MOTORISTAS OFFLINE: {len(offline_drivers)}")
        for driver in offline_drivers:
            print(f"  - {driver['name']} ({driver['id']}) - {driver['status_field']}: {driver['status_value']}")
        
        # Se não encontrou online/offline, vamos procurar padrões diferentes
        if len(online_drivers) == 0 and len(offline_drivers) == 0:
            print(f"\n🔍 NÃO ENCONTROU 'online/offline' explícito. Verificando outros padrões...")
            
            # Vamos ver todos os campos de status únicos
            all_status_fields = set()
            for driver in drivers:
                try:
                    if isinstance(driver.additional_data, dict):
                        data = driver.additional_data
                    else:
                        data = json.loads(driver.additional_data) if driver.additional_data else {}
                    
                    for key, value in data.items():
                        if 'status' in str(key).lower():
                            all_status_fields.add(f"{key}: {value}")
                            
                except:
                    continue
            
            print(f"\n📋 TODOS OS CAMPOS DE STATUS ENCONTRADOS:")
            for field in sorted(all_status_fields):
                print(f"  {field}")

if __name__ == "__main__":
    find_status_column()
