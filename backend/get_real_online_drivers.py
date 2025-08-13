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

def get_real_online_drivers():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        
        unique_drivers = {}
        
        # Primeiro, obter drivers únicos mais recentes
        for driver in drivers:
            if not driver.driver_id or driver.driver_id in ['---', '0', 'Driver']:
                continue
                
            if driver.driver_id not in unique_drivers:
                unique_drivers[driver.driver_id] = driver
            elif hasattr(driver, 'scraped_at') and hasattr(unique_drivers[driver.driver_id], 'scraped_at'):
                if driver.scraped_at > unique_drivers[driver.driver_id].scraped_at:
                    unique_drivers[driver.driver_id] = driver
        
        print(f'🔍 ANALISANDO MOTORISTAS ONLINE REAIS:\n')
        
        online_drivers = []
        offline_drivers = []
        
        for driver_id, driver in unique_drivers.items():
            try:
                # Extrair additional_data
                driver_data = driver.additional_data
                if isinstance(driver_data, dict):
                    additional_data = driver_data
                elif isinstance(driver_data, str):
                    additional_data = json.loads(driver_data)
                else:
                    additional_data = {}
                
                # Determinar se está online baseado no status
                is_online = False
                status_reason = ""
                
                # 1. Verificar campo status nos dados ativos
                if driver.data_type == 'active' and additional_data and 'status' in additional_data:
                    status = additional_data['status']
                    
                    # Status online: números > 0 (ratings) ou indicadores específicos
                    try:
                        # Se for numérico e > 0
                        status_num = float(status)
                        if status_num > 0:
                            is_online = True
                            status_reason = f"Status Rating: {status}"
                    except:
                        # Se não for numérico, verificar strings específicas
                        if str(status).lower() in ['online', 'ativo', 'active']:
                            is_online = True
                            status_reason = f"Status String: {status}"
                        elif str(status) == "View OTP":
                            is_online = False
                            status_reason = f"Aguardando OTP: {status}"
                        elif str(status) == "0":
                            is_online = False
                            status_reason = f"Status Offline: {status}"
                        else:
                            # Status com outros valores (emails, etc) - considerar offline
                            is_online = False
                            status_reason = f"Status Inválido: {status}"
                
                # 2. Verificar outros campos que indicam atividade online
                if additional_data:
                    for key, value in additional_data.items():
                        if 'online' in str(value).lower():
                            is_online = True
                            status_reason += f" + {key}:Online"
                
                # 3. Motoristas do leaderboard são considerados ativos
                if driver.data_type == 'leaderboard':
                    is_online = True
                    status_reason = "Leaderboard (Ativo)"
                
                # Informações do motorista
                name = driver.name if driver.name and driver.name not in ['None', '0'] else driver_id
                phone = driver.email if hasattr(driver, 'email') else 'N/A'
                vehicle = driver.mobile if hasattr(driver, 'mobile') else 'N/A'
                
                driver_info = {
                    'id': driver_id,
                    'name': name,
                    'phone': phone,
                    'vehicle': vehicle,
                    'data_type': driver.data_type,
                    'status_reason': status_reason,
                    'scraped_at': driver.scraped_at
                }
                
                if is_online:
                    online_drivers.append(driver_info)
                else:
                    offline_drivers.append(driver_info)
                    
            except Exception as e:
                print(f'❌ Erro ao processar {driver_id}: {e}')
                offline_drivers.append({
                    'id': driver_id,
                    'name': 'Erro',
                    'status_reason': f'Erro: {e}'
                })
        
        print(f'🟢 MOTORISTAS ONLINE ({len(online_drivers)}):')
        for i, driver in enumerate(online_drivers, 1):
            print(f'  {i}. {driver["name"]} ({driver["id"]})')
            print(f'     📞 {driver["phone"]}')
            print(f'     🚙 {driver["vehicle"]}')
            print(f'     ✅ {driver["status_reason"]}')
            print()
        
        print(f'🔴 MOTORISTAS OFFLINE ({len(offline_drivers)}):')
        for i, driver in enumerate(offline_drivers, 1):
            print(f'  {i}. {driver["name"]} ({driver["id"]})')
            print(f'     ❌ {driver["status_reason"]}')
        
        print(f'\n📊 RESUMO FINAL:')
        print(f'  🟢 MOTORISTAS ONLINE: {len(online_drivers)}')
        print(f'  🔴 MOTORISTAS OFFLINE: {len(offline_drivers)}')
        print(f'  📝 TOTAL: {len(unique_drivers)}')

if __name__ == "__main__":
    get_real_online_drivers()
