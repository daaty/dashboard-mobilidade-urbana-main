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

def analyze_raw_driver_data():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        print(f'🔍 Analisando {len(drivers)} registros de motoristas...\n')
        
        # Foco em motoristas com data_type = 'active' para ver a estrutura real
        active_drivers = [d for d in drivers if d.data_type == 'active']
        print(f'📊 Motoristas com data_type="active": {len(active_drivers)}\n')
        
        print('🔍 ESTRUTURA DOS DADOS BRUTOS (primeiros 10 registros active):')
        print('=' * 80)
        
        for i, driver in enumerate(active_drivers[:10], 1):
            print(f'\n📋 REGISTRO {i}:')
            print(f'  🆔 ID: {driver.id}')
            print(f'  🚗 Driver ID: {driver.driver_id}')
            print(f'  👤 Name: {driver.name}')
            print(f'  📧 Email: {driver.email}')
            print(f'  📱 Mobile: {driver.mobile}')
            print(f'  🏷️ Data Type: {driver.data_type}')
            print(f'  📅 Scraped At: {driver.scraped_at}')
            
            # Mostrar dados brutos do additional_data
            print(f'  📊 Additional Data (raw):')
            if driver.additional_data:
                try:
                    if isinstance(driver.additional_data, dict):
                        print(f'    Type: dict')
                        for key, value in driver.additional_data.items():
                            print(f'    {key}: {value}')
                    elif isinstance(driver.additional_data, str):
                        print(f'    Type: string')
                        data = json.loads(driver.additional_data)
                        for key, value in data.items():
                            print(f'    {key}: {value}')
                    else:
                        print(f'    Type: {type(driver.additional_data)}')
                        print(f'    Value: {driver.additional_data}')
                except Exception as e:
                    print(f'    ❌ Erro: {e}')
                    print(f'    Raw value: {driver.additional_data}')
            else:
                print(f'    ❌ Vazio')
            
            print('-' * 50)
        
        # Agora vamos ver se há algum padrão específico
        print(f'\n🔍 PROCURANDO PADRÕES DE STATUS:')
        print('=' * 50)
        
        status_patterns = {}
        online_indicators = []
        
        for driver in drivers:
            if driver.additional_data:
                try:
                    data = driver.additional_data
                    if isinstance(data, str):
                        data = json.loads(data)
                    
                    if isinstance(data, dict):
                        # Procurar por campos que possam indicar status online
                        for key, value in data.items():
                            key_lower = str(key).lower()
                            value_str = str(value).lower()
                            
                            if 'status' in key_lower or 'online' in key_lower or 'active' in key_lower:
                                pattern = f"{key}: {value}"
                                if pattern not in status_patterns:
                                    status_patterns[pattern] = 0
                                status_patterns[pattern] += 1
                                
                                if 'online' in value_str or 'ativo' in value_str or value == 1 or value == '1':
                                    online_indicators.append({
                                        'driver_id': driver.driver_id,
                                        'name': driver.name,
                                        'key': key,
                                        'value': value
                                    })
                except:
                    pass
        
        print(f'📈 PADRÕES DE STATUS ENCONTRADOS:')
        for pattern, count in sorted(status_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f'  {pattern} -> {count} ocorrências')
        
        print(f'\n🟢 POSSÍVEIS MOTORISTAS ONLINE:')
        for indicator in online_indicators:
            print(f'  {indicator["driver_id"]} ({indicator["name"]}) -> {indicator["key"]}: {indicator["value"]}')
        
        print(f'\n📊 RESUMO:')
        print(f'  Total de registros: {len(drivers)}')
        print(f'  Registros "active": {len(active_drivers)}')
        print(f'  Padrões de status: {len(status_patterns)}')
        print(f'  Possíveis online: {len(online_indicators)}')

if __name__ == "__main__":
    analyze_raw_driver_data()
