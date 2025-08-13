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

def test_drivers_deduplication():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        print(f'🔍 Total de registros drivers_data: {len(drivers)}')
        
        # Aplicar mesma lógica da API
        drivers_processed = set()
        online_drivers = []
        offline_drivers = []
        
        for driver_record in drivers:
            driver_id = driver_record.driver_id
            
            # DEDUPLICAÇÃO: Pular se ID já foi processado ou é inválido
            if not driver_id or driver_id in drivers_processed or driver_id in ['---', '0', 'Driver']:
                continue
                
            drivers_processed.add(driver_id)
            
            try:
                # Processar additional_data
                driver_data = driver_record.additional_data
                if isinstance(driver_data, str):
                    driver_data = json.loads(driver_data)
                elif not isinstance(driver_data, dict):
                    driver_data = {}
                
                # Determinar status baseado na coluna STATUS real
                driver_status = 'inativo'  # Default
                
                if driver_data:
                    # Procurar na raw_row pelo status "Online" ou "Offline"
                    raw_row = driver_data.get('raw_row', [])
                    if isinstance(raw_row, list):
                        for item in raw_row:
                            if isinstance(item, str):
                                if item.lower() == 'online':
                                    driver_status = 'ativo'
                                    break
                                elif item.lower() == 'offline':
                                    driver_status = 'inativo'
                                    break
                
                # Categorizar motorista
                driver_info = {
                    'id': driver_id,
                    'name': driver_record.name if driver_record.name and driver_record.name not in ['None', '0'] else driver_id,
                    'status': driver_status,
                    'data_type': driver_record.data_type
                }
                
                if driver_status == 'ativo':
                    online_drivers.append(driver_info)
                else:
                    offline_drivers.append(driver_info)
                    
            except Exception as e:
                print(f"❌ Erro ao processar {driver_id}: {e}")
                continue
        
        print(f'\n📊 RESULTADO COM DEDUPLICAÇÃO:')
        print(f'  👥 Total de motoristas únicos: {len(drivers_processed)}')
        print(f'  🟢 Motoristas ONLINE: {len(online_drivers)}')
        print(f'  🔴 Motoristas OFFLINE: {len(offline_drivers)}')
        
        print(f'\n🟢 MOTORISTAS ONLINE:')
        for i, driver in enumerate(online_drivers, 1):
            print(f'  {i}. {driver["name"]} ({driver["id"]}) - {driver["data_type"]}')
        
        print(f'\n🔴 MOTORISTAS OFFLINE (primeiros 10):')
        for i, driver in enumerate(offline_drivers[:10], 1):
            print(f'  {i}. {driver["name"]} ({driver["id"]}) - {driver["data_type"]}')
        
        if len(offline_drivers) > 10:
            print(f'  ... e mais {len(offline_drivers) - 10} motoristas offline')

if __name__ == "__main__":
    test_drivers_deduplication()
