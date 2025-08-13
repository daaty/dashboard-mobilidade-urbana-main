#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.drivers_data import DriversData
import json
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

def analyze_driver_status_field():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        print(f'🔍 Total de registros drivers_data: {len(drivers)}')
        
        print(f'\n🔍 ANALISANDO CAMPO additional_data PARA ENCONTRAR STATUS:')
        
        unique_drivers = {}
        status_found = []
        
        for driver in drivers:
            if not driver.driver_id or driver.driver_id in ['---', '0', 'Driver']:
                continue
                
            try:
                # Analisar additional_data
                driver_data = driver.additional_data
                
                # Se for dict direto
                if isinstance(driver_data, dict):
                    additional_data = driver_data
                # Se for string JSON
                elif isinstance(driver_data, str):
                    additional_data = json.loads(driver_data)
                else:
                    additional_data = {}
                
                print(f'\n📋 Driver: {driver.driver_id}')
                print(f'  📊 Data Type: {driver.data_type}')
                print(f'  📝 Name: {driver.name}')
                
                if additional_data:
                    print(f'  🔑 Additional Data Keys: {list(additional_data.keys())}')
                    
                    # Procurar campos relacionados a status
                    for key, value in additional_data.items():
                        if 'status' in key.lower() or 'online' in key.lower() or 'active' in key.lower():
                            print(f'    🎯 {key}: {value}')
                            status_found.append((driver.driver_id, key, value))
                else:
                    print(f'  ❌ Additional Data: Vazio ou inválido')
                
                # Manter registro mais recente
                if driver.driver_id not in unique_drivers:
                    unique_drivers[driver.driver_id] = driver
                elif hasattr(driver, 'scraped_at') and hasattr(unique_drivers[driver.driver_id], 'scraped_at'):
                    if driver.scraped_at > unique_drivers[driver.driver_id].scraped_at:
                        unique_drivers[driver.driver_id] = driver
                        
            except Exception as e:
                print(f'  ❌ Erro ao processar {driver.driver_id}: {e}')
        
        print(f'\n🎯 CAMPOS DE STATUS ENCONTRADOS:')
        if status_found:
            for driver_id, field, value in status_found:
                print(f'  {driver_id} -> {field}: {value}')
        else:
            print('  ❌ Nenhum campo de status específico encontrado')
        
        print(f'\n🔍 VERIFICANDO PADRÕES NOS DADOS:')
        
        # Verificar se há padrões nos nomes/dados que indicam status
        online_count = 0
        offline_count = 0
        
        for driver_id, driver in unique_drivers.items():
            try:
                driver_data = driver.additional_data
                if isinstance(driver_data, dict):
                    additional_data = driver_data
                elif isinstance(driver_data, str):
                    additional_data = json.loads(driver_data)
                else:
                    additional_data = {}
                
                # Verificar diferentes formas de determinar status online
                is_online = False
                status_info = ""
                
                # 1. Verificar se data_type indica atividade
                if driver.data_type == 'active':
                    is_online = True
                    status_info = f"active type"
                
                # 2. Verificar se tem dados recentes (scraped hoje)
                if hasattr(driver, 'scraped_at'):
                    from datetime import datetime, timedelta
                    if driver.scraped_at > datetime.now() - timedelta(hours=2):
                        is_online = True
                        status_info += f" + recent data"
                
                # 3. Verificar se tem informações completas (nome, veículo, etc)
                has_complete_info = (
                    driver.name and driver.name not in ['None', '0', 'null'] and
                    driver.mobile and driver.mobile != 'None'
                )
                
                if has_complete_info:
                    status_info += " + complete info"
                
                # 4. Verificar additional_data para indicadores de status
                if additional_data:
                    # Procurar por campos que possam indicar status online
                    for key, value in additional_data.items():
                        if isinstance(value, str):
                            if 'online' in str(value).lower() or 'ativo' in str(value).lower():
                                is_online = True
                                status_info += f" + {key}:{value}"
                
                if is_online:
                    online_count += 1
                    print(f'  🟢 ONLINE: {driver_id} ({status_info})')
                else:
                    offline_count += 1
                    
            except Exception as e:
                print(f'  ❌ Erro ao analisar {driver_id}: {e}')
                offline_count += 1
        
        print(f'\n📊 RESULTADO FINAL:')
        print(f'  🟢 Motoristas ONLINE: {online_count}')
        print(f'  🔴 Motoristas OFFLINE: {offline_count}')
        print(f'  📝 Total únicos: {len(unique_drivers)}')

if __name__ == "__main__":
    analyze_driver_status_field()
